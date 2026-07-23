# El Centro 0.50 — uncontrolled
## QSM–QTE–FATE Three-Stage Observation Record — Formal Release V12.2

> **Recommended location**  
> `cases/el_centro_050_uncontrolled/README.md`
>
> This README is the narrative interpretation layer for the V12.2 outputs in this folder. The CSV, JSON, log, and figure files remain the canonical machine-readable evidence.

---

## 1. Role of this case

This case is retained as a **data-semantic stress case with the longest record and the strongest sustained sensor-aware lower-interface concentration among the two El Centro records**.

Its current evidence role is: **secondary for absolute QSM power-state alignment; primary for observing how heterogeneous signal semantics propagate through QTE and FATE**.

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
| Earthquake input | El Centro |
| Input scale | 0.50 |
| Control state | uncontrolled |
| Acquisition context | Dong-Hua shake-table record |
| Source file | `elcentro_0p50_07312012_unc_donghua_converted.csv` |
| Source rows detected | 1,017,888 |
| Rows loaded after stride | 203,578 |
| Read stride | 5 |
| Columns loaded | 7 |
| Event window used in waveform figures | 51.152400–165.785600 s |
| Full processed history | 0.000000–203.577000 s, 3,000 exported rows |
| Dataset DOI | 10.7277/TPS7-V877 |

### Execution timing

| Execution item | Recorded time |
|---|---|
| Data preparation | 2.549 s |
| QSM worker | 14.001 s |
| QTE worker | 14.966 s |
| FATE worker | 19.565 s |
| Artifact generation | 4.963 s |
| Parallel method workers configured | 8 |

Worker elapsed times are computational records. Because the method workers may execute concurrently, their sum is not the case wall-clock time.

---

## 4. Signal provenance and evidential strength

| Floor | Displacement `u` | Velocity `v` | Acceleration `a` |
|---|---|---|---|
| 1F | `direct:First Floor Relative Displacement Sensor` | `derived:d(displacement)/dt` | `direct:First Floor Acceleration Sensor` |
| 2F | `direct:Second Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Second Floor Acceleration Sensor` |
| 3F | `direct:Third Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Third Floor Acceleration Sensor` |

The El Centro cases do not provide one homogeneous three-floor state description. The first-floor displacement is relative, the upper-floor displacements are absolute, and velocity is reconstructed by differentiating displacement. Acceleration remains directly measured.

Accordingly, `a·v` mixes direct acceleration with derived velocity under different coordinate semantics. The case remains scientifically useful, while its upper-floor absolute Power-state alignment is not assigned the same evidential strength as the direct-channel Kobe and Morgan Hill records.

---

## 5. Canonical three-stage result summary

| Stage | Mean signed corr | Mean abs-envelope corr | Residual RMSE | Final `D` | Mean `D` | `J12/J23` | Mean manifested ratio | Max-response floor |
|---|---|---|---|---|---|---|---|---|
| QSM | -0.135 | 0.671 | 13553.650 | 0.000 | 0.000 | 0.997 | 0.616 | 3F |
| QTE | -0.039 | 0.765 | 13214.600 | -0.000 | -0.007 | 0.983 | 0.450 | 3F |
| FATE | 0.323 | 0.615 | 22738.816 | 0.140 | 0.435 | 3.763 | 0.507 | 3F |

Definitions:

- **Signed correlation** retains Power direction and phase tendency.
- **Absolute-envelope correlation** compares the strength envelope of `|a·v|`.
- **Path dominance** is `D = (w12 - w23) / (w12 + w23)`; positive values indicate greater manifestation on `1F–2F`.
- **Edge-current ratio** is the RMS ratio `J12/J23`; values above `1` indicate greater current concentration on `1F–2F`.
- **Manifested-work ratio** is a case-internal normalized proxy. It is not an absolute cross-case physical energy percentage.

### Stage transition

- QSM → QTE changes mean absolute-envelope alignment from **0.671** to **0.765** (`Δ = +0.094`).
- QTE → FATE changes mean absolute-envelope alignment from **0.765** to **0.615** (`Δ = -0.150`).
- Signed alignment progresses **-0.135 → -0.039 → 0.323**.

The transition must be read with the signal provenance above. FATE introduces measured floor states; improvement in the direct-channel cases and degradation at the heterogeneous El Centro upper floors describe different data conditions rather than one universal expected direction.

---

## 6. Floor-by-floor comparison in one fixed format

| Stage | Floor | Signed corr | Abs-envelope corr | Residual RMSE | RMS amplitude ratio | Peak offset (s) | Manifested ratio | Response envelope |
|---|---|---|---|---|---|---|---|---|
| QSM | 1F | -0.237 | 0.750 | 4822.204 | 0.616 | 0.001000 | 0.128 | 2.357043 |
| QSM | 2F | 0.008 | 0.711 | 13328.676 | 0.083 | -1.389 | 0.766 | 3.573281 |
| QSM | 3F | -0.177 | 0.553 | 22510.071 | 0.078 | 2.459 | 0.952 | 3.658619 |
| QTE | 1F | -0.058 | 0.792 | 3933.800 | 0.266 | 0.001000 | 0.162 | 2.357043 |
| QTE | 2F | 0.003 | 0.770 | 13497.040 | 0.175 | -0.694000 | 0.237 | 3.573281 |
| QTE | 3F | -0.060 | 0.733 | 22212.959 | 0.051 | 0.008000 | 0.952 | 3.658619 |
| FATE | 1F | 0.778 | 0.900 | 32545.811 | 9.275 | -0.006000 | 0.008 | 2.357043 |
| FATE | 2F | 0.093 | 0.477 | 13569.566 | 0.320 | 0.158000 | 0.560 | 3.573281 |
| FATE | 3F | 0.097 | 0.469 | 22101.070 | 0.193 | -0.025000 | 0.952 | 3.658619 |

The RMS amplitude ratio is recomputed from `03_qsm_qte_fate_full_history.csv` over the declared event window using `RMS(evolved a·v) / RMS(measured a·v)`. It complements correlation: two signals may have similar shape while retaining different amplitudes.

Residual RMSE carries the numerical scale of each source record. It is useful within a case and floor; it should not be compared across source datasets without normalization.

---

## 7. QSM — zero-diagonal input-driven Power-state evolution

QSM uses:

```text
H_QSM = -W
```

The diagonal is cleared. The fixed relational channels transmit the boundary input, and the current V12.2 QSM stage does not assimilate the three measured floor states.

For this case, QSM gives mean signed/absolute-envelope alignment of **-0.135/0.671**. Its fixed path remains `w12 = w23 = 1`, so `D = 0`; the edge-current ratio is **0.997**, close to an equal-current state.

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

For this case, QTE mean signed/absolute-envelope alignment is **-0.039/0.765**. The final path dominance is **-0.000**, the full-history mean is **-0.007**, and the edge-current ratio is **0.983**.

The full QTE history ranges from `D = -0.115` at `5.498 s` to `D = 0.083` at `0.746 s`. The final state remains near equal, showing that the boundary-driven Laplacian topology alone does not establish the sensor-aware internal path seen in FATE.

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

FATE produces mean signed/absolute-envelope alignment of **0.323/0.615**. Its final path state is `w12 = 1.140`, `w23 = 0.860`, with `D = 0.140` and edge-current ratio **3.763**.

The sensor-aware 1F result becomes coherent, while 2F and 3F retain weak signed and envelope alignment. The contrast follows the signal provenance: 1F displacement is relative, 2F and 3F displacement are absolute, and all velocities are numerical derivatives.

The FATE path begins from equality, develops a broad and sustained 1F–2F concentration, reaches its strongest separation late in the record, and only partially redistributes before the final time. The final dominance therefore understates the duration of the intermediate concentration.

### Full-history FATE path audit

| Audit quantity | Value |
|---|---|
| Final `D` | 0.140 |
| Mean `D` | 0.435 |
| Maximum `D` | 0.692 at 145.334 s |
| Minimum `D` | 0.000 at 0.000 s |
| Fraction of history with `D > 0` | 100.0% |
| Fraction of history with `D > 0.1` | 97.3% |
| Fraction of history with `D > 0.2` | 89.5% |

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
| QSM | 0.560 | 0.561 | 0.997 |
| QTE | 0.468 | 0.476 | 0.983 |
| FATE | 0.444 | 0.118 | 3.763 |

![QSM → QTE → FATE edge-current concentration ratio](10_qsm_qte_fate_edge_current_ratio.png)

### 10.2 FATE work-compatible manifestation by floor

| Floor | Hit-work capacity | Displacement-side work | Manifested ratio | Unmanifested margin | Measured abs work | Max response | Peak time (s) |
|---|---|---|---|---|---|---|---|
| 1F | 26253005.230 | 220106.854 | 0.008 | 0.992 | 220106.854 | 2.357043 | 66.549000 |
| 2F | 1434375.679 | 803166.414 | 0.560 | 0.440 | 803166.414 | 3.573281 | 57.542000 |
| 3F | 1424657.162 | 1356816.345 | 0.952 | 0.048 | 1356816.345 | 3.658619 | 57.546000 |

![FATE work-compatible proxy ratios by floor](16_fate_work_proxy_ratios_by_floor.png)

![Measured response manifestation by floor](18_response_manifestation_by_floor.png)

These work-compatible ratios are normalized within the case. They describe how the current observation chain partitions manifested and unmanifested proxy capacity; they are not physical energy percentages that can be compared directly across earthquakes.

---

## 11. Traditional structural entrance: acceleration–displacement work-loop proxy

The acceleration–displacement plot is a broad multi-branch cloud with a persistent descending orientation. It retains a restoring-response tendency, but its branch structure is too heterogeneous for direct hysteresis-area interpretation.

The event-window acceleration–displacement correlations recomputed from the full-history CSV are:

| Floor | Corr(`u`,`a`) over figure event window |
|---|---|
| 1F | -0.876 |
| 2F | -0.275 |
| 3F | -0.345 |

A negative correlation is consistent with a broad restoring orientation. It does not turn the normalized proxy plot into a directly calibrated force–displacement hysteresis loop; floor mass, restoring force calibration, and coordinate consistency remain outside the current record.

![Traditional acceleration/force–displacement work-loop proxy](17_force_displacement_work_loop_proxy.png)

---

## 12. What this case currently supports

- QSM and QTE retain the incoming-event envelope under heterogeneous channel semantics.
- FATE produces meaningful 1F alignment and a persistent 1F–2F path history, while the upper-floor Power-state alignment remains weak.
- The method exposes the consequences of mixing relative and absolute displacement coordinates with differentiated velocity.
- Path manifestation can remain interpretable even when amplitude-level Power-state coherence is degraded.
- The irregular work-loop proxy is preserved as evidence about the data-production chain rather than filtered into an artificial smooth loop.

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

El Centro 0.50 — uncontrolled is retained as part of the four-case V12.2 evidence matrix. Its strongest contribution is not a single score; it is the way the same QSM → QTE → FATE chain reveals the relation among input-driven state evolution, spatial path formation, sensor-aware manifestation, work-compatible proxies, and measured structural response.