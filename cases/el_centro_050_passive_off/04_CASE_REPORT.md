# El Centro 0.50 — passive-off

## QSM–QTE–FATE Integrated Seismic Field Observation · V12.2

- Source file: `elcentro_0p50_07312012_poff_donghua_converted.csv`
- Earthquake input: **El Centro**
- Input scale: **0.50**
- Control state: **passive-off**
- Acquisition context: **Dong-Hua shake-table record**

## Three-stage method chain

| Order | Method | Hamiltonian / update | Observation role |
|---:|---|---|---|
| 1 | QSM | `H = -W`, zero diagonal | Input-driven power-state evolution |
| 2 | QTE | `H = L(W)` in the present NEES execution | Spatial topology-path evolution |
| 3 | FATE | QTE evolution with continuous floor-sensor assimilation and response feedback | `Aware_power` |

> The present QTE execution uses the Laplacian topology term. A hard structural-parameter field diagonal is not asserted for these NEES records.

## Method summary

| Method | Mean signed corr | Mean abs-envelope corr | Final path dominance | Edge-current ratio 1F–2F / 2F–3F | Mean manifested-work ratio |
|---|---:|---:|---:|---:|---:|
| QSM | 0.002 | 0.617 | 0.000 | 1.001 | 0.679 |
| QTE | 0.037 | 0.737 | -0.003 | 0.970 | 0.488 |
| FATE | 0.258 | 0.589 | 0.150 | 2.010 | 0.555 |

## Three-floor results

| Method | Floor | Signed corr | Abs-envelope corr | Residual RMSE | Manifested-work ratio | Response envelope |
|---|---|---:|---:|---:|---:|---:|
| QSM | 1F | -0.103 | 0.585 | 1323.02 | 0.191 | 3.57778 |
| QSM | 2F | 0.507 | 0.636 | 4297.94 | 0.895 | 2.55554 |
| QSM | 3F | -0.400 | 0.629 | 7160.83 | 0.952 | 2.62722 |
| QTE | 1F | -0.054 | 0.857 | 1241.81 | 0.196 | 3.57778 |
| QTE | 2F | 0.016 | 0.667 | 4518.54 | 0.317 | 2.55554 |
| QTE | 3F | 0.150 | 0.687 | 6806.3 | 0.952 | 2.62722 |
| FATE | 1F | 0.680 | 0.799 | 10306.6 | 0.010 | 3.57778 |
| FATE | 2F | 0.053 | 0.501 | 4618.75 | 0.703 | 2.55554 |
| FATE | 3F | 0.040 | 0.468 | 6929.53 | 0.952 | 2.62722 |

## Figure guide

| Figure | Question answered |
|---|---|
| `06_qsm_qte_fate_stage_bar.png` | How does three-floor observation alignment evolve through QSM → QTE → FATE? |
| `07_qsm_three_floor_waveforms.png` | What does zero-diagonal QSM evolve at 1F, 2F, and 3F? |
| `08_qte_three_floor_waveforms.png` | What does Laplacian QTE evolve at 1F, 2F, and 3F? |
| `09_fate_three_floor_waveforms.png` | What changes when sensor-aware FATE updates the three floors? |
| `10_qsm_qte_fate_edge_current_ratio.png` | How is RMS edge-current concentration redistributed through the three-stage chain? |
| `11_qte_path_weight_evolution.png` | How does the QTE spatial path evolve? |
| `12_fate_sensor_aware_path_evolution.png` | How does sensor awareness reshape the path in FATE? |
| `13_qte_fate_edge_current_evolution.png` | How do J12 and J23 evolve before and after sensor awareness? |
| `14_qte_fate_path_dominance_evolution.png` | How does path dominance evolve from QTE to FATE? |
| `15_fate_target_hit_state_awareness.png` | How do target-hit Power, measured |a·v|, fidelity, and residual evolve together? |
| `16_fate_work_proxy_ratios_by_floor.png` | What portion of work-compatible capacity is manifested or remains unmanifested? |
| `17_force_displacement_work_loop_proxy.png` | How does the result reconnect to the traditional acceleration/force–displacement structural entrance? |
| `18_response_manifestation_by_floor.png` | Where is the largest measured downstream displacement response? |

## Signal provenance

| Floor | Displacement | Velocity | Acceleration |
|---|---|---|---|
| 1F | `direct:First Floor Relative Displacement Sensor` | `derived:d(displacement)/dt` | `direct:First Floor Acceleration Sensor` |
| 2F | `direct:Second Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Second Floor Acceleration Sensor` |
| 3F | `direct:Third Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Third Floor Acceleration Sensor` |

## Interpretation boundary

V12.2 keeps the single QSM → QTE → FATE method chain. The restored figures are independent physical observation dimensions, not additional sensitivity groups or competing methods.

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. DOI: 10.7277/TPS7-V877.
