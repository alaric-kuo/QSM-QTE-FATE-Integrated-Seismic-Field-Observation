# V12.2 Output Guide

## Method order

```text
QSM → QTE → FATE
```

The method order is sequential. Physical observations under each stage are not extra algorithms.

## Per-case reading order

1. `06_qsm_qte_fate_stage_bar.png` — three-stage, three-floor overview.
2. `07_qsm_three_floor_waveforms.png` — QSM input-driven zero-diagonal evolution.
3. `08_qte_three_floor_waveforms.png` — QTE Laplacian topology-stage waveforms.
4. `09_fate_three_floor_waveforms.png` — FATE sensor-aware waveforms.
5. `10_qsm_qte_fate_edge_current_ratio.png` — stage-wise edge-current concentration.
6. `11_qte_path_weight_evolution.png` — QTE path weights.
7. `12_fate_sensor_aware_path_evolution.png` — sensor-aware FATE path weights.
8. `13_qte_fate_edge_current_evolution.png` — QTE and FATE edge-current histories.
9. `14_qte_fate_path_dominance_evolution.png` — path formation, concentration, recovery, and redistribution.
10. `15_fate_target_hit_state_awareness.png` — target hit, fidelity, and residual awareness.
11. `16_fate_work_proxy_ratios_by_floor.png` — manifested and unmanifested work-compatible proxies.
12. `17_force_displacement_work_loop_proxy.png` — traditional structural acceleration/force–displacement entrance.
13. `18_response_manifestation_by_floor.png` — measured downstream response.

## Cross-case figures

- `03_cross_case_qsm_qte_fate_bar.png` — stage-wise mean alignment.
- `04_cross_case_edge_current_ratio.png` — edge-current concentration.
- `05_cross_case_fate_path_dominance.png` — FATE final path dominance.
- `06_cross_case_fate_manifested_work_ratio.png` — FATE manifested-work ratio.
- `07_cross_case_three_floor_alignment.png` — separate QSM, QTE, and FATE floor panels.

## CSV hierarchy

- `01_qsm_qte_fate_method_summary.csv` — one row for each method.
- `02_qsm_qte_fate_floor_summary.csv` — one row for each method and floor.
- `03_qsm_qte_fate_full_history.csv` — 149-column trace for measured data and all three stages.

## Reading cautions

- Stage-wise correlations are not a competition because later stages receive additional information.
- Shape-normalized and common-scale waveform views answer different questions; the V12.2 stage waveform figures preserve common scale within each floor.
- Work-compatible ratios are case-internal normalized proxies, not cross-earthquake physical energy percentages.
- Positive FATE path dominance indicates a higher `1F–2F` floor-domain weight; it is not by itself proof of a member-level failure plane.
