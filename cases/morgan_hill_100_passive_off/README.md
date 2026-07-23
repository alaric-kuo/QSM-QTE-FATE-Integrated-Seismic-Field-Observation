# Morgan Hill 1.00 — passive-off
## QSM–QTE–FATE Three-Stage Observation Record — Formal Release V12.2

> **Recommended location**  
> `cases/morgan_hill_100_passive_off/README.md`
>
> This README is the narrative interpretation layer for the V12.2 outputs in this folder. The CSV, JSON, log, and figure files remain the canonical machine-readable evidence.

---

## 1. Role of this case

This case is retained as a **second primary direct-channel case and cross-event replication of the three-stage chain**.

Its current evidence role is: **primary evidence for repeatable sensor-aware one-step alignment under a different earthquake and control condition**.

The V12.2 method is presented as one sequential chain:

```text
QSM — zero-diagonal input-driven Power-state evolution
  ↓
QTE — Laplacian spatial topology-path evolution
  ↓
FATE — sensor-aware evolution at the Aware_power layer
```

QSM, QTE, and FATE are successive observation layers. The stage-wise correlations are therefore not a leaderboard between three competing models. Each later stage receives a richer structural description.

![QSM → QTE → FATE stage-wise three-floor summary](06_qsm_qte_fate_stage_bar.png)

---

## 2. What V12.2 changes from V11

V12.2 removes the former five-probe presentation and retains only the intended methodological sequence:

| Stage | Operator and state update | Current role |
|---|---|---|
| QSM | `H = -W`; zero diagonal; fixed relational channels; boundary input | Evolves the input-driven Power state |
| QTE | `H = L(W)`; dynamic path; boundary input | Adds spatial topology and path evolution |
| FATE | QTE evolution + floor-state assimilation + response feedback | Forms `Aware_power` from continuously updated sensor content |

The restored figures `10`–`18` are independent physical observation dimensions—edge current, path history, target hit, work proxies, structural work-loop proxy, and response manifestation. They are not additional methods or sensitivity groups.

> **Current QTE boundary**  
> This NEES execution uses the Laplacian topology term `H = L(W)`. It does not claim that a hard as-built structural-parameter field diagonal—mass, stiffness, damping, member capacity, joints, and device states—has already been inserted.

---

## 3. Experimental source and execution record

| Item | Value |
|---|---|
| Project | NEES-2011-1076 |
| Project title | RTHS and Shake Table Comparison for Smart Structural Systems |
| Earthquake input | Morgan Hill |
| Input scale | 1.00 (encoded as morgan_1) |
| Control state | passive-off |
| Acquisition context | averaged converted record |
| Source file | `morgan_1_p_off_avg_converted.csv` |
| Source rows detected | 81,009 |
| Rows loaded after stride | 16,202 |
| Read stride | 5 |
| Columns loaded | 10 |
| Event window used in waveform figures | 4.754883–16.700195 s |
| Full processed history | 0.000000–79.106445 s, 3,000 exported rows |
| Dataset DOI | 10.7277/TPS7-V877 |

### Execution timing

| Execution item | Recorded time |
|---|---|
| Data preparation | 0.216 s |
| QSM worker | 0.503 s |
| QTE worker | 0.779 s |
| FATE worker | 0.966 s |
| Artifact generation | 4.400 s |
| Parallel method workers configured | 8 |

Worker elapsed times are computational records. Because the method workers may execute concurrently, their sum is not the case wall-clock time.

---

## 4. Signal provenance and evidential strength

| Floor | Displacement `u` | Velocity `v` | Acceleration `a` |
|---|---|---|---|
| 1F | `direct:First Floor Displacement - Analytical` | `direct:First Floor Velocity Sensor - Analytical` | `direct:First Floor Acceleration - Analytical` |
| 2F | `direct:Second Floor Displacement - Analytical` | `direct:Second Floor Velocity Sensor - Analytical` | `direct:Second Floor Acceleration - Analytical` |
| 3F | `direct:Third Floor Displacement - Analytical` | `direct:Third Floor Velocity Sensor - Analytical` | `direct:Third Floor Acceleration - Analytical` |

All three floors use direct analytical displacement, velocity, and acceleration channels. This gives a synchronized basis for the phase-sensitive quantity:

```text
p_i(t) = a_i(t) · v_i(t)
```

Because floor mass is not supplied in the NEES record, `a·v` is reported as a mass-normalized work-compatible Power-state quantity, not as absolute power in watts.

---

## 5. Canonical three-stage result summary

| Stage | Mean signed corr | Mean abs-envelope corr | Residual RMSE | Final `D` | Mean `D` | `J12/J23` | Mean manifested ratio | Max-response floor |
|---|---|---|---|---|---|---|---|---|
| QSM | 0.049 | 0.604 | 0.109940 | 0.000 | 0.000 | 0.992 | 0.673 | 2F |
| QTE | 0.046 | 0.699 | 0.111133 | -0.004 | -0.017 | 0.958 | 0.490 | 2F |
| FATE | 0.753 | 0.952 | 0.095845 | 0.079 | 0.205 | 1.368 | 0.552 | 2F |

Definitions:

- **Signed correlation** retains Power direction and phase tendency.
- **Absolute-envelope correlation** compares the strength envelope of `|a·v|`.
- **Path dominance** is `D = (w12 - w23) / (w12 + w23)`; positive values indicate greater manifestation on `1F–2F`.
- **Edge-current ratio** is the RMS ratio `J12/J23`; values above `1` indicate greater current concentration on `1F–2F`.
- **Manifested-work ratio** is a case-internal normalized proxy. It is not an absolute cross-case physical energy percentage.

### Stage transition

- QSM → QTE changes mean absolute-envelope alignment from **0.604** to **0.699** (`Δ = +0.095`).
- QTE → FATE changes mean absolute-envelope alignment from **0.699** to **0.952** (`Δ = +0.253`).
- Signed alignment progresses **0.049 → 0.046 → 0.753**.

The transition must be read with the signal provenance above. FATE introduces measured floor states; improvement in the direct-channel cases and degradation at the heterogeneous El Centro upper floors describe different data conditions rather than one universal expected direction.

---

## 6. Floor-by-floor comparison in one fixed format

| Stage | Floor | Signed corr | Abs-envelope corr | Residual RMSE | RMS amplitude ratio | Peak offset (s) | Manifested ratio | Response envelope |
|---|---|---|---|---|---|---|---|---|
| QSM | 1F | 0.116 | 0.536 | 0.036688 | 0.327 | 2.441 | 0.279 | 2.773846 |
| QSM | 2F | -0.130 | 0.627 | 0.109604 | 0.097 | 2.959 | 0.952 | 2.804271 |
| QSM | 3F | 0.163 | 0.649 | 0.183528 | 0.138 | -0.083008 | 0.787 | 2.802081 |
| QTE | 1F | 0.154 | 0.782 | 0.038253 | 0.532 | -0.175781 | 0.115 | 2.773846 |
| QTE | 2F | 0.040 | 0.788 | 0.108154 | 0.133 | 2.959 | 0.402 | 2.804271 |
| QTE | 3F | -0.054 | 0.527 | 0.186993 | 0.067 | 3.877 | 0.952 | 2.802081 |
| FATE | 1F | 0.733 | 0.907 | 0.087928 | 3.061 | 0.004883 | 0.166 | 2.773846 |
| FATE | 2F | 0.785 | 0.974 | 0.070360 | 0.995 | 0.000000 | 0.539 | 2.804271 |
| FATE | 3F | 0.740 | 0.974 | 0.129247 | 0.565 | 0.004883 | 0.952 | 2.802081 |

The RMS amplitude ratio is recomputed from `03_qsm_qte_fate_full_history.csv` over the declared event window using `RMS(evolved a·v) / RMS(measured a·v)`. It complements correlation: two signals may have similar shape while retaining different amplitudes.

Residual RMSE carries the numerical scale of each source record. It is useful within a case and floor; it should not be compared across source datasets without normalization.

---

## 7. QSM — zero-diagonal input-driven Power-state evolution

QSM uses:

```text
H_QSM = -W
```

The diagonal is cleared. The fixed relational channels transmit the boundary input, and the current V12.2 QSM stage does not assimilate the three measured floor states.

For this case, QSM gives mean signed/absolute-envelope alignment of **0.049/0.604**. Its fixed path remains `w12 = w23 = 1`, so `D = 0`; the edge-current ratio is **0.992**, close to an equal-current state.

QSM therefore provides the baseline answer to:

> How much of the next-step Power-state history can be evolved from the incoming excitation through the zero-diagonal relational operator before spatial path adaptation and sensor-aware correction are added?

![QSM three-floor evolved and measured Power-state histories](07_qsm_three_floor_waveforms.png)

---

## 8. QTE — Laplacian spatial topology-path evolution

QTE uses the present topology Hamiltonian:

```text
H_QTE = L(W)
```

The Laplacian restores the topology diagonal and allows the path weights to evolve. This stage still uses the boundary input without continuous floor-state assimilation.

For this case, QTE mean signed/absolute-envelope alignment is **0.046/0.699**. The final path dominance is **-0.004**, the full-history mean is **-0.017**, and the edge-current ratio is **0.958**.

The full QTE history ranges from `D = -0.116` at `5.513 s` to `D = 0.082` at `0.762 s`. The final state remains near equal, showing that the boundary-driven Laplacian topology alone does not establish the sensor-aware internal path seen in FATE.

![QTE three-floor Power-state histories](08_qte_three_floor_waveforms.png)

![QTE Laplacian path-weight evolution](11_qte_path_weight_evolution.png)

Current interpretation:

- QTE improves or reorganizes the input-driven envelope without yet receiving the complete as-built parameter field.
- Near-equal final weights are a result, not a failed plot. They mark the limit of a topology-only, boundary-driven execution.
- The later FATE path should not be retroactively attributed to QTE alone.

---

## 9. FATE — sensor-aware evolution at `Aware_power`

FATE retains the Laplacian path evolution and adds continuous floor-state assimilation plus response feedback:

```text
sensor state at t
→ update Ψ(t)
→ evolve the topology path
→ observe target hit, edge current, work proxy, and response
→ assimilate the next measured state
```

FATE produces mean signed/absolute-envelope alignment of **0.753/0.952**. Its final path state is `w12 = 1.079`, `w23 = 0.921`, with `D = 0.079` and edge-current ratio **1.368**.

FATE gives the highest mean signed and absolute-envelope alignment in the four-case release. The three floors remain consistently aligned, with 2F and 3F absolute-envelope correlations near 0.974.

FATE develops a marked intermediate 1F–2F concentration and later redistributes toward a modest positive final dominance. The final value is small relative to the maximum, so the full path history is essential.

### Full-history FATE path audit

| Audit quantity | Value |
|---|---|
| Final `D` | 0.079 |
| Mean `D` | 0.205 |
| Maximum `D` | 0.462 at 39.141 s |
| Minimum `D` | -0.004 at 2.002 s |
| Fraction of history with `D > 0` | 99.4% |
| Fraction of history with `D > 0.1` | 77.8% |
| Fraction of history with `D > 0.2` | 42.0% |

![FATE three-floor sensor-aware Power-state histories](09_fate_three_floor_waveforms.png)

![FATE sensor-aware path-weight evolution](12_fate_sensor_aware_path_evolution.png)

![QTE and FATE edge-current histories](13_qte_fate_edge_current_evolution.png)

![QTE and FATE path-dominance histories](14_qte_fate_path_dominance_evolution.png)

![FATE target-hit and state-awareness history](15_fate_target_hit_state_awareness.png)

The implemented FATE scope is `Aware_power`. `Alert_control` and `Alive_evolve` remain subsequent stages; no closed-loop structural control result is claimed here.

---

## 10. Edge current, work manifestation, and downstream response

### 10.1 Edge-current concentration across the three stages

| Stage | RMS `J12` | RMS `J23` | `J12/J23` |
|---|---|---|---|
| QSM | 0.556 | 0.560 | 0.992 |
| QTE | 0.468 | 0.489 | 0.958 |
| FATE | 0.426 | 0.312 | 1.368 |

![QSM → QTE → FATE edge-current concentration ratio](10_qsm_qte_fate_edge_current_ratio.png)

### 10.2 FATE work-compatible manifestation by floor

| Floor | Hit-work capacity | Displacement-side work | Manifested ratio | Unmanifested margin | Measured abs work | Max response | Peak time (s) |
|---|---|---|---|---|---|---|---|
| 1F | 4.155235 | 0.687998 | 0.166 | 0.834 | 0.687998 | 2.773846 | 6.870117 |
| 2F | 4.009674 | 2.162455 | 0.539 | 0.461 | 2.162455 | 2.804271 | 6.875000 |
| 3F | 3.943870 | 3.756066 | 0.952 | 0.048 | 3.756066 | 2.802081 | 6.879883 |

![FATE work-compatible proxy ratios by floor](16_fate_work_proxy_ratios_by_floor.png)

![Measured response manifestation by floor](18_response_manifestation_by_floor.png)

These work-compatible ratios are normalized within the case. They describe how the current observation chain partitions manifested and unmanifested proxy capacity; they are not physical energy percentages that can be compared directly across earthquakes.

---

## 11. Traditional structural entrance: acceleration–displacement work-loop proxy

The acceleration–displacement traces form a narrow descending family, especially at 2F and 3F. This is the most coherent traditional restoring-response entrance in the release.

The event-window acceleration–displacement correlations recomputed from the full-history CSV are:

| Floor | Corr(`u`,`a`) over figure event window |
|---|---|
| 1F | -0.911 |
| 2F | -0.993 |
| 3F | -0.989 |

A negative correlation is consistent with a broad restoring orientation. It does not turn the normalized proxy plot into a directly calibrated force–displacement hysteresis loop; floor mass, restoring force calibration, and coordinate consistency remain outside the current record.

![Traditional acceleration/force–displacement work-loop proxy](17_force_displacement_work_loop_proxy.png)

---

## 12. What this case currently supports

- QSM provides a clean zero-diagonal input-driven baseline.
- QTE adds spatial topology organization but remains near equal without the as-built field diagonal or sensor-state assimilation.
- FATE reproduces strong three-floor one-step Power-state alignment with direct `u`, `v`, and `a` channels.
- Sensor-aware path and edge-current histories identify a case-specific 1F–2F concentration history.
- The traditional acceleration–displacement entrance is coherent enough to connect the Power-state observation back to a familiar structural restoring tendency.

## 13. What this case does not establish

- It does not establish long-horizon free prediction; the comparison is one-step and measurement-updated.
- It does not locate a member-level failure plane; the topology contains only three floor nodes and two inter-floor paths.
- It does not insert a complete as-built mass–stiffness–damping–capacity field into the QTE diagonal.
- It does not prove that path dominance equals physical damage.
- It does not implement `Alert_control` or `Alive_evolve`.
- It does not convert the work-compatible proxies into absolute joules or watts.

---

## 14. Figure and evidence guide

| File | Primary question |
|---|---|
| `06_qsm_qte_fate_stage_bar.png` | Three-stage, three-floor signed and absolute-envelope alignment |
| `07_qsm_three_floor_waveforms.png` | QSM zero-diagonal input-driven histories |
| `08_qte_three_floor_waveforms.png` | QTE Laplacian topology histories |
| `09_fate_three_floor_waveforms.png` | FATE sensor-aware histories |
| `10_qsm_qte_fate_edge_current_ratio.png` | Edge-current concentration through QSM → QTE → FATE |
| `11_qte_path_weight_evolution.png` | QTE path-weight history |
| `12_fate_sensor_aware_path_evolution.png` | FATE sensor-aware path history |
| `13_qte_fate_edge_current_evolution.png` | QTE and FATE edge-current time histories |
| `14_qte_fate_path_dominance_evolution.png` | QTE and FATE dominance histories |
| `15_fate_target_hit_state_awareness.png` | Target hit, measured `|a·v|`, fidelity, and residual |
| `16_fate_work_proxy_ratios_by_floor.png` | Manifested and unmanifested work-compatible ratios |
| `17_force_displacement_work_loop_proxy.png` | Traditional acceleration/force–displacement entrance |
| `18_response_manifestation_by_floor.png` | Measured downstream response by floor |

---

## 15. Reproducibility files

| File | Role |
|---|---|
| `01_qsm_qte_fate_method_summary.csv` | Canonical method-level values in QSM → QTE → FATE order |
| `02_qsm_qte_fate_floor_summary.csv` | Canonical method × floor comparison |
| `03_qsm_qte_fate_full_history.csv` | 149-column complete time-history evidence |
| `04_CASE_REPORT.md` | Machine-generated compact case report |
| `05_release_report.txt` | Plain-text summary |
| `19_release_run_log.txt` | Execution and timing record |
| `20_release_file_manifest.json` | Source metadata, provenance, method definitions, and file inventory |

The canonical numerical claims in this README are traceable to the two summary CSVs, the full-history CSV, and the release manifest.

---

## 16. Lifecycle interpretation

The present NEES execution is an operational retrospective observation using archived sensing data. The intended lifecycle sequence is:

```text
Design
  BIM/IFC topology → zero-diagonal relational channels and topology alternatives

Construction / as-built
  verified mass, stiffness, damping, joints, devices, and boundaries
  → field-driven Hamiltonian

Operation
  Digital Twin sensing
  → FATE Aware_power
  → future Alert_control
  → future Alive_evolve
```

V12.2 validates the executable observation chain only at the level represented by the available NEES floor-domain data.

---

## 17. Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. DOI: `10.7277/TPS7-V877`.

## 18. Release statement

Morgan Hill 1.00 — passive-off is retained as part of the four-case V12.2 evidence matrix. Its strongest contribution is not a single score; it is the way the same QSM → QTE → FATE chain reveals the relation among input-driven state evolution, spatial path formation, sensor-aware manifestation, work-compatible proxies, and measured structural response.