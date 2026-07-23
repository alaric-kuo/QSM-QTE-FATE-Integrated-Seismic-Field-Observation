#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QSM-QTE-FATE Integrated Seismic Field Observation
NEES-2011-1076 Three-Stage Complete Observation Release V12.2

Public method chain
-------------------
QSM -> QTE -> FATE

V12.2 executes and reports exactly three sequential methods:

1. QSM: zero-diagonal input-driven power-state evolution.
2. QTE: Laplacian spatial topology-path evolution.
3. FATE: sensor-aware evolution at the Aware_power layer.

Only these three sequential methods are generated. Independent physical observation outputs are retained under the relevant stage.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import multiprocessing
import os
import time
from datetime import datetime, timezone
import csv
import json
import math
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

for _thread_env in (
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_thread_env, "1")
os.environ.setdefault("MPLBACKEND", "Agg")

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


FLOORS = ["First", "Second", "Third"]


FLOOR_SHORT = {"First": "1F", "Second": "2F", "Third": "3F"}


FLOOR_NO = {"First": 1, "Second": 2, "Third": 3}


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    display_name: str
    event_name: str
    input_scale: str
    control_mode: str
    acquisition_context: str
    filename: str
    aliases: Tuple[str, ...] = ()


CASE_SPECS: Tuple[CaseSpec, ...] = (
    CaseSpec(
        case_id="el_centro_050_uncontrolled",
        display_name="El Centro 0.50 — uncontrolled",
        event_name="El Centro",
        input_scale="0.50",
        control_mode="uncontrolled",
        acquisition_context="Dong-Hua shake-table record",
        filename="elcentro_0p50_07312012_unc_donghua_converted.csv",
        aliases=("*elcentro*0p50*unc*donghua*converted.csv",),
    ),
    CaseSpec(
        case_id="el_centro_050_passive_off",
        display_name="El Centro 0.50 — passive-off",
        event_name="El Centro",
        input_scale="0.50",
        control_mode="passive-off",
        acquisition_context="Dong-Hua shake-table record",
        filename="elcentro_0p50_07312012_poff_donghua_converted.csv",
        aliases=("*elcentro*0p50*poff*donghua*converted.csv",),
    ),
    CaseSpec(
        case_id="kobe_035_semi_active",
        display_name="Kobe 0.35 — semi-active",
        event_name="Kobe",
        input_scale="0.35",
        control_mode="semi-active",
        acquisition_context="averaged converted record",
        filename="kobe_035_semi_active_avg_converted.csv",
        aliases=("*kobe*035*semi*active*avg*converted.csv",),
    ),
    CaseSpec(
        case_id="morgan_hill_100_passive_off",
        display_name="Morgan Hill 1.00 — passive-off",
        event_name="Morgan Hill",
        input_scale="1.00 (encoded as morgan_1)",
        control_mode="passive-off",
        acquisition_context="averaged converted record",
        filename="morgan_1_p_off_avg_converted.csv",
        aliases=("*morgan*1*p*off*avg*converted.csv",),
    ),
)


def robust_scale(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    med = np.nanmedian(x)
    scale = np.nanpercentile(np.abs(x - med), 95)
    if not np.isfinite(scale) or scale < eps:
        scale = np.nanstd(x)
    if not np.isfinite(scale) or scale < eps:
        scale = 1.0
    return (x - med) / (scale + eps)


def normalize_by_max(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    m = np.nanmax(np.abs(x))
    if not np.isfinite(m) or m < eps:
        return np.zeros_like(x, dtype=float)
    return x / (m + eps)


def normalize_complex(z: np.ndarray, eps: float = 1e-15) -> np.ndarray:
    z = np.asarray(z, dtype=complex)
    n = np.linalg.norm(z)
    if not np.isfinite(n) or n < eps:
        return np.ones_like(z, dtype=complex) / math.sqrt(len(z))
    return z / n


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if np.nanstd(x) < 1e-15 or np.nanstd(y) < 1e-15:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def dominant_omega(t: np.ndarray, x: np.ndarray, fmin: float = 0.1, fmax: float = 30.0) -> float:
    t = np.asarray(t, dtype=float)
    x = np.asarray(x, dtype=float)
    if len(t) < 8:
        return 2.0 * np.pi
    dt = float(np.nanmedian(np.diff(t)))
    if not np.isfinite(dt) or dt <= 0:
        return 2.0 * np.pi
    y = x - np.nanmean(x)
    if np.nanstd(y) < 1e-15:
        return 2.0 * np.pi
    win = np.hanning(len(y))
    spec = np.abs(np.fft.rfft(y * win))
    freqs = np.fft.rfftfreq(len(y), dt)
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(mask):
        return 2.0 * np.pi
    idx = np.nanargmax(spec[mask])
    return float(2.0 * np.pi * freqs[mask][idx])


def causal_envelope_abs(x: np.ndarray, t: np.ndarray, tau: float = 0.6) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    t = np.asarray(t, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    n, m = x.shape
    dt = float(np.nanmedian(np.diff(t))) if len(t) > 1 else 0.005
    if not np.isfinite(dt) or dt <= 0:
        dt = 0.005
    decay = math.exp(-dt / max(tau, 1e-9))
    env = np.zeros_like(x, dtype=float)
    x_scaled = np.column_stack([robust_scale(x[:, i]) for i in range(m)])
    abs_x = np.abs(x_scaled)
    env[0] = abs_x[0]
    for k in range(1, n):
        env[k] = np.maximum(abs_x[k], decay * env[k - 1])
    return env


def path_manifestation_label(w12: float, w23: float, tol: float = 0.02) -> str:
    """Return a cautious floor-domain path indication from final dominance.

    The threshold is applied to the normalized dominance index rather than to
    the raw path-weight difference. Values close to zero are reported as
    near-equal instead of being assigned to an interface by sign alone.
    """
    dominance = (float(w12) - float(w23)) / (float(w12) + float(w23) + 1e-12)
    if abs(dominance) <= tol:
        return "near-equal / no clear final path indication"
    return (
        "1F-2F lower-interface indication"
        if dominance > 0
        else "2F-3F upper-interface indication"
    )


def compute_work_capacity_scale(result: Dict, safety_factor: float = 1.05) -> float:
    """Case-level scaling from QSM hit-work index to work-compatible capacity index.

    Without known mass/stiffness, QSM evolved a*v / hit-work and displacement-side work are proxy indices,
    not physical Joules. This scale makes the comparison physically readable:
    available hit-work capacity should exceed displacement-side work proxy.
    """
    w_hit_final = np.maximum(result["w_hit"][-1], 1e-12)
    disp_side_work_final = np.maximum(result["measured_abs_work"][-1], 0.0)
    raw_ratio = disp_side_work_final / w_hit_final
    scale = float(np.nanmax(raw_ratio) * safety_factor)
    if not np.isfinite(scale) or scale <= 0:
        scale = 1.0
    return scale


def _deduplicate_names(names: Sequence[str]) -> List[str]:
    seen: Dict[str, int] = {}
    out: List[str] = []
    for i, raw in enumerate(names):
        name = str(raw).strip() or f"unnamed_{i}"
        count = seen.get(name, 0)
        seen[name] = count + 1
        out.append(name if count == 0 else f"{name}__{count+1}")
    return out


def _numeric_fraction(row: Sequence[str]) -> float:
    if not row:
        return 0.0
    numeric = 0
    nonempty = 0
    for cell in row:
        s = str(cell).strip()
        if not s:
            continue
        nonempty += 1
        try:
            float(s)
            numeric += 1
        except ValueError:
            pass
    return numeric / max(nonempty, 1)


def inspect_nees_header(path: str | Path, max_rows: int = 80) -> Tuple[List[str], int]:
    """Locate the sensor-name row and first numeric data row.

    The legacy NEES exports usually place sensor names near row 7 and data near
    row 13. This detector keeps that convention as a fallback while allowing
    small metadata differences among the four source files.
    """
    path = Path(path)
    rows: List[List[str]] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for _ in range(max_rows):
            try:
                rows.append(next(reader))
            except StopIteration:
                break

    if not rows:
        raise ValueError(f"CSV is empty: {path}")

    header_idx: Optional[int] = None
    for i, row in enumerate(rows):
        joined = " ".join(str(x) for x in row).lower()
        has_time = any(str(x).strip().lower() == "time" for x in row)
        floor_hits = sum(token in joined for token in ("first floor", "second floor", "third floor"))
        if has_time and floor_hits >= 1:
            header_idx = i
            break

    if header_idx is None:
        header_idx = 6 if len(rows) > 6 else 0

    data_start: Optional[int] = None
    expected_width = max(len(rows[header_idx]), 1)
    for i in range(header_idx + 1, len(rows)):
        # Legacy exports include a short "Sensor_Time, 0" metadata row.
        # Require a near-full-width numeric row so that row is not mistaken
        # for the first sample.
        if (
            len(rows[i]) >= max(3, int(0.75 * expected_width))
            and _numeric_fraction(rows[i]) >= 0.45
        ):
            data_start = i
            break
    if data_start is None:
        data_start = 12 if len(rows) > 12 else header_idx + 1

    names = _deduplicate_names(rows[header_idx])
    return names, data_start


def _signal_score(column: str, floor: str, signal_kind: str) -> int:
    c = re.sub(r"\s+", " ", column.lower().replace("_", " "))
    if floor.lower() not in c or "floor" not in c:
        return -10_000

    required = {
        "displacement": ("displacement",),
        "velocity": ("velocity",),
        "acceleration": ("acceleration",),
    }[signal_kind]
    if not all(token in c for token in required):
        return -10_000

    excluded = ("table", "ground", "damper", "command", "target", "reference", "voltage", "force")
    if any(token in c for token in excluded):
        return -10_000

    score = 0
    if "analytical" in c:
        score += 8
    if "experimental" in c or "measured" in c:
        score += 6
    if "sensor" in c:
        score += 2
    if signal_kind == "velocity" and "velocity sensor" in c:
        score += 2
    if c.startswith(f"{floor.lower()} floor"):
        score += 3
    return score


def _find_signal_column(columns: Iterable[str], floor: str, signal_kind: str) -> Optional[str]:
    ranked = sorted(
        ((_signal_score(str(c), floor, signal_kind), str(c)) for c in columns),
        reverse=True,
    )
    return ranked[0][1] if ranked and ranked[0][0] > -10_000 else None


def _integrate_trapezoid(y: np.ndarray, t: np.ndarray) -> np.ndarray:
    out = np.zeros_like(y, dtype=float)
    if len(y) > 1:
        out[1:] = np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(t))
    return out


def _remove_linear_trend(y: np.ndarray, t: np.ndarray) -> np.ndarray:
    if len(y) < 3:
        return y - np.nanmean(y)
    coeff = np.polyfit(t, y, 1)
    return y - np.polyval(coeff, t)


def extract_floor_arrays(
    df: pd.DataFrame,
    allow_acceleration_reconstruction: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Dict[str, str]]]:
    """Extract 1F/2F/3F u, v, a arrays and document every selected source.

    Preferred order:
      1. directly exported displacement, velocity, acceleration;
      2. velocity from measured displacement derivative;
      3. displacement from measured velocity integration;
      4. acceleration from measured velocity derivative.

    Double integration from acceleration is disabled unless explicitly requested,
    because it changes the evidentiary status of a*v.
    """
    t = df["Time"].to_numpy(dtype=float)
    if not np.all(np.diff(t) > 0):
        raise ValueError("Time values must be strictly increasing after cleanup")

    arrays: Dict[str, List[np.ndarray]] = {"u": [], "v": [], "a": []}
    signal_map: Dict[str, Dict[str, str]] = {}

    for floor in FLOORS:
        cols = {
            "u": _find_signal_column(df.columns, floor, "displacement"),
            "v": _find_signal_column(df.columns, floor, "velocity"),
            "a": _find_signal_column(df.columns, floor, "acceleration"),
        }
        values: Dict[str, Optional[np.ndarray]] = {
            key: (df[col].to_numpy(dtype=float) if col is not None else None)
            for key, col in cols.items()
        }
        provenance: Dict[str, str] = {
            key: (f"direct:{col}" if col is not None else "missing")
            for key, col in cols.items()
        }

        if values["v"] is None and values["u"] is not None:
            values["v"] = np.gradient(values["u"], t)
            provenance["v"] = "derived:d(displacement)/dt"
        if values["u"] is None and values["v"] is not None:
            values["u"] = _integrate_trapezoid(values["v"], t)
            provenance["u"] = "derived:integral(velocity)dt"
        if values["a"] is None and values["v"] is not None:
            values["a"] = np.gradient(values["v"], t)
            provenance["a"] = "derived:d(velocity)/dt"

        if (values["u"] is None or values["v"] is None) and values["a"] is not None:
            if not allow_acceleration_reconstruction:
                raise KeyError(
                    f"{FLOOR_SHORT[floor]} lacks displacement/velocity columns. "
                    "Use --allow-acceleration-reconstruction only if reconstructed "
                    "velocity/displacement are acceptable for this case."
                )
            a0 = _remove_linear_trend(values["a"], t)
            v0 = _remove_linear_trend(_integrate_trapezoid(a0, t), t)
            u0 = _remove_linear_trend(_integrate_trapezoid(v0, t), t)
            if values["v"] is None:
                values["v"] = v0
                provenance["v"] = "reconstructed:baseline-corrected integral(acceleration)dt"
            if values["u"] is None:
                values["u"] = u0
                provenance["u"] = "reconstructed:baseline-corrected double integral(acceleration)"

        missing = [key for key, val in values.items() if val is None]
        if missing:
            raise KeyError(f"Missing {missing} for {FLOOR_SHORT[floor]}")

        for key in ("u", "v", "a"):
            arr = np.asarray(values[key], dtype=float)
            if np.isnan(arr).any():
                arr = pd.Series(arr).interpolate(limit_direction="both").to_numpy(dtype=float)
            arrays[key].append(arr)
        signal_map[FLOOR_SHORT[floor]] = provenance

    u = np.column_stack(arrays["u"])
    v = np.column_stack(arrays["v"])
    a = np.column_stack(arrays["a"])
    return t, u, v, a, signal_map


def detect_event_window(t: np.ndarray, a: np.ndarray, lower: float = 0.01, upper: float = 0.99) -> Tuple[float, float]:
    """Choose a figure window from cumulative acceleration-state activity."""
    scaled = np.column_stack([robust_scale(a[:, i]) for i in range(a.shape[1])])
    activity = np.sum(scaled**2, axis=1)
    activity = np.nan_to_num(activity, nan=0.0, posinf=0.0, neginf=0.0)
    total = float(np.sum(activity))
    if total <= 0:
        return float(t[0]), float(t[-1])
    cumulative = np.cumsum(activity) / total
    i0 = int(np.searchsorted(cumulative, lower))
    i1 = int(np.searchsorted(cumulative, upper))
    i0 = max(0, min(i0, len(t) - 1))
    i1 = max(i0 + 1, min(i1, len(t) - 1))
    pad = 0.05 * max(float(t[i1] - t[i0]), 1e-9)
    return max(float(t[0]), float(t[i0] - pad)), min(float(t[-1]), float(t[i1] + pad))


def resolve_case_file(root: Path, spec: CaseSpec) -> Optional[Path]:
    exact = root / spec.filename
    if exact.exists():
        return exact
    for pattern in spec.aliases:
        matches = sorted(root.glob(pattern))
        if matches:
            return matches[0]
    return None


def build_empirical_wavefunction(t: np.ndarray, u: np.ndarray, v: np.ndarray, a: np.ndarray):
    n_floor = u.shape[1]
    omega = np.array([dominant_omega(t, u[:, i]) for i in range(n_floor)])
    omega_ref = np.nanmedian(omega)
    if not np.isfinite(omega_ref) or omega_ref <= 0:
        omega_ref = 2.0 * np.pi
    omega_norm = omega / omega_ref

    u_norm = np.column_stack([robust_scale(u[:, i]) for i in range(n_floor)])
    v_norm = np.column_stack([robust_scale(v[:, i]) for i in range(n_floor)])
    a_norm = np.column_stack([robust_scale(a[:, i]) for i in range(n_floor)])

    energy = v_norm**2 + (omega_norm.reshape(1, -1) * u_norm) ** 2 + 0.25 * a_norm**2 + 1e-12
    amp = np.sqrt(energy / np.sum(energy, axis=1, keepdims=True))
    phase = np.arctan2(omega_norm.reshape(1, -1) * u_norm, v_norm)
    psi = amp * np.exp(1j * phase)
    psi = np.array([normalize_complex(row) for row in psi])
    return psi, amp, phase, omega


def build_path_operator(w12: float, w23: float, operator_key: str):
    W = np.array(
        [
            [0.0, w12, 0.0],
            [w12, 0.0, w23],
            [0.0, w23, 0.0],
        ],
        dtype=float,
    )
    D = np.diag(W.sum(axis=1))
    L = D - W
    if operator_key == "laplacian":
        H = L
    elif operator_key == "zero_diagonal":
        H = -W
    else:
        raise ValueError("operator_key must be laplacian or zero_diagonal")
    return W, L, H


_UNITARY_CACHE: Dict[Tuple[str, float, float, float], Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}


def build_path_operator_and_unitary(w12: float, w23: float, operator_key: str, dt: float):
    """Build H and U with a small cache for fast release runs.

    The path weights evolve smoothly, so rounding the cache key is a practical
    numerical release choice. It keeps the evidence stable while avoiding tens of
    thousands of repeated 3x3 matrix exponentials.
    """
    key = (operator_key, round(float(w12), 5), round(float(w23), 5), round(float(dt), 8))
    cached = _UNITARY_CACHE.get(key)
    if cached is not None:
        return cached
    W, L, H = build_path_operator(key[1], key[2], operator_key)
    # H is real symmetric for both methods, so eigen evolution is exact and faster
    # than calling scipy.linalg.expm repeatedly.
    evals, evecs = np.linalg.eigh(H)
    U = (evecs * np.exp(-1j * evals * dt)) @ evecs.conj().T
    _UNITARY_CACHE[key] = (W, L, H, U)
    return W, L, H, U


def edge_currents(psi: np.ndarray, H: np.ndarray):
    j12 = 2.0 * np.imag(np.conj(psi[0]) * H[0, 1] * psi[1])
    j23 = 2.0 * np.imag(np.conj(psi[1]) * H[1, 2] * psi[2])
    return float(j12), float(j23)


def normalize_path(w12: float, w23: float, total: float = 2.0, eps: float = 1e-9):
    w12 = max(float(w12), eps)
    w23 = max(float(w23), eps)
    s = w12 + w23
    return total * w12 / s, total * w23 / s


def summarize_method(result: Dict) -> Tuple[dict, pd.DataFrame]:
    t = result["t"]
    p_av = result["p_av"]
    p_hit = result["p_hit"]
    signed_p_hit = result["signed_p_hit"]
    evolved_av_next = result["evolved_av_next"]
    evolved_av_next_residual = result["evolved_av_next_residual"]
    w_hit = result["w_hit"]
    measured_abs_work = result["measured_abs_work"]
    measured_signed_work = result["measured_signed_work"]
    disp_env = result["disp_env"]
    hidden = result["hidden_work_proxy"]

    work_capacity_scale = compute_work_capacity_scale(result)

    final_w12 = float(result["w12_hist"][-1])
    final_w23 = float(result["w23_hist"][-1])
    j12 = float(np.sqrt(np.nanmean(result["j12_hist"] ** 2)))
    j23 = float(np.sqrt(np.nanmean(result["j23_hist"] ** 2)))

    rows = []
    for i, fl in enumerate(FLOORS):
        peak_p = int(np.nanargmax(p_hit[:, i]))
        peak_av = int(np.nanargmax(np.abs(p_av[:, i])))
        peak_d = int(np.nanargmax(disp_env[:, i]))
        hit_work_capacity_final = float(work_capacity_scale * w_hit[-1, i])
        displacement_side_work_final = float(measured_abs_work[-1, i])
        manifested_work_ratio = displacement_side_work_final / (hit_work_capacity_final + 1e-12)
        rows.append({
            "method_key": result["method_key"],
            "method_name": result["method_name"],
            "method_stage": result["method_stage"],
            "operator_key": result["operator_key"],
            "operator_name": result["operator_name"],
            "dynamic_path_enabled": result["dynamic_path_enabled"],
            "response_feedback_enabled": result["response_feedback_enabled"],
            "input_mode": result.get("input_mode", "floor_state_assimilated"),
            "boundary_floor": result.get("boundary_floor", "1F"),
            "target_floor_no": FLOOR_NO[fl],
            "target_floor": FLOOR_SHORT[fl],
            "evolved_av_next_vs_measured_av_corr": safe_corr(evolved_av_next[:, i], p_av[:, i]),
            "evolved_abs_av_next_vs_measured_abs_av_corr": safe_corr(np.abs(evolved_av_next[:, i]), np.abs(p_av[:, i])),
            "one_step_av_evolution_residual_rmse": float(np.sqrt(np.nanmean(evolved_av_next_residual[:, i] ** 2))),
            "target_hit_power_alignment_corr": safe_corr(p_hit[:, i], np.abs(p_av[:, i])),
            "signed_hit_power_vs_signed_av_corr": safe_corr(signed_p_hit[:, i], p_av[:, i]),
            "target_hit_power_peak_time_seconds": float(t[peak_p]),
            "measured_abs_a_times_v_peak_time_seconds": float(t[peak_av]),
            "target_hit_power_peak_time_offset_seconds": float(t[peak_p] - t[peak_av]),
            "w_hit_final": float(w_hit[-1, i]),
            "work_capacity_scale": float(work_capacity_scale),
            "hit_work_capacity_final": hit_work_capacity_final,
            "displacement_side_work_final": displacement_side_work_final,
            "manifested_work_ratio": float(manifested_work_ratio),
            "unmanifested_work_margin": float(1.0 - manifested_work_ratio),
            "measured_abs_work_final": float(measured_abs_work[-1, i]),
            "measured_signed_work_final": float(measured_signed_work[-1, i]),
            "max_downstream_response_envelope": float(np.nanmax(disp_env[:, i])),
            "downstream_response_peak_time_seconds": float(t[peak_d]),
            "hidden_work_proxy_mean": float(np.nanmean(hidden[:, i])),
        })

    target_df = pd.DataFrame(rows)

    mode = {
        "method_key": result["method_key"],
        "method_name": result["method_name"],
        "method_stage": result["method_stage"],
        "operator_key": result["operator_key"],
        "operator_name": result["operator_name"],
        "dynamic_path_enabled": result["dynamic_path_enabled"],
        "response_feedback_enabled": result["response_feedback_enabled"],
        "input_mode": result.get("input_mode", "floor_state_assimilated"),
        "boundary_floor": result.get("boundary_floor", "1F"),
        "path_manifestation": path_manifestation_label(final_w12, final_w23),
        "final_w12": final_w12,
        "final_w23": final_w23,
        "final_path_dominance_index": float(result["path_dominance"][-1]),
        "mean_path_dominance_index": float(np.nanmean(result["path_dominance"])),
        "edge_current_rms_1F_2F": j12,
        "edge_current_rms_2F_3F": j23,
        "edge_current_concentration_ratio_1F_2F_over_2F_3F": j12 / (j23 + 1e-12),
        "mean_evolved_av_next_vs_measured_av_corr": float(np.nanmean(target_df["evolved_av_next_vs_measured_av_corr"])),
        "mean_evolved_abs_av_next_vs_measured_abs_av_corr": float(np.nanmean(target_df["evolved_abs_av_next_vs_measured_abs_av_corr"])),
        "mean_one_step_av_evolution_residual_rmse": float(np.nanmean(target_df["one_step_av_evolution_residual_rmse"])),
        "mean_target_hit_power_alignment_corr": float(np.nanmean(target_df["target_hit_power_alignment_corr"])),
        "mean_signed_hit_power_vs_signed_av_corr": float(np.nanmean(target_df["signed_hit_power_vs_signed_av_corr"])),
        "mean_target_hit_peak_time_offset_seconds": float(np.nanmean(np.abs(target_df["target_hit_power_peak_time_offset_seconds"]))),
        "work_capacity_scale": float(work_capacity_scale),
        "mean_manifested_work_ratio": float(np.nanmean(target_df["manifested_work_ratio"])),
        "mean_unmanifested_work_margin": float(np.nanmean(target_df["unmanifested_work_margin"])),
        "max_response_floor": target_df.loc[target_df["max_downstream_response_envelope"].idxmax(), "target_floor"],
    }
    return mode, target_df


def _select_read_columns(names: Sequence[str]) -> List[str]:
    """Select only time and the floor-response columns needed by QSM-QTE-FATE.

    The original legacy exports contain many control and instrumentation channels.
    Reading only the active floor displacement, velocity, and acceleration columns
    reduces CSV parsing time and memory pressure substantially.
    """
    selected: List[str] = []
    time_candidates = [c for c in names if str(c).strip().lower() == "time"]
    if not time_candidates:
        time_candidates = [c for c in names if "time" in str(c).lower()]
    if not time_candidates:
        raise KeyError("No time column found in detected NEES header")
    selected.append(time_candidates[0])

    for floor in FLOORS:
        for signal_kind in ("displacement", "velocity", "acceleration"):
            col = _find_signal_column(names, floor, signal_kind)
            if col is not None and col not in selected:
                selected.append(col)
    return selected


def read_nees_csv(
    path: str | Path,
    stride: int = 5,
    chunk_rows: int = 200_000,
) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """V12.2 high-throughput NEES CSV reader.

    Improvements over V9:
      * uses pandas' C parser rather than a per-row Python ``skiprows`` callback;
      * reads in chunks so the 250-440 MB El Centro files do not need to be
        materialized at full resolution;
      * keeps only the response columns required by the three-floor field model;
      * applies stride vectorially inside each chunk.
    """
    path = Path(path)
    names, data_start = inspect_nees_header(path)
    stride = max(int(stride), 1)
    chunk_rows = max(int(chunk_rows), 10_000)
    usecols = _select_read_columns(names)

    frames: List[pd.DataFrame] = []
    rows_seen = 0
    chunks_read = 0
    reader = pd.read_csv(
        path,
        skiprows=data_start,
        header=None,
        names=names,
        usecols=usecols,
        engine="c",
        chunksize=chunk_rows,
        on_bad_lines="skip",
    )
    for chunk in reader:
        n_chunk = len(chunk)
        if n_chunk == 0:
            continue
        global_index = np.arange(rows_seen, rows_seen + n_chunk, dtype=np.int64)
        keep = (global_index % stride) == 0
        if np.any(keep):
            frames.append(chunk.iloc[np.flatnonzero(keep)])
        rows_seen += n_chunk
        chunks_read += 1

    if not frames:
        raise ValueError(f"No numeric data rows retained from {path.name}")
    df = pd.concat(frames, ignore_index=True)
    del frames

    time_candidates = [c for c in df.columns if str(c).strip().lower() == "time"]
    if not time_candidates:
        time_candidates = [c for c in df.columns if "time" in str(c).lower()]
    if not time_candidates:
        raise KeyError(f"No time column found in {path.name}")
    time_col = time_candidates[0]
    if time_col != "Time":
        df = df.rename(columns={time_col: "Time"})

    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Time"]).sort_values("Time")
    df = df[~df["Time"].duplicated(keep="first")].reset_index(drop=True)
    if len(df) < 8:
        raise ValueError(f"Too few numeric rows after parsing {path.name}: {len(df)}")

    metadata = {
        "source_file": path.name,
        "source_path": str(path),
        "detected_header_row_1_based": data_start if data_start > 0 else 1,
        "data_start_row_1_based": data_start + 1,
        "read_stride": stride,
        "chunk_rows": chunk_rows,
        "chunks_read": chunks_read,
        "source_rows_seen": int(rows_seen),
        "rows_loaded": int(len(df)),
        "columns_loaded": int(len(df.columns)),
        "selected_columns": [str(c) for c in df.columns],
        "parser": "pandas C engine with vectorized chunk stride",
    }
    return df, metadata


def _cumulative_work(p_av: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
    measured_abs_work = np.zeros_like(p_av, dtype=float)
    measured_signed_work = np.zeros_like(p_av, dtype=float)
    if len(p_av) > 1:
        measured_abs_work[1:] = np.cumsum(
            0.5 * (np.abs(p_av[:-1]) + np.abs(p_av[1:])) * dt,
            axis=0,
        )
        measured_signed_work[1:] = np.cumsum(
            0.5 * (p_av[:-1] + p_av[1:]) * dt,
            axis=0,
        )
    return measured_abs_work, measured_signed_work


def prepare_case_features(
    t: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    a: np.ndarray,
    disp_env_tau: float = 0.6,
) -> Dict[str, np.ndarray | float]:
    """Build field-observation arrays once per case, not once per method."""
    dt = float(np.nanmedian(np.diff(t)))
    psi_meas, _amp, phase, _omega = build_empirical_wavefunction(t, u, v, a)
    p_av = a * v
    p_av_norm = np.column_stack([robust_scale(p_av[:, i]) for i in range(3)])
    p_abs_norm = np.column_stack(
        [robust_scale(np.abs(p_av[:, i])) for i in range(3)]
    )
    disp_env = causal_envelope_abs(u, t, tau=disp_env_tau)
    disp_env_norm = np.column_stack(
        [normalize_by_max(disp_env[:, i]) for i in range(3)]
    )
    measured_abs_work, measured_signed_work = _cumulative_work(p_av, dt)
    return {
        "t": np.asarray(t, dtype=float),
        "u": np.asarray(u, dtype=float),
        "v": np.asarray(v, dtype=float),
        "a": np.asarray(a, dtype=float),
        "psi_meas": np.asarray(psi_meas, dtype=complex),
        "phase": np.asarray(phase, dtype=float),
        "p_av": np.asarray(p_av, dtype=float),
        "p_av_norm": np.asarray(p_av_norm, dtype=float),
        "p_abs_norm": np.asarray(p_abs_norm, dtype=float),
        "disp_env": np.asarray(disp_env, dtype=float),
        "disp_env_norm": np.asarray(disp_env_norm, dtype=float),
        "measured_abs_work": np.asarray(measured_abs_work, dtype=float),
        "measured_signed_work": np.asarray(measured_signed_work, dtype=float),
        "dt": dt,
    }


def run_method_prepared(
    prepared: Dict[str, np.ndarray | float],
    method_key: str,
    method_name: str,
    method_stage: str,
    operator_key: str,
    operator_name: str,
    dynamic_path_enabled: bool,
    response_feedback_enabled: bool,
    input_mode: str = "floor_state_assimilated",
    boundary_index: int = 0,
    measurement_gain: float = 0.20,
    source_gain: float = 0.08,
    path_decay: float = 0.02,
    path_current_gain: float = 0.15,
    path_power_gain: float = 0.30,
    path_residual_gain: float = 0.06,
    path_hidden_gain: float = 0.05,
    total_path_weight: float = 2.0,
) -> Dict[str, object]:
    """V12.2 O(n) method engine using precomputed case features.

    The Earlier historical maximum scan was O(n^2). Since cumulative hit-work is
    monotonic, V12.2 keeps a three-value running maximum, preserving the numerical
    meaning while reducing this part of the loop to O(n).
    """
    t = np.asarray(prepared["t"])
    u = np.asarray(prepared["u"])
    v = np.asarray(prepared["v"])
    a = np.asarray(prepared["a"])
    psi_meas = np.asarray(prepared["psi_meas"])
    phase = np.asarray(prepared["phase"])
    p_av = np.asarray(prepared["p_av"])
    p_av_norm = np.asarray(prepared["p_av_norm"])
    p_abs_norm = np.asarray(prepared["p_abs_norm"])
    disp_env = np.asarray(prepared["disp_env"])
    disp_env_norm = np.asarray(prepared["disp_env_norm"])
    measured_abs_work = np.asarray(prepared["measured_abs_work"])
    measured_signed_work = np.asarray(prepared["measured_signed_work"])
    dt = float(prepared["dt"])
    n = len(t)

    boundary_index = int(boundary_index)
    if boundary_index < 0 or boundary_index >= len(FLOORS):
        raise ValueError("boundary_index must be 0, 1, or 2")
    boundary_floor = FLOOR_SHORT[FLOORS[boundary_index]]
    if input_mode not in {"floor_state_assimilated", "boundary_input_only"}:
        raise ValueError(
            "input_mode must be floor_state_assimilated or boundary_input_only"
        )

    if input_mode == "boundary_input_only":
        psi = np.zeros(3, dtype=complex)
        psi[boundary_index] = np.exp(1j * phase[0, boundary_index])
        psi = normalize_complex(psi)
        effective_measurement_gain = 0.0
    else:
        psi = np.array(psi_meas[0], dtype=complex, copy=True)
        effective_measurement_gain = measurement_gain

    w12, w23 = normalize_path(1.0, 1.0, total_path_weight)

    p_hit = np.zeros((n, 3), dtype=float)
    w_hit = np.zeros((n, 3), dtype=float)
    evolved_av_next = np.zeros((n, 3), dtype=float)
    hidden_work_proxy = np.zeros((n, 3), dtype=float)
    w12_hist = np.zeros(n, dtype=float)
    w23_hist = np.zeros(n, dtype=float)
    path_dominance = np.zeros(n, dtype=float)
    j12_hist = np.zeros(n, dtype=float)
    j23_hist = np.zeros(n, dtype=float)
    state_fidelity = np.zeros(n, dtype=float)
    residual_norm = np.zeros(n, dtype=float)

    w12_hist[0] = w12
    w23_hist[0] = w23
    state_fidelity[0] = 1.0
    running_w_max = np.full(3, 1e-12, dtype=float)

    for k in range(n - 1):
        _, _, H, U = build_path_operator_and_unitary(
            w12, w23, operator_key, dt
        )
        j12, j23 = edge_currents(psi, H)
        j12_hist[k] = j12
        j23_hist[k] = j23

        if input_mode == "boundary_input_only":
            sign_boundary = np.sign(p_av_norm[k, boundary_index])
            if sign_boundary == 0:
                sign_boundary = 1.0
            source_phase = np.zeros(3, dtype=float)
            source_amp = np.zeros(3, dtype=float)
            source_phase[boundary_index] = (
                phase[k, boundary_index] + (sign_boundary < 0) * np.pi
            )
            source_amp[boundary_index] = np.sqrt(
                abs(p_av_norm[k, boundary_index]) + 1e-12
            )
            source = source_amp * np.exp(1j * source_phase)
        else:
            sign = np.sign(p_av_norm[k])
            sign[sign == 0] = 1.0
            source_phase = phase[k] + (sign < 0) * np.pi
            source_amp = np.sqrt(np.abs(p_av_norm[k]) + 1e-12)
            source = source_amp * np.exp(1j * source_phase)

        psi_prior = normalize_complex(U @ (psi + source_gain * dt * source))
        state_fidelity[k + 1] = abs(
            np.vdot(psi_meas[k + 1], psi_prior)
        ) ** 2
        fid = np.abs(psi_prior) ** 2

        if input_mode == "boundary_input_only":
            p_total = float(np.abs(p_av[k, boundary_index]))
        else:
            p_total = float(np.sum(np.abs(p_av[k])))

        evolved_phase = np.angle(psi_prior)
        evolved_sign = np.sign(-np.sin(2.0 * evolved_phase))
        current_sign = np.sign(p_av[k])
        current_sign[current_sign == 0] = 1.0
        evolved_sign[evolved_sign == 0] = current_sign[evolved_sign == 0]

        evolved_av_next[k + 1] = p_total * fid * evolved_sign
        p_hit[k + 1] = np.abs(evolved_av_next[k + 1])
        w_hit[k + 1] = (
            w_hit[k] + 0.5 * (p_hit[k] + p_hit[k + 1]) * dt
        )

        running_w_max = np.maximum(running_w_max, w_hit[k + 1])
        w_hit_norm_now = w_hit[k + 1] / running_w_max
        hidden_now = w_hit_norm_now - disp_env_norm[k + 1]
        hidden_work_proxy[k + 1] = hidden_now

        residual_full = psi_meas[k + 1] - psi_prior
        if input_mode == "boundary_input_only":
            residual = np.zeros_like(residual_full)
            residual[boundary_index] = residual_full[boundary_index]
        else:
            residual = residual_full
        residual_norm[k + 1] = float(np.linalg.norm(residual_full))
        psi = normalize_complex(
            psi_prior + effective_measurement_gain * residual
        )

        if dynamic_path_enabled:
            if input_mode == "boundary_input_only":
                dP12 = abs(fid[1] - fid[0])
                dP23 = abs(fid[2] - fid[1])
                r12 = r23 = 0.0
                h12 = h23 = 0.0
            else:
                dP12 = abs(p_abs_norm[k, 1] - p_abs_norm[k, 0])
                dP23 = abs(p_abs_norm[k, 2] - p_abs_norm[k, 1])
                r12 = abs(residual[1] - residual[0])
                r23 = abs(residual[2] - residual[1])
                if response_feedback_enabled:
                    h12 = abs(hidden_now[1] - hidden_now[0])
                    h23 = abs(hidden_now[2] - hidden_now[1])
                else:
                    h12 = h23 = 0.0

            w12_new = (1.0 - path_decay * dt) * w12
            w23_new = (1.0 - path_decay * dt) * w23
            w12_new += (
                path_current_gain * abs(j12) * dt
                + path_power_gain * dP12 * dt
                + path_residual_gain * r12 * dt
                + path_hidden_gain * h12 * dt
            )
            w23_new += (
                path_current_gain * abs(j23) * dt
                + path_power_gain * dP23 * dt
                + path_residual_gain * r23 * dt
                + path_hidden_gain * h23 * dt
            )
            w12, w23 = normalize_path(
                w12_new, w23_new, total_path_weight
            )
        else:
            w12, w23 = normalize_path(1.0, 1.0, total_path_weight)

        w12_hist[k + 1] = w12
        w23_hist[k + 1] = w23
        path_dominance[k + 1] = (
            (w12 - w23) / (w12 + w23 + 1e-12)
        )

    pos_hit_work = np.zeros_like(evolved_av_next, dtype=float)
    neg_hit_work = np.zeros_like(evolved_av_next, dtype=float)
    if n > 1:
        pos_hit_work[1:] = np.cumsum(
            np.maximum(evolved_av_next[1:], 0.0) * dt,
            axis=0,
        )
        neg_hit_work[1:] = np.cumsum(
            np.maximum(-evolved_av_next[1:], 0.0) * dt,
            axis=0,
        )

    return {
        "method_key": method_key,
        "method_name": method_name,
        "method_stage": method_stage,
        "operator_key": operator_key,
        "operator_name": operator_name,
        "dynamic_path_enabled": dynamic_path_enabled,
        "response_feedback_enabled": response_feedback_enabled,
        "input_mode": input_mode,
        "boundary_floor": boundary_floor,
        "t": t,
        "u": u,
        "v": v,
        "a": a,
        "p_av": p_av,
        "p_hit": p_hit,
        "signed_p_hit": evolved_av_next,
        "evolved_av_next": evolved_av_next,
        "evolved_av_next_residual": p_av - evolved_av_next,
        "w_hit": w_hit,
        "pos_hit_work": pos_hit_work,
        "neg_hit_work": neg_hit_work,
        "measured_abs_work": measured_abs_work,
        "measured_signed_work": measured_signed_work,
        "disp_env": disp_env,
        "disp_env_norm": disp_env_norm,
        "hidden_work_proxy": hidden_work_proxy,
        "w12_hist": w12_hist,
        "w23_hist": w23_hist,
        "path_dominance": path_dominance,
        "j12_hist": j12_hist,
        "j23_hist": j23_hist,
        "state_fidelity": state_fidelity,
        "residual_norm": residual_norm,
        "dt": dt,
    }


def _save_arrays(folder: Path, arrays: Dict[str, np.ndarray]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, value in arrays.items():
        np.save(folder / f"{name}.npy", np.asarray(value), allow_pickle=False)


def _load_arrays(folder: Path, names: Sequence[str]) -> Dict[str, np.ndarray]:
    return {
        name: np.load(folder / f"{name}.npy", mmap_mode="r")
        for name in names
    }


PREPARED_ARRAY_NAMES: Tuple[str, ...] = (
    "t",
    "u",
    "v",
    "a",
    "psi_meas",
    "phase",
    "p_av",
    "p_av_norm",
    "p_abs_norm",
    "disp_env",
    "disp_env_norm",
    "measured_abs_work",
    "measured_signed_work",
)


METHOD_ARRAY_NAMES: Tuple[str, ...] = (
    "evolved_av_next",
    "w_hit",
    "pos_hit_work",
    "neg_hit_work",
    "hidden_work_proxy",
    "w12_hist",
    "w23_hist",
    "path_dominance",
    "j12_hist",
    "j23_hist",
    "state_fidelity",
    "residual_norm",
)


def _spec_from_dict(data: Dict[str, object]) -> CaseSpec:
    return CaseSpec(
        case_id=str(data["case_id"]),
        display_name=str(data["display_name"]),
        event_name=str(data["event_name"]),
        input_scale=str(data["input_scale"]),
        control_mode=str(data["control_mode"]),
        acquisition_context=str(data["acquisition_context"]),
        filename=str(data["filename"]),
        aliases=tuple(data.get("aliases", ())),
    )


def prepare_case_cache_worker(payload: Dict[str, object]) -> Dict[str, object]:
    started = time.perf_counter()
    spec = _spec_from_dict(dict(payload["spec"]))
    source_path = Path(str(payload["source_path"]))
    cache_dir = Path(str(payload["cache_dir"]))
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    df, read_metadata = read_nees_csv(
        source_path,
        stride=int(payload["stride"]),
        chunk_rows=int(payload["chunk_rows"]),
    )
    t, u, v, a, signal_map = extract_floor_arrays(
        df,
        allow_acceleration_reconstruction=bool(
            payload["allow_acceleration_reconstruction"]
        ),
    )
    del df

    auto_start, auto_end = detect_event_window(t, a)
    start_override = payload.get("event_start_override")
    end_override = payload.get("event_end_override")
    event_start = (
        float(start_override) if start_override is not None else auto_start
    )
    event_end = float(end_override) if end_override is not None else auto_end
    if event_end <= event_start:
        raise ValueError("event-end must be greater than event-start")

    prepared = prepare_case_features(t, u, v, a)
    array_payload = {
        name: np.asarray(prepared[name])
        for name in PREPARED_ARRAY_NAMES
    }
    _save_arrays(cache_dir / "arrays", array_payload)

    metadata = {
        "release": "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V12.2",
        "spec": asdict(spec),
        "source_path": str(source_path),
        "read_metadata": read_metadata,
        "signal_map": signal_map,
        "event_start": event_start,
        "event_end": event_end,
        "event_selection": (
            "CLI override"
            if start_override is not None or end_override is not None
            else "automatic cumulative acceleration-state activity window"
        ),
        "dt": float(prepared["dt"]),
        "elapsed_seconds": time.perf_counter() - started,
    }
    (cache_dir / "case_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "case_id": spec.case_id,
        "cache_dir": str(cache_dir),
        "source_path": str(source_path),
        "rows_loaded": int(read_metadata["rows_loaded"]),
        "elapsed_seconds": float(metadata["elapsed_seconds"]),
    }


def run_method_cache_worker(payload: Dict[str, object]) -> Dict[str, object]:
    started = time.perf_counter()
    cache_dir = Path(str(payload["cache_dir"]))
    result_dir = Path(str(payload["result_dir"]))
    method_def = tuple(payload["method_def"])
    if result_dir.exists():
        shutil.rmtree(result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    prepared_arrays = _load_arrays(
        cache_dir / "arrays", PREPARED_ARRAY_NAMES
    )
    meta = json.loads((cache_dir / "case_metadata.json").read_text(encoding="utf-8"))
    prepared: Dict[str, np.ndarray | float] = dict(prepared_arrays)
    prepared["dt"] = float(meta["dt"])

    (
        method_key,
        method_name,
        method_stage,
        operator_key,
        operator_name,
        dynamic_path_enabled,
        response_feedback_enabled,
        input_mode,
    ) = method_def
    _UNITARY_CACHE.clear()
    result = run_method_prepared(
        prepared,
        method_key=str(method_key),
        method_name=str(method_name),
        method_stage=str(method_stage),
        operator_key=str(operator_key),
        operator_name=str(operator_name),
        dynamic_path_enabled=bool(dynamic_path_enabled),
        response_feedback_enabled=bool(response_feedback_enabled),
        input_mode=str(input_mode),
        boundary_index=0,
    )
    _save_arrays(
        result_dir,
        {name: np.asarray(result[name]) for name in METHOD_ARRAY_NAMES},
    )
    result_meta = {
        "method_key": result["method_key"],
        "method_name": result["method_name"],
        "method_stage": result["method_stage"],
        "operator_key": result["operator_key"],
        "operator_name": result["operator_name"],
        "dynamic_path_enabled": result["dynamic_path_enabled"],
        "response_feedback_enabled": result["response_feedback_enabled"],
        "input_mode": result["input_mode"],
        "boundary_floor": result["boundary_floor"],
        "dt": result["dt"],
        "elapsed_seconds": time.perf_counter() - started,
    }
    (result_dir / "metadata.json").write_text(
        json.dumps(result_meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {
        "case_id": str(payload["case_id"]),
        "method_key": str(method_key),
        "method_name": str(method_name),
        "result_dir": str(result_dir),
        "elapsed_seconds": float(result_meta["elapsed_seconds"]),
    }


def load_cached_method_result(cache_dir: Path, result_dir: Path) -> Dict[str, object]:
    prepared = _load_arrays(cache_dir / "arrays", PREPARED_ARRAY_NAMES)
    arrays = _load_arrays(result_dir, METHOD_ARRAY_NAMES)
    meta = json.loads((result_dir / "metadata.json").read_text(encoding="utf-8"))
    evolved = np.asarray(arrays["evolved_av_next"])
    p_av = np.asarray(prepared["p_av"])
    return {
        **meta,
        "t": prepared["t"],
        "u": prepared["u"],
        "v": prepared["v"],
        "a": prepared["a"],
        "p_av": prepared["p_av"],
        "p_hit": np.abs(evolved),
        "signed_p_hit": arrays["evolved_av_next"],
        "evolved_av_next": arrays["evolved_av_next"],
        "evolved_av_next_residual": p_av - evolved,
        "w_hit": arrays["w_hit"],
        "pos_hit_work": arrays["pos_hit_work"],
        "neg_hit_work": arrays["neg_hit_work"],
        "measured_abs_work": prepared["measured_abs_work"],
        "measured_signed_work": prepared["measured_signed_work"],
        "disp_env": prepared["disp_env"],
        "disp_env_norm": prepared["disp_env_norm"],
        "hidden_work_proxy": arrays["hidden_work_proxy"],
        "w12_hist": arrays["w12_hist"],
        "w23_hist": arrays["w23_hist"],
        "path_dominance": arrays["path_dominance"],
        "j12_hist": arrays["j12_hist"],
        "j23_hist": arrays["j23_hist"],
        "state_fidelity": arrays["state_fidelity"],
        "residual_norm": arrays["residual_norm"],
        "dt": float(meta["dt"]),
    }


METHOD_ORDER: Tuple[str, ...] = ("qsm", "qte", "fate")


METHOD_LABELS = {
    "qsm": "QSM",
    "qte": "QTE",
    "fate": "FATE",
}


METHOD_DEFS = (
    (
        "qsm",
        "QSM",
        "qsm",
        "zero_diagonal",
        "Zero-diagonal Hamiltonian H=-W",
        False,
        False,
        "boundary_input_only",
    ),
    (
        "qte",
        "QTE",
        "qte",
        "laplacian",
        "Laplacian topology Hamiltonian H=L(W)",
        True,
        False,
        "boundary_input_only",
    ),
    (
        "fate",
        "FATE",
        "fate",
        "laplacian",
        "Sensor-aware Laplacian evolution (Aware_power)",
        True,
        True,
        "floor_state_assimilated",
    ),
)


PROJECT_METADATA = {
    "project_id": "NEES-2011-1076",
    "project_title": "RTHS and Shake Table Comparison for Smart Structural Systems",
    "doi": "10.7277/TPS7-V877",
    "nsf_award": "CMMI-1011534 (NEESR)",
    "release": "V12.2",
    "method_chain": "QSM -> QTE -> FATE",
    "method_scope": {
        "QSM": "zero-diagonal input-driven power-state evolution",
        "QTE": "Laplacian spatial topology-path evolution; current NEES execution has no hard structural-parameter field diagonal",
        "FATE": "sensor-aware evolution at the Aware_power layer",
    },
}


def _ordered_method_results(results: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    by_key = {str(r["method_key"]): r for r in results}
    missing = [key for key in METHOD_ORDER if key not in by_key]
    if missing:
        raise ValueError(f"Missing V12.2 methods: {missing}")
    return [by_key[key] for key in METHOD_ORDER]


def _methodize_mode_df(mode_df: pd.DataFrame) -> pd.DataFrame:
    out = mode_df.copy()
    out["method_order"] = out["method_key"].map(
        {key: i + 1 for i, key in enumerate(METHOD_ORDER)}
    )
    out = out.sort_values("method_order").reset_index(drop=True)
    cols = [
        "method_order", "method_key", "method_name", "method_stage",
        "operator_key", "operator_name", "dynamic_path_enabled",
        "response_feedback_enabled", "input_mode", "boundary_floor",
        "path_manifestation", "final_w12", "final_w23",
        "final_path_dominance_index", "mean_path_dominance_index",
        "edge_current_rms_1F_2F", "edge_current_rms_2F_3F",
        "edge_current_concentration_ratio_1F_2F_over_2F_3F",
        "mean_evolved_av_next_vs_measured_av_corr",
        "mean_evolved_abs_av_next_vs_measured_abs_av_corr",
        "mean_one_step_av_evolution_residual_rmse",
        "mean_target_hit_power_alignment_corr",
        "mean_signed_hit_power_vs_signed_av_corr",
        "mean_target_hit_peak_time_offset_seconds",
        "work_capacity_scale", "mean_manifested_work_ratio",
        "mean_unmanifested_work_margin", "max_response_floor",
    ]
    return out[[c for c in cols if c in out.columns]]


def _methodize_target_df(target_df: pd.DataFrame) -> pd.DataFrame:
    out = target_df.copy()
    order_map = {key: i + 1 for i, key in enumerate(METHOD_ORDER)}
    out["method_order"] = out["method_key"].map(order_map)
    out = out.sort_values(["method_order", "target_floor_no"]).reset_index(drop=True)
    cols = [
        "method_order", "method_key", "method_name", "method_stage",
        "operator_key", "operator_name", "dynamic_path_enabled",
        "response_feedback_enabled", "input_mode", "boundary_floor",
        "target_floor_no", "target_floor",
        "evolved_av_next_vs_measured_av_corr",
        "evolved_abs_av_next_vs_measured_abs_av_corr",
        "one_step_av_evolution_residual_rmse",
        "target_hit_power_alignment_corr",
        "signed_hit_power_vs_signed_av_corr",
        "target_hit_power_peak_time_seconds",
        "measured_abs_a_times_v_peak_time_seconds",
        "target_hit_power_peak_time_offset_seconds",
        "w_hit_final", "work_capacity_scale", "hit_work_capacity_final",
        "displacement_side_work_final", "manifested_work_ratio",
        "unmanifested_work_margin", "measured_abs_work_final",
        "measured_signed_work_final", "max_downstream_response_envelope",
        "downstream_response_peak_time_seconds", "hidden_work_proxy_mean",
    ]
    return out[[c for c in cols if c in out.columns]]


def build_v12_2_history(results: Sequence[Dict[str, object]]) -> pd.DataFrame:
    """Build one canonical, traceable history table for the full three-stage chain.

    V12.2 keeps the concise QSM -> QTE -> FATE organization while restoring the
    physical evidence fields that were calculated but hidden in V12. Measured
    structural channels are written once; method-specific manifestation, work,
    path, current, fidelity, and residual histories are written for each stage.
    """
    ordered = _ordered_method_results(results)
    base = ordered[0]
    t = np.asarray(base["t"], dtype=float)
    data: Dict[str, object] = {
        "00_method_chain": np.repeat("QSM-QTE-FATE", len(t)),
        "01_time_s": t,
    }

    measured_fields = {
        "u": np.asarray(base["u"], dtype=float),
        "v": np.asarray(base["v"], dtype=float),
        "a": np.asarray(base["a"], dtype=float),
        "av": np.asarray(base["p_av"], dtype=float),
        "abs_av": np.abs(np.asarray(base["p_av"], dtype=float)),
        "disp_env": np.asarray(base["disp_env"], dtype=float),
        "disp_env_norm": np.asarray(base["disp_env_norm"], dtype=float),
        "abs_work": np.asarray(base["measured_abs_work"], dtype=float),
        "signed_work": np.asarray(base["measured_signed_work"], dtype=float),
    }
    col_no = 2
    for i, floor in enumerate(("1F", "2F", "3F")):
        for label, values in measured_fields.items():
            data[f"{col_no:03d}_measured_{label}_{floor}"] = values[:, i]
            col_no += 1

    for result in ordered:
        key = str(result["method_key"])
        capacity_scale = compute_work_capacity_scale(result)
        evolved = np.asarray(result["evolved_av_next"], dtype=float)
        residual = np.asarray(result["evolved_av_next_residual"], dtype=float)
        p_hit = np.asarray(result["p_hit"], dtype=float)
        signed_p_hit = np.asarray(result["signed_p_hit"], dtype=float)
        w_hit = np.asarray(result["w_hit"], dtype=float)
        pos_hit = np.asarray(result["pos_hit_work"], dtype=float)
        neg_hit = np.asarray(result["neg_hit_work"], dtype=float)
        hidden = np.asarray(result["hidden_work_proxy"], dtype=float)
        measured_abs_work = np.asarray(result["measured_abs_work"], dtype=float)

        for i, floor in enumerate(("1F", "2F", "3F")):
            hit_capacity = capacity_scale * w_hit[:, i]
            capacity_ref = max(float(hit_capacity[-1]), 1e-12)
            floor_fields = {
                "evolved_av": evolved[:, i],
                "evolved_av_residual": residual[:, i],
                "p_hit": p_hit[:, i],
                "signed_p_hit": signed_p_hit[:, i],
                "w_hit": w_hit[:, i],
                "pos_hit_work": pos_hit[:, i],
                "neg_hit_work": neg_hit[:, i],
                "hidden_work_proxy": hidden[:, i],
                "hit_work_capacity_norm": hit_capacity / capacity_ref,
                "displacement_side_work_norm": measured_abs_work[:, i] / capacity_ref,
                "work_capacity_margin_norm": (hit_capacity - measured_abs_work[:, i]) / capacity_ref,
            }
            for label, values in floor_fields.items():
                data[f"{col_no:03d}_{key}_{label}_{floor}"] = values
                col_no += 1

        stage_fields = {
            "w12": np.asarray(result["w12_hist"], dtype=float),
            "w23": np.asarray(result["w23_hist"], dtype=float),
            "path_dominance": np.asarray(result["path_dominance"], dtype=float),
            "j12": np.asarray(result["j12_hist"], dtype=float),
            "j23": np.asarray(result["j23_hist"], dtype=float),
            "state_fidelity": np.asarray(result["state_fidelity"], dtype=float),
            "residual_norm": np.asarray(result["residual_norm"], dtype=float),
        }
        for label, values in stage_fields.items():
            data[f"{col_no:03d}_{key}_{label}"] = values
            col_no += 1

    df = pd.DataFrame(data)
    if len(df) > 3000:
        idx = np.linspace(0, len(df) - 1, 3000).astype(int)
        df = df.iloc[idx].reset_index(drop=True)
    return df

def _event_indices(t: np.ndarray, start: float, end: float, max_points: int = 1200) -> np.ndarray:
    idx = np.where((t >= start) & (t <= end))[0]
    if len(idx) == 0:
        idx = np.arange(len(t))
    if len(idx) > max_points:
        idx = idx[np.linspace(0, len(idx) - 1, max_points).astype(int)]
    return idx


def make_figures(
    out: Path,
    results: List[Dict],
    mode_df: pd.DataFrame,
    target_df: pd.DataFrame,
    event_start: float,
    event_end: float,
    case_title: str,
):
    """Create the complete V12.2 observation suite.

    The analytical organization remains QSM -> QTE -> FATE. No legacy
    boundary/fixed/no-feedback sensitivity groups are generated. V12.2 restores
    the independent physical observation figures that V12 incorrectly removed.
    """
    if plt is None:
        return

    ordered = _ordered_method_results(results)
    by_key = {str(r["method_key"]): r for r in ordered}
    mode = _methodize_mode_df(mode_df)
    target = _methodize_target_df(target_df)
    qsm = by_key["qsm"]
    qte = by_key["qte"]
    fate = by_key["fate"]
    t = np.asarray(qsm["t"], dtype=float)
    idx_event = _event_indices(t, event_start, event_end, max_points=1200)
    idx_full = _event_indices(t, float(t[0]), float(t[-1]), max_points=1400)

    # 06 — ordered stage-wise alignment bar: QSM -> QTE -> FATE.
    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(3, dtype=float)
    width = 0.24
    for offset, floor in zip((-1, 0, 1), ("1F", "2F", "3F")):
        vals = []
        for method in METHOD_ORDER:
            row = target[(target["method_key"] == method) & (target["target_floor"] == floor)]
            vals.append(float(row["evolved_abs_av_next_vs_measured_abs_av_corr"].iloc[0]))
        bars = ax.bar(x + offset * width, vals, width, label=floor)
        for bar, value in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, value + 0.015, f"{value:.3f}",
                    ha="center", va="bottom", fontsize=8, rotation=90)
    ax.set_xticks(x, ["QSM", "QTE", "FATE"])
    ax.set_ylim(0.0, 1.08)
    ax.set_ylabel("Absolute-envelope correlation")
    ax.set_title(f"{case_title}\nQSM → QTE → FATE stage-wise three-floor observation alignment")
    ax.legend(title="Floor")
    fig.tight_layout()
    fig.savefig(out / "06_qsm_qte_fate_stage_bar.png", dpi=180)
    plt.close(fig)

    # 07-09 — one three-floor waveform figure for each stage.
    figure_files = {
        "qsm": "07_qsm_three_floor_waveforms.png",
        "qte": "08_qte_three_floor_waveforms.png",
        "fate": "09_fate_three_floor_waveforms.png",
    }
    method_subtitles = {
        "qsm": "Zero-diagonal input-driven power-state evolution",
        "qte": "Laplacian spatial topology-path evolution",
        "fate": "Sensor-aware evolution — Aware_power",
    }
    for result in ordered:
        method = str(result["method_key"])
        measured = np.asarray(result["p_av"], dtype=float)
        evolved = np.asarray(result["evolved_av_next"], dtype=float)
        method_target = target[target["method_key"] == method]
        method_mode = mode[mode["method_key"] == method].iloc[0]
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        for i, (ax, floor) in enumerate(zip(axes, ("1F", "2F", "3F"))):
            scale = max(float(np.nanmax(np.abs(measured[idx_event, i]))),
                        float(np.nanmax(np.abs(evolved[idx_event, i]))), 1e-12)
            row = method_target[method_target["target_floor"] == floor].iloc[0]
            signed_corr = float(row["evolved_av_next_vs_measured_av_corr"])
            abs_corr = float(row["evolved_abs_av_next_vs_measured_abs_av_corr"])
            rms_ratio = float(np.sqrt(np.nanmean(evolved[:, i]**2)) /
                              (np.sqrt(np.nanmean(measured[:, i]**2)) + 1e-12))
            ax.axhline(0.0, linewidth=1)
            ax.plot(t[idx_event], evolved[idx_event, i]/scale,
                    label=f"{METHOD_LABELS[method]} evolved a·v (k+1|k)")
            ax.plot(t[idx_event], measured[idx_event, i]/scale,
                    linestyle="--", label="Measured a·v (k+1)")
            ax.set_ylim(-1.08, 1.08)
            ax.set_ylabel(f"{floor}\nnormalized a·v")
            ax.set_title(f"{floor}: signed r={signed_corr:.3f}; abs-envelope r={abs_corr:.3f}; RMS ratio={rms_ratio:.3f}")
            ax.legend(loc="upper right")
        axes[-1].set_xlabel("Time (s)")
        if method == "qsm":
            metric_line = (f"mean signed r={float(method_mode['mean_evolved_av_next_vs_measured_av_corr']):.3f}; "
                           f"mean abs-envelope r={float(method_mode['mean_evolved_abs_av_next_vs_measured_abs_av_corr']):.3f}")
        elif method == "qte":
            metric_line = (f"final path dominance={float(method_mode['final_path_dominance_index']):.3f}; "
                           f"edge-current ratio={float(method_mode['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.3f}")
        else:
            metric_line = (f"mean state fidelity={float(np.nanmean(result['state_fidelity'])):.3f}; "
                           f"mean residual norm={float(np.nanmean(result['residual_norm'])):.3f}")
        fig.suptitle(f"{case_title}\n{METHOD_LABELS[method]} — {method_subtitles[method]}\n{metric_line}", y=0.995)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        fig.savefig(out / figure_files[method], dpi=180)
        plt.close(fig)

    # 10 — Edge-current concentration ratio, still ordered by the three stages.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ratios = [float(mode[mode["method_key"] == key]["edge_current_concentration_ratio_1F_2F_over_2F_3F"].iloc[0]) for key in METHOD_ORDER]
    bars = ax.bar(np.arange(3), ratios)
    for bar, value in zip(bars, ratios):
        ax.text(bar.get_x()+bar.get_width()/2, value, f"{value:.3f}", ha="center", va="bottom")
    ax.axhline(1.0, linestyle="--", linewidth=1, label="Equal RMS concentration")
    ax.set_xticks(np.arange(3), ["QSM", "QTE", "FATE"])
    ax.set_ylabel("RMS edge-current ratio: 1F–2F / 2F–3F")
    ax.set_title(f"{case_title}\nEdge-current concentration across the QSM → QTE → FATE chain")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "10_qsm_qte_fate_edge_current_ratio.png", dpi=180)
    plt.close(fig)

    # 11 — QTE spatial path-weight evolution.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(t[idx_full], np.asarray(qte["w12_hist"])[idx_full], label="1F–2F path weight")
    ax.plot(t[idx_full], np.asarray(qte["w23_hist"])[idx_full], label="2F–3F path weight")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Path weight")
    ax.set_title(f"{case_title}\nQTE Laplacian spatial path-weight evolution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "11_qte_path_weight_evolution.png", dpi=180)
    plt.close(fig)

    # 12 — FATE sensor-aware path-weight evolution.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(t[idx_full], np.asarray(fate["w12_hist"])[idx_full], label="1F–2F path weight")
    ax.plot(t[idx_full], np.asarray(fate["w23_hist"])[idx_full], label="2F–3F path weight")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Path weight")
    ax.set_title(f"{case_title}\nFATE Aware_power sensor-aware path-weight evolution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "12_fate_sensor_aware_path_evolution.png", dpi=180)
    plt.close(fig)

    # 13 — QTE and FATE edge-current evolution (current envelopes, not extra methods).
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for ax, result, key in zip(axes, (qte, fate), ("qte", "fate")):
        dt_local = float(np.nanmedian(np.diff(t))) if len(t) > 1 else 0.005
        span = max(5, int(round(0.30 / max(dt_local, 1e-9))))
        j12_env = pd.Series(np.abs(np.asarray(result["j12_hist"], dtype=float))).ewm(span=span, adjust=False).mean().to_numpy()
        j23_env = pd.Series(np.abs(np.asarray(result["j23_hist"], dtype=float))).ewm(span=span, adjust=False).mean().to_numpy()
        scale = max(float(np.nanmax(j12_env[idx_full])), float(np.nanmax(j23_env[idx_full])), 1e-12)
        ratio = float(mode[mode["method_key"] == key]["edge_current_concentration_ratio_1F_2F_over_2F_3F"].iloc[0])
        ax.plot(t[idx_full], j12_env[idx_full]/scale, label="|J12| causal envelope")
        ax.plot(t[idx_full], j23_env[idx_full]/scale, label="|J23| causal envelope")
        ax.set_ylabel(f"{key.upper()}\nnormalized current")
        ax.set_title(f"{key.upper()}: RMS J12/J23 ratio={ratio:.3f}")
        ax.legend()
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle(f"{case_title}\nQTE → FATE edge-current evolution", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out / "13_qte_fate_edge_current_evolution.png", dpi=180)
    plt.close(fig)

    # 14 — spatial path dominance before and after sensor awareness.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(t[idx_full], np.asarray(qte["path_dominance"])[idx_full], label="QTE path dominance")
    ax.plot(t[idx_full], np.asarray(fate["path_dominance"])[idx_full], label="FATE sensor-aware path dominance")
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Path dominance index")
    ax.set_title(f"{case_title}\nQTE → FATE path-dominance evolution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "14_qte_fate_path_dominance_evolution.png", dpi=180)
    plt.close(fig)

    # 15 — FATE target-hit and state-awareness history.
    fig, axes = plt.subplots(4, 1, figsize=(12, 11), sharex=True)
    measured_abs = np.abs(np.asarray(fate["p_av"], dtype=float))
    p_hit = np.asarray(fate["p_hit"], dtype=float)
    for i, (ax, floor) in enumerate(zip(axes[:3], ("1F", "2F", "3F"))):
        scale = max(float(np.nanmax(measured_abs[idx_event, i])), float(np.nanmax(p_hit[idx_event, i])), 1e-12)
        ax.plot(t[idx_event], p_hit[idx_event, i]/scale, label="FATE target-hit Power")
        ax.plot(t[idx_event], measured_abs[idx_event, i]/scale, linestyle="--", label="Measured |a·v|")
        ax.set_ylabel(f"{floor}\nnormalized")
        ax.legend(loc="upper right")
    fidelity = np.asarray(fate["state_fidelity"], dtype=float)
    residual = np.asarray(fate["residual_norm"], dtype=float)
    residual_normed = residual / (float(np.nanmax(np.abs(residual[idx_event]))) + 1e-12)
    axes[3].plot(t[idx_event], fidelity[idx_event], label="State fidelity")
    axes[3].plot(t[idx_event], residual_normed[idx_event], label="Residual norm (normalized)")
    axes[3].set_ylabel("Awareness")
    axes[3].set_xlabel("Time (s)")
    axes[3].legend(loc="upper right")
    fig.suptitle(f"{case_title}\nFATE Aware_power: target-hit manifestation and state awareness", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out / "15_fate_target_hit_state_awareness.png", dpi=180)
    plt.close(fig)

    # 16 — FATE work-compatible proxy ratios by floor.
    fate_target = target[target["method_key"] == "fate"].sort_values("target_floor_no")
    floors = list(fate_target["target_floor"])
    x = np.arange(len(floors))
    width = 0.36
    manifested = fate_target["manifested_work_ratio"].to_numpy(dtype=float)
    margin = fate_target["unmanifested_work_margin"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x-width/2, manifested, width, label="Manifested work ratio")
    ax.bar(x+width/2, margin, width, label="Unmanifested work margin")
    ax.axhline(0.0, linewidth=1)
    ax.set_xticks(x, floors)
    ax.set_ylabel("Work-compatible proxy ratio")
    ax.set_title(f"{case_title}\nFATE work-compatible manifestation proxies by floor")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "16_fate_work_proxy_ratios_by_floor.png", dpi=180)
    plt.close(fig)

    # 17 — traditional structural-dynamics entrance: measured acceleration-displacement loops.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, floor in enumerate(("1F", "2F", "3F")):
        u_norm = normalize_by_max(np.asarray(fate["u"][:, i], dtype=float))
        a_norm = normalize_by_max(np.asarray(fate["a"][:, i], dtype=float))
        ax.plot(u_norm[idx_event], a_norm[idx_event], label=f"{floor} a–u loop")
    ax.axhline(0.0, linewidth=1)
    ax.axvline(0.0, linewidth=1)
    ax.set_xlabel("Measured displacement u(t), normalized")
    ax.set_ylabel("Acceleration / force proxy a(t), normalized")
    ax.set_title(f"{case_title}\nTraditional structural entrance: normalized acceleration–displacement work-loop proxy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "17_force_displacement_work_loop_proxy.png", dpi=180)
    plt.close(fig)

    # 18 — measured downstream response manifestation by floor.
    vals = fate_target["max_downstream_response_envelope"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(np.arange(3), vals)
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, value, f"{value:.6g}", ha="center", va="bottom")
    ax.set_xticks(np.arange(3), floors)
    ax.set_ylabel("Max measured displacement-response envelope")
    ax.set_title(f"{case_title}\nObserved downstream response manifestation by floor")
    fig.tight_layout()
    fig.savefig(out / "18_response_manifestation_by_floor.png", dpi=180)
    plt.close(fig)

def write_case_report_v12_2(
    out: Path,
    spec: CaseSpec,
    source_path: Path,
    mode_df: pd.DataFrame,
    target_df: pd.DataFrame,
    signal_map: Dict[str, Dict[str, str]],
) -> None:
    mode = _methodize_mode_df(mode_df)
    target = _methodize_target_df(target_df)
    lines = [
        f"# {spec.display_name}", "",
        "## QSM–QTE–FATE Integrated Seismic Field Observation · V12.2", "",
        f"- Source file: `{source_path.name}`",
        f"- Earthquake input: **{spec.event_name}**",
        f"- Input scale: **{spec.input_scale}**",
        f"- Control state: **{spec.control_mode}**",
        f"- Acquisition context: **{spec.acquisition_context}**", "",
        "## Three-stage method chain", "",
        "| Order | Method | Hamiltonian / update | Observation role |",
        "|---:|---|---|---|",
        "| 1 | QSM | `H = -W`, zero diagonal | Input-driven power-state evolution |",
        "| 2 | QTE | `H = L(W)` in the present NEES execution | Spatial topology-path evolution |",
        "| 3 | FATE | QTE evolution with continuous floor-sensor assimilation and response feedback | `Aware_power` |", "",
        "> The present QTE execution uses the Laplacian topology term. A hard structural-parameter field diagonal is not asserted for these NEES records.", "",
        "## Method summary", "",
        "| Method | Mean signed corr | Mean abs-envelope corr | Final path dominance | Edge-current ratio 1F–2F / 2F–3F | Mean manifested-work ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in mode.iterrows():
        lines.append(
            f"| {row['method_name']} | {float(row['mean_evolved_av_next_vs_measured_av_corr']):.3f} | "
            f"{float(row['mean_evolved_abs_av_next_vs_measured_abs_av_corr']):.3f} | "
            f"{float(row['final_path_dominance_index']):.3f} | "
            f"{float(row['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.3f} | "
            f"{float(row['mean_manifested_work_ratio']):.3f} |"
        )
    lines += ["", "## Three-floor results", "",
              "| Method | Floor | Signed corr | Abs-envelope corr | Residual RMSE | Manifested-work ratio | Response envelope |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for _, row in target.iterrows():
        lines.append(
            f"| {row['method_name']} | {row['target_floor']} | "
            f"{float(row['evolved_av_next_vs_measured_av_corr']):.3f} | "
            f"{float(row['evolved_abs_av_next_vs_measured_abs_av_corr']):.3f} | "
            f"{float(row['one_step_av_evolution_residual_rmse']):.6g} | "
            f"{float(row['manifested_work_ratio']):.3f} | "
            f"{float(row['max_downstream_response_envelope']):.6g} |"
        )
    lines += [
        "", "## Figure guide", "",
        "| Figure | Question answered |",
        "|---|---|",
        "| `06_qsm_qte_fate_stage_bar.png` | How does three-floor observation alignment evolve through QSM → QTE → FATE? |",
        "| `07_qsm_three_floor_waveforms.png` | What does zero-diagonal QSM evolve at 1F, 2F, and 3F? |",
        "| `08_qte_three_floor_waveforms.png` | What does Laplacian QTE evolve at 1F, 2F, and 3F? |",
        "| `09_fate_three_floor_waveforms.png` | What changes when sensor-aware FATE updates the three floors? |",
        "| `10_qsm_qte_fate_edge_current_ratio.png` | How is RMS edge-current concentration redistributed through the three-stage chain? |",
        "| `11_qte_path_weight_evolution.png` | How does the QTE spatial path evolve? |",
        "| `12_fate_sensor_aware_path_evolution.png` | How does sensor awareness reshape the path in FATE? |",
        "| `13_qte_fate_edge_current_evolution.png` | How do J12 and J23 evolve before and after sensor awareness? |",
        "| `14_qte_fate_path_dominance_evolution.png` | How does path dominance evolve from QTE to FATE? |",
        "| `15_fate_target_hit_state_awareness.png` | How do target-hit Power, measured |a·v|, fidelity, and residual evolve together? |",
        "| `16_fate_work_proxy_ratios_by_floor.png` | What portion of work-compatible capacity is manifested or remains unmanifested? |",
        "| `17_force_displacement_work_loop_proxy.png` | How does the result reconnect to the traditional acceleration/force–displacement structural entrance? |",
        "| `18_response_manifestation_by_floor.png` | Where is the largest measured downstream displacement response? |",
        "", "## Signal provenance", "",
        "| Floor | Displacement | Velocity | Acceleration |",
        "|---|---|---|---|",
    ]
    for floor, mapping in signal_map.items():
        lines.append(f"| {floor} | `{mapping['u']}` | `{mapping['v']}` | `{mapping['a']}` |")
    lines += [
        "", "## Interpretation boundary", "",
        "V12.2 keeps the single QSM → QTE → FATE method chain. The restored figures are independent physical observation dimensions, not additional sensitivity groups or competing methods.", "",
        "## Data citation", "",
        "Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. DOI: 10.7277/TPS7-V877.", "",
    ]
    (out / "04_CASE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    short_lines = [
        "QSM-QTE-FATE Integrated Seismic Field Observation — V12.2",
        f"Case: {spec.display_name}", f"Source: {source_path.name}", "",
    ]
    for _, row in mode.iterrows():
        short_lines.append(
            f"{row['method_name']}: mean signed corr={float(row['mean_evolved_av_next_vs_measured_av_corr']):.6f}; "
            f"mean abs-envelope corr={float(row['mean_evolved_abs_av_next_vs_measured_abs_av_corr']):.6f}; "
            f"final path dominance={float(row['final_path_dominance_index']):.6f}; "
            f"edge-current ratio={float(row['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.6f}; "
            f"mean manifested-work ratio={float(row['mean_manifested_work_ratio']):.6f}"
        )
    (out / "05_release_report.txt").write_text("\n".join(short_lines)+"\n", encoding="utf-8")

def finalize_cached_case_v12_2(
    spec: CaseSpec,
    source_path: Path,
    cache_dir: Path,
    method_result_dirs: Dict[str, Path],
    case_out: Path,
    workers: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    started = time.perf_counter()
    if case_out.exists():
        shutil.rmtree(case_out)
    case_out.mkdir(parents=True, exist_ok=True)

    cache_meta = json.loads((cache_dir / "case_metadata.json").read_text(encoding="utf-8"))
    results: List[Dict[str, object]] = []
    mode_rows: List[Dict[str, object]] = []
    target_frames: List[pd.DataFrame] = []
    method_elapsed: Dict[str, float] = {}
    for method_def in METHOD_DEFS:
        method_key = str(method_def[0])
        result = load_cached_method_result(cache_dir, method_result_dirs[method_key])
        method_elapsed[method_key] = float(result.get("elapsed_seconds", 0.0))
        mode_row, target = summarize_method(result)
        results.append(result)
        mode_rows.append(mode_row)
        target_frames.append(target)

    mode_df = pd.DataFrame(mode_rows)
    target_df = pd.concat(target_frames, ignore_index=True)
    method_out = _methodize_mode_df(mode_df)
    floor_out = _methodize_target_df(target_df)
    history_out = build_v12_2_history(results)

    method_out.to_csv(case_out / "01_qsm_qte_fate_method_summary.csv", index=False)
    floor_out.to_csv(case_out / "02_qsm_qte_fate_floor_summary.csv", index=False)
    history_out.to_csv(case_out / "03_qsm_qte_fate_full_history.csv", index=False)

    signal_map = cache_meta["signal_map"]
    event_start = float(cache_meta["event_start"])
    event_end = float(cache_meta["event_end"])
    write_case_report_v12_2(case_out, spec, source_path, mode_df, target_df, signal_map)
    make_figures(case_out, results, mode_df, target_df, event_start, event_end, case_title=spec.display_name)

    elapsed = time.perf_counter() - started
    prep_seconds = float(cache_meta.get("elapsed_seconds", 0.0))
    log_lines = [
        "QSM-QTE-FATE Integrated Seismic Field Observation",
        "NEES-2011-1076 Three-Stage Complete Observation Release V12.2", "",
        f"Case: {spec.display_name}", f"Source: {source_path.name}",
        f"Event window: {event_start:.6f} s to {event_end:.6f} s",
        f"Data preparation: {prep_seconds:.3f} s", f"Artifact generation: {elapsed:.3f} s",
        f"Parallel method workers configured: {workers}", "", "Method elapsed times:",
    ]
    for method in METHOD_ORDER:
        log_lines.append(f"  {METHOD_LABELS[method]}: {method_elapsed.get(method, 0.0):.3f} s")
    log_lines += [
        "", "Public method order: QSM -> QTE -> FATE",
        "No boundary-only, fixed-path, or no-feedback sensitivity groups are generated.",
        "The complete physical observation suite is retained: alignment, path weights, edge current, path dominance, target hit, work proxies, structural work loops, and response manifestation.",
    ]
    (case_out / "19_release_run_log.txt").write_text("\n".join(log_lines)+"\n", encoding="utf-8")

    manifest = {
        "release": "QSM-QTE-FATE Integrated Seismic Field Observation — V12.2",
        "case": asdict(spec), "project": PROJECT_METADATA,
        "source_read_metadata": cache_meta["read_metadata"], "signal_provenance": signal_map,
        "event_window_seconds": {"start": event_start, "end": event_end, "selection": cache_meta["event_selection"]},
        "method_order": list(METHOD_ORDER),
        "method_definitions": [
            {"method_key": d[0], "method_name": d[1], "operator": d[3], "operator_name": d[4],
             "dynamic_path_enabled": d[5], "response_feedback_enabled": d[6], "input_mode": d[7]}
            for d in METHOD_DEFS
        ],
        "output_policy": "three sequential methods plus complete independent physical observation outputs",
        "output_files": sorted([p.name for p in case_out.iterdir() if p.is_file()] + ["20_release_file_manifest.json"]),
    }
    (case_out / "20_release_file_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    method_case = method_out.copy()
    for pos, (name, value) in enumerate([
        ("case_id", spec.case_id), ("case_name", spec.display_name), ("event_name", spec.event_name),
        ("input_scale", spec.input_scale), ("control_mode", spec.control_mode), ("source_file", source_path.name)
    ]):
        method_case.insert(pos, name, value)
    floor_case = floor_out.copy()
    for pos, (name, value) in enumerate([
        ("case_id", spec.case_id), ("case_name", spec.display_name), ("event_name", spec.event_name),
        ("input_scale", spec.input_scale), ("control_mode", spec.control_mode), ("source_file", source_path.name)
    ]):
        floor_case.insert(pos, name, value)
    return method_case, floor_case

def make_cross_case_figures_v12_2(
    out: Path,
    method_df: pd.DataFrame,
    floor_df: pd.DataFrame,
) -> None:
    if plt is None or method_df.empty:
        return
    methods = list(METHOD_ORDER)
    cases = method_df["case_name"].drop_duplicates().tolist()
    x = np.arange(len(methods), dtype=float)
    width = 0.8 / max(len(cases), 1)

    # 03 — sequential QSM → QTE → FATE observation alignment.
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, case_name in enumerate(cases):
        part = method_df[method_df["case_name"] == case_name]
        vals = [
            float(
                part[part["method_key"] == method][
                    "mean_evolved_abs_av_next_vs_measured_abs_av_corr"
                ].iloc[0]
            )
            for method in methods
        ]
        ax.bar(x - 0.4 + width / 2 + i * width, vals, width, label=case_name)
    ax.set_xticks(x, ["QSM", "QTE", "FATE"])
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Mean absolute-envelope correlation")
    ax.set_title("Cross-case QSM → QTE → FATE stage-wise observation alignment")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "03_cross_case_qsm_qte_fate_bar.png", dpi=180)
    plt.close(fig)

    # 04 — edge-current concentration is a separate physical observation.
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, case_name in enumerate(cases):
        part = method_df[method_df["case_name"] == case_name]
        vals = [
            float(
                part[part["method_key"] == method][
                    "edge_current_concentration_ratio_1F_2F_over_2F_3F"
                ].iloc[0]
            )
            for method in methods
        ]
        ax.bar(x - 0.4 + width / 2 + i * width, vals, width, label=case_name)
    ax.axhline(1.0, linestyle="--", linewidth=1)
    ax.set_xticks(x, ["QSM", "QTE", "FATE"])
    ax.set_ylabel("RMS edge-current ratio: 1F–2F / 2F–3F")
    ax.set_title("Cross-case edge-current concentration through the three-stage chain")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "04_cross_case_edge_current_ratio.png", dpi=180)
    plt.close(fig)

    # 05 — FATE path dominance stands alone because it answers where the path manifests.
    fate = method_df[method_df["method_key"] == "fate"].copy()
    xpos = np.arange(len(fate))
    labels = fate["case_name"].tolist()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(xpos, fate["final_path_dominance_index"].to_numpy(dtype=float))
    ax.axhline(0.0, linewidth=1)
    ax.set_ylabel("Final path dominance")
    ax.set_xticks(xpos, labels, rotation=15, ha="right")
    ax.set_title("Cross-case FATE sensor-aware path manifestation")
    fig.tight_layout()
    fig.savefig(out / "05_cross_case_fate_path_dominance.png", dpi=180)
    plt.close(fig)

    # 06 — manifested-work ratio stands alone because it answers how much work is manifested.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(xpos, fate["mean_manifested_work_ratio"].to_numpy(dtype=float))
    ax.axhline(0.0, linewidth=1)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Mean manifested-work ratio")
    ax.set_xticks(xpos, labels, rotation=15, ha="right")
    ax.set_title("Cross-case FATE manifested-work ratio")
    fig.tight_layout()
    fig.savefig(out / "06_cross_case_fate_manifested_work_ratio.png", dpi=180)
    plt.close(fig)

    # 07 — restored three-floor cross-case view, one panel per sequential method.
    if not floor_df.empty:
        floor_order = ["1F", "2F", "3F"]
        fig, axes = plt.subplots(3, 1, figsize=(14, 13), sharex=True)
        case_x = np.arange(len(cases), dtype=float)
        floor_width = 0.24
        offsets = [-floor_width, 0.0, floor_width]
        for ax, method in zip(axes, methods):
            part = floor_df[floor_df["method_key"] == method]
            for offset, floor in zip(offsets, floor_order):
                vals = []
                for case_name in cases:
                    row = part[
                        (part["case_name"] == case_name)
                        & (part["target_floor"] == floor)
                    ]
                    vals.append(
                        float(
                            row[
                                "evolved_abs_av_next_vs_measured_abs_av_corr"
                            ].iloc[0]
                        )
                    )
                ax.bar(case_x + offset, vals, floor_width, label=floor)
            ax.set_ylim(0.0, 1.05)
            ax.set_ylabel("Abs-envelope corr.")
            ax.set_title(f"{METHOD_LABELS[method]} — three-floor observation alignment")
            ax.legend(ncol=3, fontsize=8, loc="upper left")
        axes[-1].set_xticks(case_x, cases, rotation=15, ha="right")
        fig.suptitle("Cross-case three-floor alignment through QSM → QTE → FATE", y=0.995)
        fig.tight_layout(rect=(0, 0, 1, 0.98))
        fig.savefig(out / "07_cross_case_three_floor_alignment.png", dpi=180)
        plt.close(fig)

def write_cross_case_outputs_v12_2(
    root_out: Path,
    method_frames: List[pd.DataFrame],
    floor_frames: List[pd.DataFrame],
    selected_specs: Sequence[CaseSpec],
) -> None:
    cross_out = root_out / "00_cross_case"
    cross_out.mkdir(parents=True, exist_ok=True)
    method_df = pd.concat(method_frames, ignore_index=True)
    floor_df = pd.concat(floor_frames, ignore_index=True)
    method_df.to_csv(cross_out / "01_cross_case_method_summary.csv", index=False)
    floor_df.to_csv(cross_out / "02_cross_case_floor_summary.csv", index=False)
    make_cross_case_figures_v12_2(cross_out, method_df, floor_df)

    lines = [
        "# QSM–QTE–FATE Cross-Case Comparison · V12.2", "",
        "The comparison follows the fixed sequential method order QSM → QTE → FATE. Edge current, path manifestation, and work proxies are reported as physical observation dimensions, not additional methods.", "",
        "## Stage-wise observation alignment", "",
        "| Case | QSM mean abs corr | QTE mean abs corr | FATE mean abs corr |",
        "|---|---:|---:|---:|",
    ]
    for case_name in method_df["case_name"].drop_duplicates():
        part = method_df[method_df["case_name"] == case_name]
        vals = {m: float(part[part["method_key"] == m]["mean_evolved_abs_av_next_vs_measured_abs_av_corr"].iloc[0]) for m in METHOD_ORDER}
        lines.append(f"| {case_name} | {vals['qsm']:.3f} | {vals['qte']:.3f} | {vals['fate']:.3f} |")
    lines += ["", "## Physical observation summary", "",
              "| Case | QSM edge ratio | QTE edge ratio | FATE edge ratio | FATE path dominance | FATE manifested-work ratio |",
              "|---|---:|---:|---:|---:|---:|"]
    for case_name in method_df["case_name"].drop_duplicates():
        part = method_df[method_df["case_name"] == case_name]
        rows = {m: part[part["method_key"] == m].iloc[0] for m in METHOD_ORDER}
        lines.append(
            f"| {case_name} | {float(rows['qsm']['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.3f} | "
            f"{float(rows['qte']['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.3f} | "
            f"{float(rows['fate']['edge_current_concentration_ratio_1F_2F_over_2F_3F']):.3f} | "
            f"{float(rows['fate']['final_path_dominance_index']):.3f} | "
            f"{float(rows['fate']['mean_manifested_work_ratio']):.3f} |"
        )
    lines += ["", "No boundary-only, fixed-path, or no-feedback sensitivity groups are generated.", ""]
    (cross_out / "08_CROSS_CASE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    registry = {"release": "V12.2", "project": PROJECT_METADATA, "method_order": list(METHOD_ORDER), "cases": [asdict(spec) for spec in selected_specs]}
    (cross_out / "09_case_registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = {"release": "V12.2", "output_files": sorted([p.name for p in cross_out.iterdir() if p.is_file()] + ["10_cross_case_file_manifest.json"])}
    (cross_out / "10_cross_case_file_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

def parse_args_v12_2() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "V12.2 three-stage QSM-QTE-FATE Integrated Seismic Field Observation "
            "for NEES-2011-1076"
        )
    )
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--out", default="outputs_qsm_qte_fate_nees_2011_1076_v12_2"
    )
    parser.add_argument(
        "--cases",
        nargs="*",
        choices=[spec.case_id for spec in CASE_SPECS],
    )
    parser.add_argument("--stride", type=int, default=5)
    parser.add_argument("--chunk-rows", type=int, default=200_000)
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Parallel method processes; 0 selects an automatic value",
    )
    parser.add_argument("--prepare-workers", type=int, default=2)
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument(
        "--allow-acceleration-reconstruction", action="store_true"
    )
    parser.add_argument("--event-start", type=float, default=None)
    parser.add_argument("--event-end", type=float, default=None)
    parser.add_argument("--keep-output", action="store_true")
    parser.add_argument("--keep-cache", action="store_true")
    return parser.parse_args()


def main_v12_2() -> None:
    multiprocessing.freeze_support()
    args = parse_args_v12_2()
    if plt is None:
        raise RuntimeError("matplotlib is required for the V12.2 release")

    overall_started = time.perf_counter()
    run_started_utc = datetime.now(timezone.utc).isoformat()
    root = Path(args.root).expanduser().resolve()
    root_out = Path(args.out).expanduser()
    if not root_out.is_absolute():
        root_out = root / root_out
    root_out = root_out.resolve()

    if root_out.exists() and not args.keep_output:
        shutil.rmtree(root_out)
    root_out.mkdir(parents=True, exist_ok=True)
    cache_root = root_out / "_v12_2_cache"
    cache_root.mkdir(parents=True, exist_ok=True)

    selected_ids = set(args.cases or [spec.case_id for spec in CASE_SPECS])
    selected_specs = [
        spec for spec in CASE_SPECS if spec.case_id in selected_ids
    ]
    resolved: List[Tuple[CaseSpec, Path]] = []
    missing: List[CaseSpec] = []
    for spec in selected_specs:
        path = resolve_case_file(root, spec)
        if path is None:
            missing.append(spec)
        else:
            resolved.append((spec, path))

    if missing and not args.allow_missing:
        missing_text = "\n".join(
            f"  - {spec.case_id}: expected {spec.filename}" for spec in missing
        )
        raise FileNotFoundError(
            "Missing required source files:\n"
            f"{missing_text}\n"
            "Use --allow-missing to run only available files."
        )
    if not resolved:
        raise FileNotFoundError(f"No configured case files found under {root}")

    cpu_count = os.cpu_count() or 4
    total_method_tasks = len(resolved) * len(METHOD_DEFS)
    workers = int(args.workers)
    if workers <= 0:
        workers = min(8, max(2, cpu_count - 2), total_method_tasks)
    workers = max(1, min(workers, total_method_tasks))
    prepare_workers = max(
        1, min(int(args.prepare_workers), len(resolved), cpu_count)
    )

    print("=== QSM-QTE-FATE Three-Stage Complete Observation Release V12.2 ===")
    print("Method order: QSM -> QTE -> FATE")
    print(f"Logical processors detected: {cpu_count}")
    print(f"CSV preparation workers: {prepare_workers}")
    print(f"Parallel method workers: {workers}")
    print(f"Cases: {len(resolved)}; method tasks: {total_method_tasks}")
    print()

    mp_context = multiprocessing.get_context("spawn")
    prep_payloads: List[Dict[str, object]] = []
    for spec, source_path in resolved:
        prep_payloads.append(
            {
                "spec": asdict(spec),
                "source_path": str(source_path),
                "cache_dir": str(cache_root / spec.case_id),
                "stride": args.stride,
                "chunk_rows": args.chunk_rows,
                "allow_acceleration_reconstruction": args.allow_acceleration_reconstruction,
                "event_start_override": args.event_start,
                "event_end_override": args.event_end,
            }
        )

    prep_results: Dict[str, Dict[str, object]] = {}
    phase1_started = time.perf_counter()
    print("[Phase 1/3] Reading and preparing case fields...")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=prepare_workers, mp_context=mp_context
    ) as executor:
        futures = {
            executor.submit(prepare_case_cache_worker, payload): payload
            for payload in prep_payloads
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            completed += 1
            prep_results[str(result["case_id"])] = result
            print(
                f"  [PREP {completed}/{len(futures)}] "
                f"{result['case_id']}: {result['rows_loaded']:,} rows, "
                f"{result['elapsed_seconds']:.1f} s"
            )
    phase1_elapsed = time.perf_counter() - phase1_started

    method_payloads: List[Dict[str, object]] = []
    for spec, _source_path in resolved:
        prep = prep_results[spec.case_id]
        for method_def in METHOD_DEFS:
            method_payloads.append(
                {
                    "case_id": spec.case_id,
                    "cache_dir": prep["cache_dir"],
                    "method_def": method_def,
                    "result_dir": str(
                        Path(str(prep["cache_dir"]))
                        / "method_results"
                        / str(method_def[0])
                    ),
                }
            )

    method_results: Dict[str, Dict[str, Path]] = {
        spec.case_id: {} for spec, _ in resolved
    }
    phase2_started = time.perf_counter()
    print("\n[Phase 2/3] Running QSM, QTE, and FATE in parallel...")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers, mp_context=mp_context
    ) as executor:
        futures = {
            executor.submit(run_method_cache_worker, payload): payload
            for payload in method_payloads
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            completed += 1
            case_id = str(result["case_id"])
            method_key = str(result["method_key"])
            method_results[case_id][method_key] = Path(str(result["result_dir"]))
            print(
                f"  [METHOD {completed}/{len(futures)}] "
                f"{case_id} / {result['method_name']}: "
                f"{result['elapsed_seconds']:.1f} s"
            )
    phase2_elapsed = time.perf_counter() - phase2_started

    phase3_started = time.perf_counter()
    print("\n[Phase 3/3] Writing three-stage case and complete physical observation outputs...")
    cases_root = root_out / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)
    method_frames: List[pd.DataFrame] = []
    floor_frames: List[pd.DataFrame] = []
    for index, (spec, source_path) in enumerate(resolved, start=1):
        method_df, floor_df = finalize_cached_case_v12_2(
            spec=spec,
            source_path=source_path,
            cache_dir=Path(str(prep_results[spec.case_id]["cache_dir"])),
            method_result_dirs=method_results[spec.case_id],
            case_out=cases_root / spec.case_id,
            workers=workers,
        )
        method_frames.append(method_df)
        floor_frames.append(floor_df)
        print(f"  [WRITE {index}/{len(resolved)}] {spec.case_id}")

    write_cross_case_outputs_v12_2(
        root_out,
        method_frames,
        floor_frames,
        [spec for spec, _ in resolved],
    )
    phase3_elapsed = time.perf_counter() - phase3_started

    if not args.keep_cache:
        shutil.rmtree(cache_root, ignore_errors=True)

    elapsed = time.perf_counter() - overall_started
    run_finished_utc = datetime.now(timezone.utc).isoformat()
    root_log_lines = [
        "QSM-QTE-FATE Integrated Seismic Field Observation",
        "NEES-2011-1076 Three-Stage Complete Observation Release V12.2",
        "",
        f"Run started UTC: {run_started_utc}",
        f"Run finished UTC: {run_finished_utc}",
        f"Project root: {root}",
        f"Output root: {root_out}",
        f"Logical processors detected: {cpu_count}",
        f"CSV preparation workers: {prepare_workers}",
        f"Parallel method workers: {workers}",
        f"Cases completed: {len(resolved)}",
        f"Method tasks completed: {total_method_tasks}",
        "",
        "Method order",
        "  QSM -> QTE -> FATE",
        "",
        "Wall-clock timing",
        f"  Phase 1 — data preparation: {phase1_elapsed:.3f} s",
        f"  Phase 2 — QSM/QTE/FATE methods: {phase2_elapsed:.3f} s",
        f"  Phase 3 — artifact generation: {phase3_elapsed:.3f} s",
        f"  Total release elapsed: {elapsed:.3f} s",
        "",
        "V12.2 does not generate boundary-only, fixed-path, or no-feedback sensitivity groups; the complete physical observation suite is retained.",
    ]
    if missing:
        root_log_lines += ["", "Cases skipped:"]
        root_log_lines.extend(f"  - {spec.case_id}" for spec in missing)
    (root_out / "00_RELEASE_RUN_LOG.txt").write_text(
        "\n".join(root_log_lines) + "\n", encoding="utf-8"
    )

    print("\n=== V12.2 three-stage release completed ===")
    print(f"Project root: {root}")
    print(f"Output root: {root_out}")
    print(f"Cases completed: {len(resolved)}")
    print(f"Total elapsed time: {elapsed:.1f} s")

if __name__ == "__main__":
    main_v12_2()
