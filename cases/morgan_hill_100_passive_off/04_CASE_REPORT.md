# Morgan Hill 1.00 — passive-off

## QSM–QTE–FATE Integrated Seismic Field Observation · V12.2

- Source file: `morgan_1_p_off_avg_converted.csv`
- Earthquake input: **Morgan Hill**
- Input scale: **1.00 (encoded as morgan_1)**
- Control state: **passive-off**
- Acquisition context: **averaged converted record**

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
| QSM | 0.049 | 0.604 | 0.000 | 0.992 | 0.673 |
| QTE | 0.046 | 0.699 | -0.004 | 0.958 | 0.490 |
| FATE | 0.753 | 0.952 | 0.079 | 1.368 | 0.552 |

## Three-floor results

| Method | Floor | Signed corr | Abs-envelope corr | Residual RMSE | Manifested-work ratio | Response envelope |
|---|---|---:|---:|---:|---:|---:|
| QSM | 1F | 0.116 | 0.536 | 0.0366881 | 0.279 | 2.77385 |
| QSM | 2F | -0.130 | 0.627 | 0.109604 | 0.952 | 2.80427 |
| QSM | 3F | 0.163 | 0.649 | 0.183528 | 0.787 | 2.80208 |
| QTE | 1F | 0.154 | 0.782 | 0.0382532 | 0.115 | 2.77385 |
| QTE | 2F | 0.040 | 0.788 | 0.108154 | 0.402 | 2.80427 |
| QTE | 3F | -0.054 | 0.527 | 0.186993 | 0.952 | 2.80208 |
| FATE | 1F | 0.733 | 0.907 | 0.0879275 | 0.166 | 2.77385 |
| FATE | 2F | 0.785 | 0.974 | 0.0703601 | 0.539 | 2.80427 |
| FATE | 3F | 0.740 | 0.974 | 0.129247 | 0.952 | 2.80208 |

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
| 1F | `direct:First Floor Displacement - Analytical` | `direct:First Floor Velocity Sensor - Analytical` | `direct:First Floor Acceleration - Analytical` |
| 2F | `direct:Second Floor Displacement - Analytical` | `direct:Second Floor Velocity Sensor - Analytical` | `direct:Second Floor Acceleration - Analytical` |
| 3F | `direct:Third Floor Displacement - Analytical` | `direct:Third Floor Velocity Sensor - Analytical` | `direct:Third Floor Acceleration - Analytical` |

## Interpretation boundary

V12.2 keeps the single QSM → QTE → FATE method chain. The restored figures are independent physical observation dimensions, not additional sensitivity groups or competing methods.

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. DOI: 10.7277/TPS7-V877.
