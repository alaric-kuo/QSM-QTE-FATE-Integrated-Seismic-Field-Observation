#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QSM-QTE-FATE Integrated Seismic Field Observation
NEES-2011-1076 Multi-Case Formal Release V11

Purpose
-------
This release provides a reproducible four-case observation package for the
NEES-2011-1076 project:

1. El Centro 0.50 — uncontrolled
2. El Centro 0.50 — passive-off
3. Kobe 0.35 — semi-active
4. Morgan Hill 1.00 — passive-off

Method chain and scope
----------------------
QSM is used for one-step structure-coupled power-state evolution.
QTE is used for floor-domain topology-path indication at the resolution
available in the experimental records.
FATE is represented at the Aware_power observation layer.

Two observation modes are reported for every floor and every case:

    boundary-input-only diagnostic reference
    vs
    floor-state-assimilated evolution

The one-step evolved-field comparison is:

    evolved a*v at k+1|k
    vs
    measured a*v at k+1

The k+1 measurement is used after this comparison as the next field update.

Interpretation boundary
-----------------------
Acceleration is treated as a mass-normalized force proxy:

    dW/m ≈ a du = a v dt

The calibrated hit-work capacity and displacement-side work quantities are
reported as work-compatible proxy indices. Displacement is retained as
downstream response evidence.

Data provenance
---------------
Project: NEES-2011-1076
Title: RTHS and Shake Table Comparison for Smart Structural Systems
DOI: 10.7277/TPS7-V877
NSF award: CMMI-1011534 (NEESR)
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

# Each probe is parallelized as an independent process. Keep BLAS at one
# thread per worker to avoid nested oversubscription.
for _thread_env in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
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

PROJECT_METADATA = {
    "project_id": "NEES-2011-1076",
    "project_title": "RTHS and Shake Table Comparison for Smart Structural Systems",
    "doi": "10.7277/TPS7-V877",
    "nsf_award": "CMMI-1011534 (NEESR)",
    "method_chain": "QSM power-state evolution -> QTE floor-domain path indication -> FATE Aware_power observation",
}


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


# 1. Utilities
# ---------------------------------------------------------------------

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


# ---------------------------------------------------------------------



# ---------------------------------------------------------------------
# 2. Data discovery and extraction
# ---------------------------------------------------------------------

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


def read_nees_csv(path: str | Path, stride: int = 5) -> Tuple[pd.DataFrame, Dict[str, object]]:
    """Read a legacy NEES converted CSV without loading every source row.

    `stride` is applied while pandas reads the file. This matters for the two
    large El Centro exports and avoids loading hundreds of megabytes only to
    down-sample afterward.
    """
    path = Path(path)
    names, data_start = inspect_nees_header(path)
    stride = max(int(stride), 1)

    def skip_row(i: int) -> bool:
        if i < data_start:
            return True
        return ((i - data_start) % stride) != 0

    df = pd.read_csv(
        path,
        skiprows=skip_row,
        header=None,
        names=names,
        engine="python",
        on_bad_lines="skip",
    )
    df = df.dropna(axis=1, how="all")

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
        "rows_loaded": int(len(df)),
        "columns_loaded": int(len(df.columns)),
    }
    return df, metadata


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


# 3. QSM-QTE-FATE core
# ---------------------------------------------------------------------

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
    # H is real symmetric for both probes, so eigen evolution is exact and faster
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


def run_probe(
    t: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    a: np.ndarray,
    probe_key: str,
    probe_name: str,
    probe_role: str,
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
    disp_env_tau: float = 0.6,
):
    dt = float(np.nanmedian(np.diff(t)))
    n = len(t)
    psi_meas, amp, phase, omega = build_empirical_wavefunction(t, u, v, a)

    p_av = a * v
    p_av_norm = np.column_stack([robust_scale(p_av[:, i]) for i in range(3)])
    p_abs_norm = np.column_stack([robust_scale(np.abs(p_av[:, i])) for i in range(3)])
    disp_env = causal_envelope_abs(u, t, tau=disp_env_tau)
    disp_env_norm = np.column_stack([normalize_by_max(disp_env[:, i]) for i in range(3)])

    boundary_index = int(boundary_index)
    if boundary_index < 0 or boundary_index >= len(FLOORS):
        raise ValueError("boundary_index must be 0, 1, or 2")
    boundary_floor = FLOOR_SHORT[FLOORS[boundary_index]]
    if input_mode not in {"floor_state_assimilated", "boundary_input_only"}:
        raise ValueError("input_mode must be floor_state_assimilated or boundary_input_only")

    if input_mode == "boundary_input_only":
        # Boundary-input-only reference:
        # only the boundary floor injects measured power-state information.
        # Upper-floor measurements are held back until the comparison step.
        psi = np.zeros(3, dtype=complex)
        psi[boundary_index] = np.exp(1j * phase[0, boundary_index])
        psi = normalize_complex(psi)
        effective_measurement_gain = 0.0
    else:
        psi = psi_meas[0].copy()
        effective_measurement_gain = measurement_gain

    w12, w23 = normalize_path(1.0, 1.0, total_path_weight)

    psi_prior_hist = np.zeros((n, 3), dtype=complex)
    p_hit = np.zeros((n, 3), dtype=float)
    w_hit = np.zeros((n, 3), dtype=float)
    signed_p_hit = np.zeros((n, 3), dtype=float)
    evolved_av_next = np.zeros((n, 3), dtype=float)
    evolved_av_next_residual = np.zeros((n, 3), dtype=float)
    pos_hit_work = np.zeros((n, 3), dtype=float)
    neg_hit_work = np.zeros((n, 3), dtype=float)
    measured_abs_work = np.zeros((n, 3), dtype=float)
    measured_signed_work = np.zeros((n, 3), dtype=float)
    hidden_work_proxy = np.zeros((n, 3), dtype=float)

    w12_hist = np.zeros(n)
    w23_hist = np.zeros(n)
    path_dominance = np.zeros(n)
    j12_hist = np.zeros(n)
    j23_hist = np.zeros(n)
    state_fidelity = np.zeros(n)
    residual_norm = np.zeros(n)

    w12_hist[0] = w12
    w23_hist[0] = w23
    path_dominance[0] = 0.0
    state_fidelity[0] = 1.0
    psi_prior_hist[0] = psi

    for k in range(n - 1):
        _, _, H, U = build_path_operator_and_unitary(w12, w23, operator_key, dt)
        j12, j23 = edge_currents(psi, H)
        j12_hist[k] = j12
        j23_hist[k] = j23

        if input_mode == "boundary_input_only":
            sign = np.ones(3, dtype=float)
            sign_boundary = np.sign(p_av_norm[k, boundary_index])
            if sign_boundary == 0:
                sign_boundary = 1.0
            source_phase = np.zeros(3, dtype=float)
            source_amp = np.zeros(3, dtype=float)
            source_phase[boundary_index] = phase[k, boundary_index] + (sign_boundary < 0) * np.pi
            source_amp[boundary_index] = np.sqrt(abs(p_av_norm[k, boundary_index]) + 1e-12)
            source = source_amp * np.exp(1j * source_phase)
        else:
            sign = np.sign(p_av_norm[k])
            sign[sign == 0] = 1.0
            source_phase = phase[k] + (sign < 0) * np.pi
            source_amp = np.sqrt(np.abs(p_av_norm[k]) + 1e-12)
            source = source_amp * np.exp(1j * source_phase)

        psi_prior = normalize_complex(U @ (psi + source_gain * dt * source))
        psi_prior_hist[k + 1] = psi_prior
        state_fidelity[k + 1] = abs(np.vdot(psi_meas[k + 1], psi_prior)) ** 2

        fid = np.abs(psi_prior) ** 2
        if input_mode == "boundary_input_only":
            p_total = float(np.abs(p_av[k, boundary_index]))
        else:
            p_total = float(np.sum(np.abs(p_av[k])))

        # V8 one-step evolved-field check:
        # Only data up to k are used. The measured a*v at k+1 is used only
        # after the evolution comparison and then for the measurement update.
        evolved_phase = np.angle(psi_prior)
        evolved_sign = np.sign(-np.sin(2.0 * evolved_phase))
        current_sign = np.sign(p_av[k])
        current_sign[current_sign == 0] = 1.0
        evolved_sign[evolved_sign == 0] = current_sign[evolved_sign == 0]

        evolved_av_next[k + 1] = p_total * fid * evolved_sign
        evolved_av_next_residual[k + 1] = p_av[k + 1] - evolved_av_next[k + 1]

        p_hit[k + 1] = np.abs(evolved_av_next[k + 1])
        signed_p_hit[k + 1] = evolved_av_next[k + 1]

        w_hit[k + 1] = w_hit[k] + 0.5 * (p_hit[k] + p_hit[k + 1]) * dt
        pos_hit_work[k + 1] = pos_hit_work[k] + np.maximum(signed_p_hit[k + 1], 0.0) * dt
        neg_hit_work[k + 1] = neg_hit_work[k] + np.maximum(-signed_p_hit[k + 1], 0.0) * dt
        measured_abs_work[k + 1] = measured_abs_work[k] + 0.5 * (np.abs(p_av[k]) + np.abs(p_av[k + 1])) * dt
        measured_signed_work[k + 1] = measured_signed_work[k] + 0.5 * (p_av[k] + p_av[k + 1]) * dt

        current_w_max = np.maximum(np.nanmax(w_hit[: k + 2], axis=0), 1e-12)
        w_hit_norm_now = w_hit[k + 1] / current_w_max
        hidden_now = w_hit_norm_now - disp_env_norm[k + 1]
        hidden_work_proxy[k + 1] = hidden_now

        residual_full = psi_meas[k + 1] - psi_prior
        if input_mode == "boundary_input_only":
            residual = np.zeros_like(residual_full)
            residual[boundary_index] = residual_full[boundary_index]
        else:
            residual = residual_full
        residual_norm[k + 1] = float(np.linalg.norm(residual_full))
        psi = normalize_complex(psi_prior + effective_measurement_gain * residual)

        if dynamic_path_enabled:
            if input_mode == "boundary_input_only":
                # No upper-floor measurement gradients are used here.
                # Path evolution is driven by the evolved field itself.
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
            w12_new += path_current_gain * abs(j12) * dt + path_power_gain * dP12 * dt + path_residual_gain * r12 * dt + path_hidden_gain * h12 * dt
            w23_new += path_current_gain * abs(j23) * dt + path_power_gain * dP23 * dt + path_residual_gain * r23 * dt + path_hidden_gain * h23 * dt
            w12, w23 = normalize_path(w12_new, w23_new, total_path_weight)
        else:
            w12, w23 = normalize_path(1.0, 1.0, total_path_weight)

        w12_hist[k + 1] = w12
        w23_hist[k + 1] = w23
        path_dominance[k + 1] = (w12 - w23) / (w12 + w23 + 1e-12)

    return {
        "probe_key": probe_key,
        "probe_name": probe_name,
        "probe_role": probe_role,
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
        "signed_p_hit": signed_p_hit,
        "evolved_av_next": evolved_av_next,
        "evolved_av_next_residual": evolved_av_next_residual,
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


# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# 4. Summary tables
# ---------------------------------------------------------------------

def summarize_probe(result: Dict) -> Tuple[dict, pd.DataFrame]:
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
            "probe_key": result["probe_key"],
            "probe_name": result["probe_name"],
            "probe_role": result["probe_role"],
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
        "probe_key": result["probe_key"],
        "probe_name": result["probe_name"],
        "probe_role": result["probe_role"],
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


def build_core_history(main: Dict) -> pd.DataFrame:
    t = main["t"]
    capacity_scale = compute_work_capacity_scale(main)

    df = pd.DataFrame({"00_method_chain": "QSM-QTE-FATE", "01_time_s": t})
    col_no = 2
    for i, fl in enumerate(FLOORS):
        fs = FLOOR_SHORT[fl].lower()
        hit_capacity = capacity_scale * main["w_hit"][:, i]
        capacity_ref = max(float(hit_capacity[-1]), 1e-12)
        cols = {
            f"{fs}_evolved_av_next": main["evolved_av_next"][:, i],
            f"{fs}_measured_av": main["p_av"][:, i],
            f"{fs}_evolved_av_next_residual": main["evolved_av_next_residual"][:, i],
            f"{fs}_p_hit_pred": main["p_hit"][:, i],
            f"{fs}_signed_p_hit_pred": main["signed_p_hit"][:, i],
            f"{fs}_w_hit_norm": normalize_by_max(main["w_hit"][:, i]),
            f"{fs}_hit_work_capacity_norm": hit_capacity / capacity_ref,
            f"{fs}_displacement_side_work_norm": main["measured_abs_work"][:, i] / capacity_ref,
            f"{fs}_work_capacity_margin_norm": (hit_capacity - main["measured_abs_work"][:, i]) / capacity_ref,
            f"{fs}_pos_hit_work_norm": normalize_by_max(main["pos_hit_work"][:, i]),
            f"{fs}_neg_hit_work_norm": normalize_by_max(main["neg_hit_work"][:, i]),
            f"{fs}_disp_env_norm": main["disp_env_norm"][:, i],
            f"{fs}_hidden_work_proxy": main["hidden_work_proxy"][:, i],
            f"{fs}_a_times_v_measured": main["p_av"][:, i],
            f"{fs}_abs_a_times_v_measured": np.abs(main["p_av"][:, i]),
            f"{fs}_u_measured": main["u"][:, i],
            f"{fs}_measured_signed_work": main["measured_signed_work"][:, i],
        }
        for name, values in cols.items():
            df[f"{col_no:02d}_{name}"] = values
            col_no += 1
    df[f"{col_no:02d}_path_w_1f_2f"] = main["w12_hist"]; col_no += 1
    df[f"{col_no:02d}_path_w_2f_3f"] = main["w23_hist"]; col_no += 1
    df[f"{col_no:02d}_state_fidelity_one_step"] = main["state_fidelity"]; col_no += 1
    df[f"{col_no:02d}_residual_norm"] = main["residual_norm"]

    # Keep the release artifact readable on GitHub. The full-resolution numeric
    # evidence is captured in figures and summaries; this history file is a
    # compact trace for inspection, not a raw data dump.
    max_rows = 3000
    if len(df) > max_rows:
        idx = np.linspace(0, len(df) - 1, max_rows).astype(int)
        df = df.iloc[idx].reset_index(drop=True)
    return df





def build_manifestation_summary(mode_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize floor-state probes separately from diagnostic references."""
    dynamic = mode_df[mode_df["probe_role"] == "floor_state_dynamic"].copy()
    if dynamic.empty:
        raise ValueError("No floor-state dynamic probes were produced")

    path_counts = dynamic["path_manifestation"].value_counts()
    top_path = str(path_counts.index[0])
    support = int(path_counts.iloc[0])
    total = int(len(dynamic))
    edge_mean = float(dynamic["edge_current_concentration_ratio_1F_2F_over_2F_3F"].mean())

    boundary_rows = mode_df[mode_df["probe_role"] == "boundary_reference"]
    boundary = boundary_rows.iloc[0] if len(boundary_rows) else None

    return pd.DataFrame([{
        "00_method_chain": "QSM-QTE-FATE",
        "01_floor_state_energy_path_manifestation": top_path,
        "02_supporting_floor_state_dynamic_probes": support,
        "03_total_floor_state_dynamic_probes": total,
        "04_floor_state_support_fraction": support / total if total else float("nan"),
        "05_mean_floor_state_edge_current_ratio_1f2f_over_2f3f": edge_mean,
        "06_boundary_reference_path_manifestation": (
            boundary["path_manifestation"] if boundary is not None else "unavailable"
        ),
        "07_boundary_reference_final_path_dominance": (
            float(boundary["final_path_dominance_index"]) if boundary is not None else float("nan")
        ),
        "08_boundary_reference_edge_current_ratio": (
            float(boundary["edge_current_concentration_ratio_1F_2F_over_2F_3F"])
            if boundary is not None else float("nan")
        ),
        "09_boundary_reference_mean_abs_av_alignment": (
            float(boundary["mean_evolved_abs_av_next_vs_measured_abs_av_corr"])
            if boundary is not None else float("nan")
        ),
    }])


def add_integer_headers(mode_df: pd.DataFrame, target_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mode_cols = [
        "probe_key", "probe_name", "probe_role", "operator_key", "operator_name",
        "dynamic_path_enabled", "response_feedback_enabled", "path_manifestation",
        "final_w12", "final_w23", "final_path_dominance_index",
        "mean_path_dominance_index", "edge_current_rms_1F_2F",
        "edge_current_rms_2F_3F",
        "edge_current_concentration_ratio_1F_2F_over_2F_3F",
        "mean_evolved_av_next_vs_measured_av_corr",
        "mean_evolved_abs_av_next_vs_measured_abs_av_corr",
        "mean_one_step_av_evolution_residual_rmse",
        "mean_target_hit_power_alignment_corr",
        "mean_signed_hit_power_vs_signed_av_corr",
        "mean_target_hit_peak_time_offset_seconds", "work_capacity_scale",
        "mean_manifested_work_ratio", "mean_unmanifested_work_margin",
        "max_response_floor", "input_mode", "boundary_floor",
    ]
    mode_out = mode_df[mode_cols].copy()
    mode_out.columns = [f"{i+1:02d}_{c}" for i, c in enumerate(mode_cols)]
    mode_out.insert(0, "00_method_chain", "QSM-QTE-FATE")

    target_cols = [
        "probe_key", "probe_name", "probe_role", "operator_key", "operator_name",
        "dynamic_path_enabled", "response_feedback_enabled", "target_floor_no",
        "target_floor", "evolved_av_next_vs_measured_av_corr",
        "evolved_abs_av_next_vs_measured_abs_av_corr",
        "one_step_av_evolution_residual_rmse", "target_hit_power_alignment_corr",
        "signed_hit_power_vs_signed_av_corr", "target_hit_power_peak_time_seconds",
        "measured_abs_a_times_v_peak_time_seconds",
        "target_hit_power_peak_time_offset_seconds", "w_hit_final",
        "work_capacity_scale", "hit_work_capacity_final",
        "displacement_side_work_final", "manifested_work_ratio",
        "unmanifested_work_margin", "measured_abs_work_final",
        "measured_signed_work_final", "max_downstream_response_envelope",
        "downstream_response_peak_time_seconds", "hidden_work_proxy_mean",
        "input_mode", "boundary_floor",
    ]
    target_out = target_df[target_cols].copy()
    target_out.columns = [f"{i+1:02d}_{c}" for i, c in enumerate(target_cols)]
    target_out.insert(0, "00_method_chain", "QSM-QTE-FATE")
    return mode_out, target_out


def format_case_log(
    spec: CaseSpec,
    source_path: Path,
    out: Path,
    mode_df: pd.DataFrame,
    target_df: pd.DataFrame,
    manifestation_df: pd.DataFrame,
    signal_map: Dict[str, Dict[str, str]],
    event_window: Tuple[float, float],
    file_count: int,
    timing: Optional[Dict[str, object]] = None,
) -> str:
    cons = manifestation_df.iloc[0]
    main = mode_df[mode_df["probe_key"] == "laplacian_dynamic_feedback"].iloc[0]
    boundary = mode_df[mode_df["probe_key"] == "boundary_input_only_evolution"].iloc[0]
    main_target = target_df[target_df["probe_key"] == "laplacian_dynamic_feedback"]
    boundary_target = target_df[target_df["probe_key"] == "boundary_input_only_evolution"]

    lines: List[str] = [
        "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V11",
        f"Case: {spec.display_name}",
        f"Source file: {source_path.name}",
        f"Output directory: {out}",
        f"Output files: {file_count} / 20",
        f"Figure event window: {event_window[0]:.6f}–{event_window[1]:.6f} s",
        "",
        "Method scope",
        "  QSM: one-step structure-coupled power-state evolution.",
        "  QTE: floor-domain topology-path indication at the available resolution.",
        "  FATE: Aware_power observation layer only in this release.",
        "  Displacement: downstream response evidence.",
        "",
        "Floor-state path indication",
        f"  Higher-weight final path indication: {cons['01_floor_state_energy_path_manifestation']}",
        f"  Supporting floor-state dynamic probes: "
        f"{int(cons['02_supporting_floor_state_dynamic_probes'])} / "
        f"{int(cons['03_total_floor_state_dynamic_probes'])}",
        f"  Main final path-dominance index: {main['final_path_dominance_index']:.3f}",
        f"  Mean edge-current ratio 1F-2F / 2F-3F: "
        f"{cons['05_mean_floor_state_edge_current_ratio_1f2f_over_2f3f']:.3f}",
        "",
        "Boundary-input-only diagnostic reference",
        f"  Final path indication: {boundary['path_manifestation']}",
        f"  Final path-dominance index: {boundary['final_path_dominance_index']:.3f}",
        f"  Mean signed a*v correlation: "
        f"{boundary['mean_evolved_av_next_vs_measured_av_corr']:.3f}",
        f"  Mean absolute-envelope a*v correlation: "
        f"{boundary['mean_evolved_abs_av_next_vs_measured_abs_av_corr']:.3f}",
        "",
        "Floor correlation: boundary-input-only vs floor-state assimilated",
    ]

    for floor in ("1F", "2F", "3F"):
        m = main_target[main_target["target_floor"] == floor].iloc[0]
        b = boundary_target[boundary_target["target_floor"] == floor].iloc[0]
        lines.append(
            f"  {floor}: boundary signed={b['evolved_av_next_vs_measured_av_corr']:.3f}, "
            f"boundary abs={b['evolved_abs_av_next_vs_measured_abs_av_corr']:.3f}; "
            f"assimilated signed={m['evolved_av_next_vs_measured_av_corr']:.3f}, "
            f"assimilated abs={m['evolved_abs_av_next_vs_measured_abs_av_corr']:.3f}"
        )

    lines += [
        "",
        "Work-compatible proxy summary",
        f"  Work-capacity scale: {main['work_capacity_scale']:.3f}",
        f"  Mean manifested work ratio: {main['mean_manifested_work_ratio']:.3f}",
        f"  Mean unmanifested work margin: {main['mean_unmanifested_work_margin']:.3f}",
        "",
        "Selected signal provenance",
    ]
    for floor, mapping in signal_map.items():
        lines.append(f"  {floor}: u={mapping['u']}; v={mapping['v']}; a={mapping['a']}")

    if timing:
        lines += [
            "",
            "Execution timing",
            f"  Data preparation: {float(timing.get('data_preparation_seconds', 0.0)):.3f} s",
            "  Probe worker elapsed times:",
        ]
        probe_times = timing.get("probe_elapsed_seconds", {})
        if isinstance(probe_times, dict):
            for probe_key, seconds in probe_times.items():
                lines.append(f"    {probe_key}: {float(seconds):.3f} s")
        lines += [
            f"  Sum of probe worker elapsed: "
            f"{float(timing.get('probe_elapsed_sum_seconds', 0.0)):.3f} s",
            f"  Longest probe worker elapsed: "
            f"{float(timing.get('probe_elapsed_max_seconds', 0.0)):.3f} s",
            f"  Case artifact generation/finalization: "
            f"{float(timing.get('case_finalization_seconds', 0.0)):.3f} s",
            f"  Accounted case task time: "
            f"{float(timing.get('accounted_case_task_seconds', 0.0)):.3f} s",
            "  Timing note: probe worker times are process elapsed times and are not "
            "directly additive as wall-clock time because probes run in parallel.",
        ]

    return "\n".join(lines) + "\n"


# 5. Figures
# ---------------------------------------------------------------------

def make_figures(out: Path, results: List[Dict], mode_df: pd.DataFrame, target_df: pd.DataFrame, event_start: float, event_end: float, case_title: str):
    if plt is None:
        return
    by_key = {r["probe_key"]: r for r in results}
    main = by_key["laplacian_dynamic_feedback"]
    boundary = by_key.get("boundary_input_only_evolution")
    t = main["t"]
    event_mask = (t >= event_start) & (t <= event_end)

    def _thin_indices(mask_or_len, max_points: int = 900):
        if isinstance(mask_or_len, np.ndarray):
            idx = np.where(mask_or_len)[0]
        else:
            idx = np.arange(int(mask_or_len))
        if len(idx) > max_points:
            idx = idx[np.linspace(0, len(idx) - 1, max_points).astype(int)]
        return idx

    idx_event = _thin_indices(event_mask, 900)
    idx_full = _thin_indices(len(t), 1200)
    dynamic = mode_df[mode_df["probe_role"].isin(["floor_state_dynamic", "boundary_reference"])]

    # 07: final path dominance, including boundary-input-only reference.
    fig = plt.figure(figsize=(11, 5))
    x = np.arange(len(dynamic))
    plt.bar(x, dynamic["final_path_dominance_index"])
    plt.xticks(x, dynamic["probe_name"], rotation=16, ha="right")
    plt.ylabel("Final path dominance index")
    plt.title(f"QSM–QTE–FATE | {case_title}\nObserved final path indicators across field probes")
    plt.tight_layout()
    plt.savefig(out / "07_energy_path_manifestation_consensus.png", dpi=180)
    plt.close(fig)

    # 08: floor-state assimilated path evolution.
    fig = plt.figure(figsize=(10, 5))
    plt.plot(main["t"][idx_full], main["w12_hist"][idx_full], label="1F-2F path weight")
    plt.plot(main["t"][idx_full], main["w23_hist"][idx_full], label="2F-3F path weight")
    plt.xlabel("Time (s)")
    plt.ylabel("Path weight")
    plt.title(f"QSM–QTE–FATE | {case_title}\nFloor-state-assimilated path-weight evolution")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "08_floor_assimilated_path_evolution.png", dpi=180)
    plt.close(fig)

    # 09: boundary-input-only path evolution.
    if boundary is not None:
        fig = plt.figure(figsize=(10, 5))
        plt.plot(boundary["t"][idx_full], boundary["w12_hist"][idx_full], label="1F-2F path weight")
        plt.plot(boundary["t"][idx_full], boundary["w23_hist"][idx_full], label="2F-3F path weight")
        plt.xlabel("Time (s)")
        plt.ylabel("Path weight")
        plt.title(f"QSM–QTE–FATE | {case_title}\nBoundary-input-only path-weight evolution")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / "09_boundary_input_only_path_evolution.png", dpi=180)
        plt.close(fig)

    # 10: edge-current concentration across probes.
    fig = plt.figure(figsize=(11, 5))
    x = np.arange(len(mode_df))
    plt.bar(x, mode_df["edge_current_concentration_ratio_1F_2F_over_2F_3F"])
    plt.xticks(x, mode_df["probe_name"], rotation=16, ha="right")
    plt.ylabel("RMS edge-current ratio: 1F-2F / 2F-3F")
    plt.title(f"QSM–QTE–FATE | {case_title}\nQSM edge-current concentration ratio across field probes")
    plt.tight_layout()
    plt.savefig(out / "10_edge_current_concentration.png", dpi=180)
    plt.close(fig)

    # 11-13: main floor-state assimilated one-step evolved a*v check.
    for fig_no, (i, fl) in enumerate(zip(range(3), FLOORS), start=11):
        fs = FLOOR_SHORT[fl]
        fig = plt.figure(figsize=(10, 5))
        plt.axhline(0, linewidth=1)
        plt.plot(t[idx_event], normalize_by_max(main["evolved_av_next"][:, i])[idx_event], label=f"{fs} one-step evolved a*v, k+1|k")
        plt.plot(t[idx_event], normalize_by_max(main["p_av"][:, i])[idx_event], linestyle="--", label=f"{fs} measured a*v, k+1")
        plt.xlabel("Time (s)")
        plt.ylabel("Normalized signed a*v")
        plt.title(f"QSM–QTE–FATE | {case_title}\n{fs} one-step evolved-field comparison: evolved a*v and measured a*v")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / f"{fig_no:02d}_{fs.lower()}_evolved_av_next_vs_measured_av.png", dpi=180)
        plt.close(fig)

    # 14: boundary-input-only vs floor-state assimilated a*v envelope alignment.
    if boundary is not None:
        main_target = target_df[target_df["probe_key"] == "laplacian_dynamic_feedback"].sort_values("target_floor_no")
        boundary_target = target_df[target_df["probe_key"] == "boundary_input_only_evolution"].sort_values("target_floor_no")
        floors = list(main_target["target_floor"])
        x = np.arange(len(floors))
        width = 0.36
        fig = plt.figure(figsize=(10, 5))
        main_abs_vals = main_target["evolved_abs_av_next_vs_measured_abs_av_corr"].to_numpy(dtype=float)
        boundary_abs_vals = boundary_target["evolved_abs_av_next_vs_measured_abs_av_corr"].to_numpy(dtype=float)
        plt.bar(x - width/2, main_abs_vals, width, label="Floor-state assimilated")
        plt.bar(x + width/2, boundary_abs_vals, width, label="Boundary-input-only")
        plt.xticks(x, floors)
        plt.ylim(0.0, 1.05)
        plt.ylabel("Absolute-envelope correlation")
        plt.title(f"QSM–QTE–FATE | {case_title}\nObserved a*v alignment by observation mode")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / "14_boundary_vs_assimilated_av_alignment.png", dpi=180)
        plt.close(fig)

        # 15: direct path dominance time-history comparison.
        fig = plt.figure(figsize=(10, 5))
        plt.plot(main["t"][idx_full], main["path_dominance"][idx_full], label="Floor-state assimilated")
        plt.plot(boundary["t"][idx_full], boundary["path_dominance"][idx_full], linestyle="--", label="Boundary-input-only")
        plt.axhline(0, linewidth=1)
        plt.xlabel("Time (s)")
        plt.ylabel("Path dominance index")
        plt.title(f"QSM–QTE–FATE | {case_title}\nObserved path-dominance histories by observation mode")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / "15_boundary_vs_assimilated_path_dominance.png", dpi=180)
        plt.close(fig)

    # 16: compact work-compatible summary by floor.
    main_target = target_df[target_df["probe_key"] == "laplacian_dynamic_feedback"].sort_values("target_floor_no")
    floors = list(main_target["target_floor"])
    x = np.arange(len(floors))
    width = 0.36
    fig = plt.figure(figsize=(10, 5))
    manifested_vals = main_target["manifested_work_ratio"].to_numpy(dtype=float)
    margin_vals = main_target["unmanifested_work_margin"].to_numpy(dtype=float)
    plt.bar(x - width/2, manifested_vals, width, label="Manifested work ratio")
    plt.bar(x + width/2, margin_vals, width, label="Unmanifested work margin")
    plt.xticks(x, floors)
    plt.ylabel("Work-compatible ratio")
    plt.title(f"QSM–QTE–FATE | {case_title}\nWork-compatible proxy ratios by floor")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "16_work_capacity_summary_by_floor.png", dpi=180)
    plt.close(fig)

    # 17 force-displacement loop proxy.
    fig = plt.figure(figsize=(10, 5))
    for i, fl in enumerate(FLOORS):
        fs = FLOOR_SHORT[fl]
        u_norm = normalize_by_max(main["u"][:, i])
        a_norm = normalize_by_max(main["a"][:, i])
        plt.plot(u_norm[idx_event], a_norm[idx_event], label=f"{fs} a-u loop")
    plt.axhline(0.0, linewidth=1)
    plt.axvline(0.0, linewidth=1)
    plt.xlabel("Measured displacement u(t), normalized")
    plt.ylabel("Acceleration / force proxy a(t), normalized")
    plt.title(f"QSM–QTE–FATE | {case_title}\nNormalized acceleration–displacement work-loop proxy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "17_force_displacement_work_loop_proxy.png", dpi=180)
    plt.close(fig)

    # 18 response manifestation.
    vals = [float(main_target[main_target["target_floor"] == FLOOR_SHORT[fl]]["max_downstream_response_envelope"].iloc[0]) for fl in FLOORS]
    fig = plt.figure(figsize=(10, 5))
    plt.bar(np.arange(3), vals)
    plt.xticks(np.arange(3), [FLOOR_SHORT[fl] for fl in FLOORS])
    plt.ylabel("Max downstream displacement response envelope")
    plt.title(f"QSM–QTE–FATE | {case_title}\nObserved downstream displacement-response envelope by floor")
    plt.tight_layout()
    plt.savefig(out / "18_response_manifestation_by_floor.png", dpi=180)
    plt.close(fig)


# ---------------------------------------------------------------------



# ---------------------------------------------------------------------
# 6. Case and cross-case reports
# ---------------------------------------------------------------------

def write_case_report(
    out: Path,
    spec: CaseSpec,
    source_path: Path,
    manifestation_df: pd.DataFrame,
    mode_df: pd.DataFrame,
    target_df: pd.DataFrame,
    signal_map: Dict[str, Dict[str, str]],
) -> None:
    cons = manifestation_df.iloc[0]
    main = mode_df[mode_df["probe_key"] == "laplacian_dynamic_feedback"].iloc[0]
    boundary = mode_df[mode_df["probe_key"] == "boundary_input_only_evolution"].iloc[0]
    main_target = target_df[target_df["probe_key"] == "laplacian_dynamic_feedback"]
    boundary_target = target_df[target_df["probe_key"] == "boundary_input_only_evolution"]

    lines = [
        f"# {spec.display_name}",
        "",
        "## QSM–QTE–FATE Integrated Seismic Field Observation · NEES-2011-1076 V11",
        "",
        f"- Source file: `{source_path.name}`",
        f"- Earthquake input: **{spec.event_name}**",
        f"- Input scale: **{spec.input_scale}**",
        f"- Control state: **{spec.control_mode}**",
        f"- Acquisition context: **{spec.acquisition_context}**",
        "",
        "## Method position",
        "",
        "This case reports an evolutionary-field observation at the available "
        "floor-domain resolution. QSM is used for one-step structure-coupled "
        "power-state evolution; QTE is used for floor-domain path indication; "
        "FATE is represented at the Aware_power observation layer. The "
        "boundary-input-only mode is retained as a diagnostic reference.",
        "",
        "The one-step check is:",
        "",
        "```text",
        "measurements through k",
        "-> evolve field to k+1|k",
        "-> compare evolved a*v with measured a*v at k+1",
        "-> assimilate the new measurement",
        "```",
        "",
        "## Case-level path indication",
        "",
        f"- Floor-state final path indication: "
        f"**{cons['01_floor_state_energy_path_manifestation']}**",
        f"- Supporting floor-state dynamic probes: "
        f"**{int(cons['02_supporting_floor_state_dynamic_probes'])} / "
        f"{int(cons['03_total_floor_state_dynamic_probes'])}**",
        f"- Main final path dominance index: "
        f"**{main['final_path_dominance_index']:.3f}**",
        f"- Main edge-current ratio 1F-2F / 2F-3F: "
        f"**{main['edge_current_concentration_ratio_1F_2F_over_2F_3F']:.3f}**",
        "",
        "## Boundary-input-only versus floor-state assimilation",
        "",
        "| Floor | Boundary signed corr | Boundary abs corr | "
        "Assimilated signed corr | Assimilated abs corr |",
        "|---|---:|---:|---:|---:|",
    ]
    for floor in ("1F", "2F", "3F"):
        m = main_target[main_target["target_floor"] == floor].iloc[0]
        b = boundary_target[boundary_target["target_floor"] == floor].iloc[0]
        lines.append(
            f"| {floor} | {b['evolved_av_next_vs_measured_av_corr']:.3f} | "
            f"{b['evolved_abs_av_next_vs_measured_abs_av_corr']:.3f} | "
            f"{m['evolved_av_next_vs_measured_av_corr']:.3f} | "
            f"{m['evolved_abs_av_next_vs_measured_abs_av_corr']:.3f} |"
        )

    lines += [
        "",
        "## Work-compatible proxy summary",
        "",
        f"- Work-capacity scale: **{main['work_capacity_scale']:.3f}**",
        f"- Mean manifested work ratio: "
        f"**{main['mean_manifested_work_ratio']:.3f}**",
        f"- Mean unmanifested work margin: "
        f"**{main['mean_unmanifested_work_margin']:.3f}**",
        f"- Largest downstream displacement response: "
        f"**{main['max_response_floor']}**",
        "",
        "## Signal provenance",
        "",
        "| Floor | Displacement u | Velocity v | Acceleration a |",
        "|---|---|---|---|",
    ]
    for floor, mapping in signal_map.items():
        lines.append(
            f"| {floor} | `{mapping['u']}` | `{mapping['v']}` | `{mapping['a']}` |"
        )

    lines += [
        "",
        "## Data citation",
        "",
        "Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison "
        "for Smart Structural Systems (NEES-2011-1076)* [Data set]. "
        "NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.",
        "",
    ]
    (out / "05_CASE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")

    short_report = "\n".join([
        "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V11",
        f"Case: {spec.display_name}",
        f"Source: {source_path.name}",
        "",
        f"Floor-state path indication: "
        f"{cons['01_floor_state_energy_path_manifestation']}",
        f"Floor-state dynamic support: "
        f"{int(cons['02_supporting_floor_state_dynamic_probes'])}/"
        f"{int(cons['03_total_floor_state_dynamic_probes'])}",
        f"Main final path dominance: {main['final_path_dominance_index']:.6f}",
        f"Boundary final path dominance: {boundary['final_path_dominance_index']:.6f}",
        f"Main mean abs a*v alignment: "
        f"{main['mean_evolved_abs_av_next_vs_measured_abs_av_corr']:.6f}",
        f"Boundary mean abs a*v alignment: "
        f"{boundary['mean_evolved_abs_av_next_vs_measured_abs_av_corr']:.6f}",
        f"Mean manifested work ratio: {main['mean_manifested_work_ratio']:.6f}",
        f"Mean unmanifested work margin: {main['mean_unmanifested_work_margin']:.6f}",
        f"Maximum downstream response floor: {main['max_response_floor']}",
    ]) + "\n"
    (out / "06_release_report.txt").write_text(short_report, encoding="utf-8")


def build_case_summary(
    spec: CaseSpec,
    source_path: Path,
    mode_df: pd.DataFrame,
    target_df: pd.DataFrame,
) -> Dict[str, object]:
    main = mode_df[mode_df["probe_key"] == "laplacian_dynamic_feedback"].iloc[0]
    boundary = mode_df[mode_df["probe_key"] == "boundary_input_only_evolution"].iloc[0]
    return {
        "case_id": spec.case_id,
        "case_name": spec.display_name,
        "event_name": spec.event_name,
        "input_scale": spec.input_scale,
        "control_mode": spec.control_mode,
        "source_file": source_path.name,
        "floor_state_path_manifestation": main["path_manifestation"],
        "floor_state_final_path_dominance": float(main["final_path_dominance_index"]),
        "floor_state_edge_current_ratio": float(
            main["edge_current_concentration_ratio_1F_2F_over_2F_3F"]
        ),
        "floor_state_mean_signed_av_corr": float(
            main["mean_evolved_av_next_vs_measured_av_corr"]
        ),
        "floor_state_mean_abs_av_corr": float(
            main["mean_evolved_abs_av_next_vs_measured_abs_av_corr"]
        ),
        "boundary_path_manifestation": boundary["path_manifestation"],
        "boundary_final_path_dominance": float(boundary["final_path_dominance_index"]),
        "boundary_edge_current_ratio": float(
            boundary["edge_current_concentration_ratio_1F_2F_over_2F_3F"]
        ),
        "boundary_mean_signed_av_corr": float(
            boundary["mean_evolved_av_next_vs_measured_av_corr"]
        ),
        "boundary_mean_abs_av_corr": float(
            boundary["mean_evolved_abs_av_next_vs_measured_abs_av_corr"]
        ),
        "abs_corr_gain_from_floor_assimilation": float(
            main["mean_evolved_abs_av_next_vs_measured_abs_av_corr"]
            - boundary["mean_evolved_abs_av_next_vs_measured_abs_av_corr"]
        ),
        "signed_corr_gain_from_floor_assimilation": float(
            main["mean_evolved_av_next_vs_measured_av_corr"]
            - boundary["mean_evolved_av_next_vs_measured_av_corr"]
        ),
        "work_capacity_scale": float(main["work_capacity_scale"]),
        "mean_manifested_work_ratio": float(main["mean_manifested_work_ratio"]),
        "mean_unmanifested_work_margin": float(main["mean_unmanifested_work_margin"]),
        "max_response_floor": main["max_response_floor"],
    }


def build_floor_method_rows(
    spec: CaseSpec,
    target_df: pd.DataFrame,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    method_map = {
        "laplacian_dynamic_feedback": "floor_state_assimilated",
        "boundary_input_only_evolution": "boundary_input_only",
    }
    for probe_key, method in method_map.items():
        part = target_df[target_df["probe_key"] == probe_key]
        for _, row in part.iterrows():
            rows.append({
                "case_id": spec.case_id,
                "case_name": spec.display_name,
                "event_name": spec.event_name,
                "control_mode": spec.control_mode,
                "method": method,
                "floor": row["target_floor"],
                "signed_av_correlation": float(
                    row["evolved_av_next_vs_measured_av_corr"]
                ),
                "absolute_envelope_av_correlation": float(
                    row["evolved_abs_av_next_vs_measured_abs_av_corr"]
                ),
                "one_step_residual_rmse": float(
                    row["one_step_av_evolution_residual_rmse"]
                ),
                "main_window_timing_offset_s": float(
                    row["target_hit_power_peak_time_offset_seconds"]
                ),
                "manifested_work_ratio": float(row["manifested_work_ratio"]),
                "unmanifested_work_margin": float(row["unmanifested_work_margin"]),
                "max_downstream_response_envelope": float(
                    row["max_downstream_response_envelope"]
                ),
            })
    return rows


def make_cross_case_figures(
    out: Path,
    summary_df: pd.DataFrame,
    floor_df: pd.DataFrame,
) -> None:
    if plt is None or summary_df.empty:
        return

    labels = summary_df["case_name"].tolist()
    x = np.arange(len(labels))
    width = 0.36

    fig = plt.figure(figsize=(12, 6))
    plt.bar(
        x - width / 2,
        summary_df["boundary_mean_abs_av_corr"],
        width,
        label="Boundary-input-only",
    )
    plt.bar(
        x + width / 2,
        summary_df["floor_state_mean_abs_av_corr"],
        width,
        label="Floor-state assimilated",
    )
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylim(-0.05, 1.05)
    plt.ylabel("Mean absolute-envelope correlation")
    plt.title("QSM–QTE–FATE | Cross-case a*v alignment by observation mode")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "05_cross_case_mean_abs_correlation.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 6))
    for method, linestyle in (
        ("boundary_input_only", "--"),
        ("floor_state_assimilated", "-"),
    ):
        part = floor_df[floor_df["method"] == method]
        means = (
            part.groupby("floor")["absolute_envelope_av_correlation"]
            .mean()
            .reindex(["1F", "2F", "3F"])
        )
        plt.plot(
            ["1F", "2F", "3F"],
            means.to_numpy(dtype=float),
            marker="o",
            linestyle=linestyle,
            label=method.replace("_", " "),
        )
    plt.ylim(-0.05, 1.05)
    plt.ylabel("Mean absolute-envelope correlation across cases")
    plt.title("QSM–QTE–FATE | Cross-case floor-wise a*v alignment")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "06_cross_case_floor_abs_correlation.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 6))
    plt.bar(
        x - width / 2,
        summary_df["boundary_final_path_dominance"],
        width,
        label="Boundary-input-only",
    )
    plt.bar(
        x + width / 2,
        summary_df["floor_state_final_path_dominance"],
        width,
        label="Floor-state assimilated",
    )
    plt.axhline(0.0, linewidth=1)
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Final path dominance index")
    plt.title("QSM–QTE–FATE | Cross-case final path indicators")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "07_cross_case_path_dominance.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 6))
    plt.bar(x, summary_df["floor_state_edge_current_ratio"])
    plt.axhline(1.0, linewidth=1, linestyle="--")
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Edge-current ratio 1F-2F / 2F-3F")
    plt.title("QSM–QTE–FATE | Cross-case floor-state edge-current ratios")
    plt.tight_layout()
    plt.savefig(out / "08_cross_case_edge_current_ratio.png", dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 6))
    plt.bar(
        x - width / 2,
        summary_df["mean_manifested_work_ratio"],
        width,
        label="Manifested work ratio",
    )
    plt.bar(
        x + width / 2,
        summary_df["mean_unmanifested_work_margin"],
        width,
        label="Unmanifested work margin",
    )
    plt.xticks(x, labels, rotation=15, ha="right")
    plt.ylabel("Work-compatible ratio")
    plt.title("QSM–QTE–FATE | Cross-case work-compatible proxy ratios")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "09_cross_case_work_manifestation.png", dpi=180)
    plt.close(fig)


def write_cross_case_report(
    out: Path,
    summary_df: pd.DataFrame,
    floor_df: pd.DataFrame,
) -> None:
    lines = [
        "# QSM–QTE–FATE Integrated Seismic Field Observation",
        "",
        "## NEES-2011-1076 four-case comparison · Release V11",
        "",
        "This package compares four records from the same three-story steel-frame "
        "project. It is reported as a partial cross-wave and cross-control "
        "observation matrix rather than as a balanced factorial experiment.",
        "",
        "## Cases",
        "",
        "| Case | Event | Scale | Control mode | Source file |",
        "|---|---|---:|---|---|",
    ]
    for _, row in summary_df.iterrows():
        lines.append(
            f"| {row['case_name']} | {row['event_name']} | {row['input_scale']} | "
            f"{row['control_mode']} | `{row['source_file']}` |"
        )

    lines += [
        "",
        "## Main comparison",
        "",
        "| Case | Boundary abs corr | Assimilated abs corr | Gain | "
        "Boundary dominance | Assimilated dominance | Manifested path |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in summary_df.iterrows():
        lines.append(
            f"| {row['case_name']} | {row['boundary_mean_abs_av_corr']:.3f} | "
            f"{row['floor_state_mean_abs_av_corr']:.3f} | "
            f"{row['abs_corr_gain_from_floor_assimilation']:.3f} | "
            f"{row['boundary_final_path_dominance']:.3f} | "
            f"{row['floor_state_final_path_dominance']:.3f} | "
            f"{row['floor_state_path_manifestation']} |"
        )

    lines += [
        "",
        "## Interpretation boundary",
        "",
        "The four cases can test whether the distinction between incoming boundary "
        "information and the structure-coupled power-state field repeats across "
        "different records and control states. Only the El Centro uncontrolled / "
        "passive-off pair holds the earthquake input and scale approximately fixed; "
        "the full four-case set should therefore be interpreted as a robustness "
        "comparison rather than a complete causal control experiment.",
        "",
        "## Data citation",
        "",
        "Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison "
        "for Smart Structural Systems (NEES-2011-1076)* [Data set]. "
        "NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.",
        "",
    ]
    (out / "10_CROSS_CASE_REPORT.md").write_text("\n".join(lines), encoding="utf-8")



# ---------------------------------------------------------------------
# 7. Four-case execution
# ---------------------------------------------------------------------

PROBE_DEFS = (
    (
        "laplacian_dynamic_feedback",
        "Laplacian floor-state field probe",
        "floor_state_dynamic",
        "laplacian",
        "Laplacian field",
        True,
        True,
        "floor_state_assimilated",
    ),
    (
        "zero_diagonal_dynamic_feedback",
        "Zero-diagonal floor-state field probe",
        "floor_state_dynamic",
        "zero_diagonal",
        "Strict zero-diagonal field",
        True,
        True,
        "floor_state_assimilated",
    ),
    (
        "boundary_input_only_evolution",
        "Boundary-input-only diagnostic reference",
        "boundary_reference",
        "laplacian",
        "Laplacian field",
        True,
        False,
        "boundary_input_only",
    ),
    (
        "dynamic_path_no_response_feedback",
        "Floor-state dynamic path without response feedback",
        "floor_state_dynamic",
        "laplacian",
        "Laplacian field",
        True,
        False,
        "floor_state_assimilated",
    ),
    (
        "fixed_path_reference",
        "Fixed-path reference",
        "fixed_reference",
        "laplacian",
        "Fixed-path reference",
        False,
        False,
        "floor_state_assimilated",
    ),
)


def run_case(
    spec: CaseSpec,
    source_path: Path,
    case_out: Path,
    stride: int,
    allow_acceleration_reconstruction: bool,
    event_start_override: Optional[float],
    event_end_override: Optional[float],
) -> Tuple[Dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print(f"\n=== {spec.display_name} ===")
    print(f"Source: {source_path}")

    if case_out.exists():
        shutil.rmtree(case_out)
    case_out.mkdir(parents=True, exist_ok=True)

    _UNITARY_CACHE.clear()
    df, read_metadata = read_nees_csv(source_path, stride=stride)
    t, u, v, a, signal_map = extract_floor_arrays(
        df,
        allow_acceleration_reconstruction=allow_acceleration_reconstruction,
    )

    auto_start, auto_end = detect_event_window(t, a)
    event_start = (
        float(event_start_override)
        if event_start_override is not None
        else auto_start
    )
    event_end = (
        float(event_end_override)
        if event_end_override is not None
        else auto_end
    )
    if event_end <= event_start:
        raise ValueError("event-end must be greater than event-start")

    results: List[Dict] = []
    mode_rows: List[Dict] = []
    target_frames: List[pd.DataFrame] = []

    for (
        probe_key,
        probe_name,
        probe_role,
        operator_key,
        operator_name,
        dynamic_path_enabled,
        response_feedback_enabled,
        input_mode,
    ) in PROBE_DEFS:
        print(f"Running: {probe_name}")
        result = run_probe(
            t,
            u,
            v,
            a,
            probe_key=probe_key,
            probe_name=probe_name,
            probe_role=probe_role,
            operator_key=operator_key,
            operator_name=operator_name,
            dynamic_path_enabled=dynamic_path_enabled,
            response_feedback_enabled=response_feedback_enabled,
            input_mode=input_mode,
            boundary_index=0,
        )
        mode, target = summarize_probe(result)
        results.append(result)
        mode_rows.append(mode)
        target_frames.append(target)

    mode_df = pd.DataFrame(mode_rows)
    target_df = pd.concat(target_frames, ignore_index=True)
    manifestation_df = build_manifestation_summary(mode_df)

    mode_out, target_out = add_integer_headers(mode_df, target_df)
    core_out = build_core_history(results[0])

    mode_out.to_csv(case_out / "01_qsm_qte_fate_mode_comparison.csv", index=False)
    manifestation_df.to_csv(
        case_out / "02_qsm_qte_fate_manifestation_summary.csv",
        index=False,
    )
    target_out.to_csv(case_out / "03_qsm_qte_fate_floor_target_summary.csv", index=False)
    core_out.to_csv(case_out / "04_qsm_qte_fate_core_history.csv", index=False)

    write_case_report(
        case_out,
        spec,
        source_path,
        manifestation_df,
        mode_df,
        target_df,
        signal_map,
    )
    make_figures(
        case_out,
        results,
        mode_df,
        target_df,
        event_start,
        event_end,
        case_title=spec.display_name,
    )

    log_path = case_out / "19_release_run_log.txt"
    initial_log = format_case_log(
        spec,
        source_path,
        case_out,
        mode_df,
        target_df,
        manifestation_df,
        signal_map,
        (event_start, event_end),
        file_count=20,
    )
    log_path.write_text(initial_log, encoding="utf-8")

    manifest = {
        "release": "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V11",
        "case": asdict(spec),
        "project": PROJECT_METADATA,
        "source_read_metadata": read_metadata,
        "signal_provenance": signal_map,
        "event_window_seconds": {
            "start": event_start,
            "end": event_end,
            "selection": (
                "CLI override"
                if event_start_override is not None or event_end_override is not None
                else "automatic cumulative acceleration-state activity window"
            ),
        },
        "method_position": (
            "exploratory evolutionary-field observation at floor-domain resolution"
        ),
        "two_observation_modes": [
            "boundary-input-only diagnostic reference",
            "floor-state-assimilated structure-coupled field evolution",
        ],
        "one_step_evolved_field_check": (
            "evolved a*v at k+1|k is compared with measured a*v at k+1"
        ),
        "qsm_qte_fate_order": (
            "QSM power-state evolution -> QTE floor-domain path indication -> "
            "FATE Aware_power observation"
        ),
        "displacement_role": (
            "downstream response evidence, not primary state variable"
        ),
        "output_files": sorted(
            [p.name for p in case_out.iterdir() if p.is_file()]
            + ["20_release_file_manifest.json"]
        ),
    }
    (case_out / "20_release_file_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    final_count = len([p for p in case_out.iterdir() if p.is_file()])
    final_log = format_case_log(
        spec,
        source_path,
        case_out,
        mode_df,
        target_df,
        manifestation_df,
        signal_map,
        (event_start, event_end),
        file_count=final_count,
    )
    log_path.write_text(final_log, encoding="utf-8")
    print(final_log)

    case_summary = build_case_summary(spec, source_path, mode_df, target_df)
    case_summary["event_window_start_s"] = event_start
    case_summary["event_window_end_s"] = event_end
    case_summary["rows_loaded_after_stride"] = read_metadata["rows_loaded"]
    case_summary["read_stride"] = read_metadata["read_stride"]

    floor_rows = pd.DataFrame(build_floor_method_rows(spec, target_df))
    probe_df = mode_df.copy()
    probe_df.insert(0, "case_id", spec.case_id)
    probe_df.insert(1, "case_name", spec.display_name)
    return case_summary, floor_rows, probe_df, target_df


def write_cross_case_outputs(
    root_out: Path,
    case_summaries: List[Dict[str, object]],
    floor_frames: List[pd.DataFrame],
    probe_frames: List[pd.DataFrame],
    selected_specs: Sequence[CaseSpec],
) -> None:
    cross_out = root_out / "00_cross_case"
    cross_out.mkdir(parents=True, exist_ok=True)

    summary_df = pd.DataFrame(case_summaries)
    floor_df = pd.concat(floor_frames, ignore_index=True)
    probe_df = pd.concat(probe_frames, ignore_index=True)
    if "method_chain" not in summary_df.columns:
        summary_df.insert(0, "method_chain", "QSM-QTE-FATE")
    if "method_chain" not in floor_df.columns:
        floor_df.insert(0, "method_chain", "QSM-QTE-FATE")
    if "method_chain" not in probe_df.columns:
        probe_df.insert(0, "method_chain", "QSM-QTE-FATE")

    summary_df.to_csv(cross_out / "01_cross_case_summary.csv", index=False)
    floor_df.to_csv(
        cross_out / "02_cross_case_floor_method_correlation.csv",
        index=False,
    )
    probe_df.to_csv(cross_out / "03_cross_case_probe_comparison.csv", index=False)

    registry = {
        "release": "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V11",
        "project": PROJECT_METADATA,
        "cases": [asdict(spec) for spec in selected_specs],
        "comparison_scope": (
            "partial cross-wave and cross-control robustness matrix; "
            "El Centro uncontrolled/passive-off is the closest paired comparison"
        ),
    }
    (cross_out / "04_case_registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    make_cross_case_figures(cross_out, summary_df, floor_df)
    write_cross_case_report(cross_out, summary_df, floor_df)

    manifest = {
        "release": registry["release"],
        "project": PROJECT_METADATA,
        "case_count": int(len(summary_df)),
        "case_ids": summary_df["case_id"].tolist(),
        "output_files": sorted(
            [p.name for p in cross_out.iterdir() if p.is_file()]
            + ["11_cross_case_file_manifest.json"]
        ),
    }
    (cross_out / "11_cross_case_file_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the four-case QSM-QTE-FATE Integrated Seismic Field Observation package "
            "for NEES-2011-1076"
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Folder containing the four converted NEES CSV files",
    )
    parser.add_argument(
        "--out",
        default="outputs_qsm_qte_fate_nees_2011_1076_v11",
        help="Root output folder",
    )
    parser.add_argument(
        "--cases",
        nargs="*",
        choices=[spec.case_id for spec in CASE_SPECS],
        help="Optional subset of case IDs; default runs all four",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=5,
        help="Read every Nth source data row; default 5",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Run available cases instead of failing when a source file is missing",
    )
    parser.add_argument(
        "--allow-acceleration-reconstruction",
        action="store_true",
        help=(
            "Allow baseline-corrected integration when a floor lacks direct "
            "displacement/velocity. Reconstructed a*v must be reported as such."
        ),
    )
    parser.add_argument(
        "--event-start",
        type=float,
        default=None,
        help="Optional shared figure-window start time; default auto-detected per case",
    )
    parser.add_argument(
        "--event-end",
        type=float,
        default=None,
        help="Optional shared figure-window end time; default auto-detected per case",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Do not clear the root output folder before running",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if plt is None:
        raise RuntimeError("matplotlib is required to create the 20-file case releases")

    root = Path(args.root).expanduser().resolve()
    root_out = Path(args.out).expanduser()
    if not root_out.is_absolute():
        root_out = root / root_out
    root_out = root_out.resolve()

    if root_out.exists() and not args.keep_output:
        shutil.rmtree(root_out)
    root_out.mkdir(parents=True, exist_ok=True)

    selected_ids = set(args.cases or [spec.case_id for spec in CASE_SPECS])
    selected_specs = [spec for spec in CASE_SPECS if spec.case_id in selected_ids]

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
            "Use --allow-missing to run only the files currently available."
        )
    if not resolved:
        raise FileNotFoundError(f"No configured case files found under {root}")

    case_summaries: List[Dict[str, object]] = []
    floor_frames: List[pd.DataFrame] = []
    probe_frames: List[pd.DataFrame] = []

    cases_root = root_out / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)

    for spec, source_path in resolved:
        case_out = cases_root / spec.case_id
        case_summary, floor_df, probe_df, _ = run_case(
            spec=spec,
            source_path=source_path,
            case_out=case_out,
            stride=args.stride,
            allow_acceleration_reconstruction=args.allow_acceleration_reconstruction,
            event_start_override=args.event_start,
            event_end_override=args.event_end,
        )
        case_summaries.append(case_summary)
        floor_frames.append(floor_df)
        probe_frames.append(probe_df)

    write_cross_case_outputs(
        root_out,
        case_summaries,
        floor_frames,
        probe_frames,
        [spec for spec, _ in resolved],
    )

    print("\n=== Multi-case release completed ===")
    print(f"Project root: {root}")
    print(f"Output root: {root_out}")
    print(f"Cases completed: {len(resolved)}")
    for spec, _ in resolved:
        print(f"  - {spec.case_id}")
    if missing:
        print("Cases skipped:")
        for spec in missing:
            print(f"  - {spec.case_id}")

# ---------------------------------------------------------------------
# V11 optimized execution engine
# ---------------------------------------------------------------------


def _v11_select_read_columns(names: Sequence[str]) -> List[str]:
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
    """V11 high-throughput NEES CSV reader.

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
    usecols = _v11_select_read_columns(names)

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


def _v11_cumulative_work(p_av: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
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
    """Build field-observation arrays once per case, not once per probe."""
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
    measured_abs_work, measured_signed_work = _v11_cumulative_work(p_av, dt)
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


def run_probe_prepared(
    prepared: Dict[str, np.ndarray | float],
    probe_key: str,
    probe_name: str,
    probe_role: str,
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
    """V11 O(n) probe engine using precomputed case features.

    The V9 historical maximum scan was O(n^2). Since cumulative hit-work is
    monotonic, V11 keeps a three-value running maximum, preserving the numerical
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
        "probe_key": probe_key,
        "probe_name": probe_name,
        "probe_role": probe_role,
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


def _v11_save_arrays(folder: Path, arrays: Dict[str, np.ndarray]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, value in arrays.items():
        np.save(folder / f"{name}.npy", np.asarray(value), allow_pickle=False)


def _v11_load_arrays(folder: Path, names: Sequence[str]) -> Dict[str, np.ndarray]:
    return {
        name: np.load(folder / f"{name}.npy", mmap_mode="r")
        for name in names
    }


V11_PREPARED_ARRAY_NAMES: Tuple[str, ...] = (
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

V11_PROBE_ARRAY_NAMES: Tuple[str, ...] = (
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


def _v11_spec_from_dict(data: Dict[str, object]) -> CaseSpec:
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
    spec = _v11_spec_from_dict(dict(payload["spec"]))
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
        for name in V11_PREPARED_ARRAY_NAMES
    }
    _v11_save_arrays(cache_dir / "arrays", array_payload)

    metadata = {
        "release": "QSM-QTE-FATE Integrated Seismic Field Observation — NEES-2011-1076 V11",
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


def run_probe_cache_worker(payload: Dict[str, object]) -> Dict[str, object]:
    started = time.perf_counter()
    cache_dir = Path(str(payload["cache_dir"]))
    result_dir = Path(str(payload["result_dir"]))
    probe_def = tuple(payload["probe_def"])
    if result_dir.exists():
        shutil.rmtree(result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    prepared_arrays = _v11_load_arrays(
        cache_dir / "arrays", V11_PREPARED_ARRAY_NAMES
    )
    meta = json.loads((cache_dir / "case_metadata.json").read_text(encoding="utf-8"))
    prepared: Dict[str, np.ndarray | float] = dict(prepared_arrays)
    prepared["dt"] = float(meta["dt"])

    (
        probe_key,
        probe_name,
        probe_role,
        operator_key,
        operator_name,
        dynamic_path_enabled,
        response_feedback_enabled,
        input_mode,
    ) = probe_def
    _UNITARY_CACHE.clear()
    result = run_probe_prepared(
        prepared,
        probe_key=str(probe_key),
        probe_name=str(probe_name),
        probe_role=str(probe_role),
        operator_key=str(operator_key),
        operator_name=str(operator_name),
        dynamic_path_enabled=bool(dynamic_path_enabled),
        response_feedback_enabled=bool(response_feedback_enabled),
        input_mode=str(input_mode),
        boundary_index=0,
    )
    _v11_save_arrays(
        result_dir,
        {name: np.asarray(result[name]) for name in V11_PROBE_ARRAY_NAMES},
    )
    result_meta = {
        "probe_key": result["probe_key"],
        "probe_name": result["probe_name"],
        "probe_role": result["probe_role"],
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
        "probe_key": str(probe_key),
        "probe_name": str(probe_name),
        "result_dir": str(result_dir),
        "elapsed_seconds": float(result_meta["elapsed_seconds"]),
    }


def load_cached_probe_result(cache_dir: Path, result_dir: Path) -> Dict[str, object]:
    prepared = _v11_load_arrays(cache_dir / "arrays", V11_PREPARED_ARRAY_NAMES)
    arrays = _v11_load_arrays(result_dir, V11_PROBE_ARRAY_NAMES)
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


def finalize_cached_case_v11(
    spec: CaseSpec,
    source_path: Path,
    cache_dir: Path,
    probe_result_dirs: Dict[str, Path],
    case_out: Path,
    workers: int,
) -> Tuple[Dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    finalization_started = time.perf_counter()
    if case_out.exists():
        shutil.rmtree(case_out)
    case_out.mkdir(parents=True, exist_ok=True)

    cache_meta = json.loads(
        (cache_dir / "case_metadata.json").read_text(encoding="utf-8")
    )
    results: List[Dict[str, object]] = []
    mode_rows: List[Dict[str, object]] = []
    target_frames: List[pd.DataFrame] = []
    probe_elapsed: Dict[str, float] = {}

    for probe_def in PROBE_DEFS:
        probe_key = probe_def[0]
        result = load_cached_probe_result(
            cache_dir, probe_result_dirs[probe_key]
        )
        probe_elapsed[str(probe_key)] = float(result.get("elapsed_seconds", 0.0))
        mode, target = summarize_probe(result)
        results.append(result)
        mode_rows.append(mode)
        target_frames.append(target)

    mode_df = pd.DataFrame(mode_rows)
    target_df = pd.concat(target_frames, ignore_index=True)
    manifestation_df = build_manifestation_summary(mode_df)
    mode_out, target_out = add_integer_headers(mode_df, target_df)
    core_out = build_core_history(results[0])

    mode_out.to_csv(
        case_out / "01_qsm_qte_fate_mode_comparison.csv", index=False
    )
    manifestation_df.to_csv(
        case_out / "02_qsm_qte_fate_manifestation_summary.csv", index=False
    )
    target_out.to_csv(
        case_out / "03_qsm_qte_fate_floor_target_summary.csv", index=False
    )
    core_out.to_csv(
        case_out / "04_qsm_qte_fate_core_history.csv", index=False
    )

    signal_map = cache_meta["signal_map"]
    event_start = float(cache_meta["event_start"])
    event_end = float(cache_meta["event_end"])
    write_case_report(
        case_out,
        spec,
        source_path,
        manifestation_df,
        mode_df,
        target_df,
        signal_map,
    )
    make_figures(
        case_out,
        results,
        mode_df,
        target_df,
        event_start,
        event_end,
        case_title=spec.display_name,
    )

    prep_seconds = float(cache_meta.get("elapsed_seconds", 0.0))
    probe_sum = float(sum(probe_elapsed.values()))
    probe_max = float(max(probe_elapsed.values(), default=0.0))
    artifact_generation_seconds = time.perf_counter() - finalization_started

    timing: Dict[str, object] = {
        "data_preparation_seconds": prep_seconds,
        "probe_elapsed_seconds": probe_elapsed,
        "probe_elapsed_sum_seconds": probe_sum,
        "probe_elapsed_max_seconds": probe_max,
        "case_finalization_seconds": artifact_generation_seconds,
        "accounted_case_task_seconds": (
            prep_seconds + probe_sum + artifact_generation_seconds
        ),
        "timing_interpretation": (
            "Probe elapsed values are worker-process times. Because probes run "
            "in parallel, their sum is a compute-load indicator rather than "
            "case wall-clock time."
        ),
    }

    performance_lines = [
        "",
        "V11 performance engine",
        f"  Parallel probe workers: {workers}",
        "  CSV parser: pandas C engine, chunked and column-selected",
        "  Field features: computed once per case and shared by memory map",
        "  Probe loop: O(n) running work maximum",
    ]

    manifest = {
        "release": (
            "QSM-QTE-FATE Integrated Seismic Field Observation "
            "— NEES-2011-1076 V11"
        ),
        "case": asdict(spec),
        "project": PROJECT_METADATA,
        "source_read_metadata": cache_meta["read_metadata"],
        "signal_provenance": signal_map,
        "event_window_seconds": {
            "start": event_start,
            "end": event_end,
            "selection": cache_meta["event_selection"],
        },
        "method_scope": {
            "QSM": "one-step structure-coupled power-state evolution",
            "QTE": (
                "floor-domain topology-path indication at the available "
                "experimental resolution"
            ),
            "FATE": "Aware_power observation layer only",
        },
        "performance_engine": {
            "parallel_probe_workers": workers,
            "csv_reader": (
                "C engine + chunked vector stride + selected columns"
            ),
            "feature_reuse": (
                "computed once per case, memory-mapped across probes"
            ),
            "time_complexity": "O(n) running work maximum",
            "blas_threads_per_worker": 1,
        },
        "execution_timing": timing,
        "two_observation_modes": [
            "boundary-input-only diagnostic reference",
            "floor-state-assimilated structure-coupled field evolution",
        ],
        "one_step_evolved_field_check": (
            "evolved a*v at k+1|k is compared with measured a*v at k+1"
        ),
        "method_chain_order": (
            "QSM power-state evolution -> QTE floor-domain path indication "
            "-> FATE Aware_power observation"
        ),
        "displacement_role": "downstream response evidence",
        "output_files": [],
    }

    log_path = case_out / "19_release_run_log.txt"
    manifest_path = case_out / "20_release_file_manifest.json"

    # First write creates the complete 20-file release, then timing is updated
    # once more to include the final log and manifest writes.
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    preliminary_log = format_case_log(
        spec,
        source_path,
        case_out,
        mode_df,
        target_df,
        manifestation_df,
        signal_map,
        (event_start, event_end),
        file_count=20,
        timing=timing,
    )
    log_path.write_text(
        preliminary_log + "\n".join(performance_lines) + "\n",
        encoding="utf-8",
    )

    finalization_seconds = time.perf_counter() - finalization_started
    timing["case_finalization_seconds"] = finalization_seconds
    timing["accounted_case_task_seconds"] = (
        prep_seconds + probe_sum + finalization_seconds
    )
    final_files = sorted(p.name for p in case_out.iterdir() if p.is_file())
    manifest["execution_timing"] = timing
    manifest["output_files"] = final_files
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    final_log = format_case_log(
        spec,
        source_path,
        case_out,
        mode_df,
        target_df,
        manifestation_df,
        signal_map,
        (event_start, event_end),
        file_count=len(final_files),
        timing=timing,
    )
    log_path.write_text(
        final_log + "\n".join(performance_lines) + "\n",
        encoding="utf-8",
    )

    case_summary = build_case_summary(spec, source_path, mode_df, target_df)
    case_summary["method_chain"] = "QSM-QTE-FATE"
    case_summary["event_window_start_s"] = event_start
    case_summary["event_window_end_s"] = event_end
    case_summary["rows_loaded_after_stride"] = cache_meta["read_metadata"][
        "rows_loaded"
    ]
    case_summary["read_stride"] = cache_meta["read_metadata"]["read_stride"]
    case_summary["data_preparation_seconds"] = prep_seconds
    case_summary["probe_elapsed_sum_seconds"] = probe_sum
    case_summary["case_finalization_seconds"] = finalization_seconds

    floor_rows = pd.DataFrame(build_floor_method_rows(spec, target_df))
    floor_rows.insert(0, "method_chain", "QSM-QTE-FATE")
    probe_df = mode_df.copy()
    probe_df.insert(0, "method_chain", "QSM-QTE-FATE")
    probe_df.insert(1, "case_id", spec.case_id)
    probe_df.insert(2, "case_name", spec.display_name)
    return case_summary, floor_rows, probe_df, target_df


def parse_args_v11() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "V11 formal multi-core QSM-QTE-FATE Integrated Seismic Field Observation "
            "for NEES-2011-1076"
        )
    )
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--out", default="outputs_qsm_qte_fate_nees_2011_1076_v11"
    )
    parser.add_argument(
        "--cases",
        nargs="*",
        choices=[spec.case_id for spec in CASE_SPECS],
        help="Optional subset of case IDs; default runs all four",
    )
    parser.add_argument("--stride", type=int, default=5)
    parser.add_argument(
        "--chunk-rows",
        type=int,
        default=200_000,
        help="CSV rows parsed per chunk; default 200000",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Parallel probe processes; 0 selects an automatic value up to 8",
    )
    parser.add_argument(
        "--prepare-workers",
        type=int,
        default=2,
        help="Parallel CSV preparation processes; default 2",
    )
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument(
        "--allow-acceleration-reconstruction", action="store_true"
    )
    parser.add_argument("--event-start", type=float, default=None)
    parser.add_argument("--event-end", type=float, default=None)
    parser.add_argument("--keep-output", action="store_true")
    parser.add_argument(
        "--keep-cache",
        action="store_true",
        help="Keep temporary memory-map arrays and probe results",
    )
    return parser.parse_args()


def main_v11() -> None:
    multiprocessing.freeze_support()
    args = parse_args_v11()
    if plt is None:
        raise RuntimeError("matplotlib is required for the V11 release")

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
    cache_root = root_out / "_v11_cache"
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
    total_probe_tasks = len(resolved) * len(PROBE_DEFS)
    workers = int(args.workers)
    if workers <= 0:
        workers = min(8, max(2, cpu_count - 2), total_probe_tasks)
    workers = max(1, min(workers, total_probe_tasks))
    prepare_workers = max(
        1, min(int(args.prepare_workers), len(resolved), cpu_count)
    )

    print("=== QSM-QTE-FATE Integrated Seismic Field Observation V11 ===")
    print(f"Logical processors detected: {cpu_count}")
    print(f"CSV preparation workers: {prepare_workers}")
    print(f"Parallel probe workers: {workers}")
    print(f"Cases: {len(resolved)}; probe tasks: {total_probe_tasks}")
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
                "allow_acceleration_reconstruction": (
                    args.allow_acceleration_reconstruction
                ),
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

    probe_payloads: List[Dict[str, object]] = []
    for spec, _source_path in resolved:
        prep = prep_results[spec.case_id]
        for probe_def in PROBE_DEFS:
            probe_payloads.append(
                {
                    "case_id": spec.case_id,
                    "cache_dir": prep["cache_dir"],
                    "probe_def": probe_def,
                    "result_dir": str(
                        Path(str(prep["cache_dir"]))
                        / "probe_results"
                        / probe_def[0]
                    ),
                }
            )

    probe_results: Dict[str, Dict[str, Path]] = {
        spec.case_id: {} for spec, _ in resolved
    }
    phase2_started = time.perf_counter()
    print("\n[Phase 2/3] Running QSM-QTE-FATE field probes in parallel...")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers, mp_context=mp_context
    ) as executor:
        futures = {
            executor.submit(run_probe_cache_worker, payload): payload
            for payload in probe_payloads
        }
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            completed += 1
            case_id = str(result["case_id"])
            probe_key = str(result["probe_key"])
            probe_results[case_id][probe_key] = Path(
                str(result["result_dir"])
            )
            print(
                f"  [PROBE {completed}/{len(futures)}] "
                f"{case_id} / {result['probe_name']}: "
                f"{result['elapsed_seconds']:.1f} s"
            )
    phase2_elapsed = time.perf_counter() - phase2_started

    phase3_started = time.perf_counter()
    print("\n[Phase 3/3] Writing case and cross-case releases...")
    cases_root = root_out / "cases"
    cases_root.mkdir(parents=True, exist_ok=True)
    case_summaries: List[Dict[str, object]] = []
    floor_frames: List[pd.DataFrame] = []
    probe_frames: List[pd.DataFrame] = []
    for index, (spec, source_path) in enumerate(resolved, start=1):
        case_summary, floor_df, probe_df, _ = finalize_cached_case_v11(
            spec=spec,
            source_path=source_path,
            cache_dir=Path(str(prep_results[spec.case_id]["cache_dir"])),
            probe_result_dirs=probe_results[spec.case_id],
            case_out=cases_root / spec.case_id,
            workers=workers,
        )
        case_summaries.append(case_summary)
        floor_frames.append(floor_df)
        probe_frames.append(probe_df)
        print(f"  [WRITE {index}/{len(resolved)}] {spec.case_id}")

    write_cross_case_outputs(
        root_out,
        case_summaries,
        floor_frames,
        probe_frames,
        [spec for spec, _ in resolved],
    )
    phase3_elapsed = time.perf_counter() - phase3_started

    if not args.keep_cache:
        shutil.rmtree(cache_root, ignore_errors=True)

    elapsed = time.perf_counter() - overall_started
    run_finished_utc = datetime.now(timezone.utc).isoformat()
    root_log_lines = [
        "QSM-QTE-FATE Integrated Seismic Field Observation",
        "NEES-2011-1076 Formal Release V11",
        "",
        f"Run started UTC: {run_started_utc}",
        f"Run finished UTC: {run_finished_utc}",
        f"Project root: {root}",
        f"Output root: {root_out}",
        f"Logical processors detected: {cpu_count}",
        f"CSV preparation workers: {prepare_workers}",
        f"Parallel probe workers: {workers}",
        f"Cases completed: {len(resolved)}",
        f"Probe tasks completed: {total_probe_tasks}",
        "",
        "Wall-clock timing",
        f"  Phase 1 — data preparation: {phase1_elapsed:.3f} s",
        f"  Phase 2 — parallel field probes: {phase2_elapsed:.3f} s",
        f"  Phase 3 — artifact generation: {phase3_elapsed:.3f} s",
        f"  Total release elapsed: {elapsed:.3f} s",
        "",
        "Interpretation note",
        "  Per-case logs include each worker-process probe time. Their sums "
        "represent computational task load, while the phase and total values "
        "above are wall-clock times.",
    ]
    if missing:
        root_log_lines += ["", "Cases skipped:"]
        root_log_lines.extend(f"  - {spec.case_id}" for spec in missing)
    (root_out / "00_RELEASE_RUN_LOG.txt").write_text(
        "\n".join(root_log_lines) + "\n",
        encoding="utf-8",
    )

    print("\n=== V11 formal release completed ===")
    print(f"Project root: {root}")
    print(f"Output root: {root_out}")
    print(f"Cases completed: {len(resolved)}")
    print(f"Parallel probe workers used: {workers}")
    print(f"Phase 1 elapsed: {phase1_elapsed:.1f} s")
    print(f"Phase 2 elapsed: {phase2_elapsed:.1f} s")
    print(f"Phase 3 elapsed: {phase3_elapsed:.1f} s")
    print(f"Total elapsed time: {elapsed:.1f} s")
    if missing:
        print("Cases skipped:")
        for spec in missing:
            print(f"  - {spec.case_id}")

if __name__ == "__main__":
    main_v11()
