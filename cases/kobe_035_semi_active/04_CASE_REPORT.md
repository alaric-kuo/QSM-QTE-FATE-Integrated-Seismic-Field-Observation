# Kobe 0.35 — semi-active

## QSM–QTE–FATE Integrated Seismic Field Observation · V12.2

- Source file: `kobe_035_semi_active_avg_converted.csv`
- Earthquake input: **Kobe**
- Input scale: **0.35**
- Control state: **semi-active**
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
| QSM | 0.065 | 0.582 | 0.000 | 0.998 | 0.677 |
| QTE | -0.016 | 0.677 | -0.007 | 0.958 | 0.549 |
| FATE | 0.656 | 0.918 | 0.543 | 4.392 | 0.611 |

## Three-floor results

| Method | Floor | Signed corr | Abs-envelope corr | Residual RMSE | Manifested-work ratio | Response envelope |
|---|---|---:|---:|---:|---:|---:|
| QSM | 1F | 0.151 | 0.561 | 0.0280346 | 0.270 | 3.64991 |
| QSM | 2F | -0.153 | 0.612 | 0.0745369 | 0.952 | 3.80214 |
| QSM | 3F | 0.196 | 0.573 | 0.110916 | 0.808 | 4.17388 |
| QTE | 1F | 0.087 | 0.757 | 0.0293415 | 0.195 | 3.64991 |
| QTE | 2F | 0.012 | 0.725 | 0.073517 | 0.500 | 3.80214 |
| QTE | 3F | -0.147 | 0.548 | 0.115384 | 0.952 | 4.17388 |
| FATE | 1F | 0.567 | 0.851 | 0.0603183 | 0.208 | 3.64991 |
| FATE | 2F | 0.709 | 0.949 | 0.0526711 | 0.672 | 3.80214 |
| FATE | 3F | 0.693 | 0.955 | 0.0819997 | 0.952 | 4.17388 |

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
