# El Centro 0.50 — Passive-Off  
## QSM–QTE–FATE Data-Semantic Observation Record — Formal Release V11

> **Recommended location**  
> `cases/el_centro_050_passive_off/README.md`
>
> **Repository**  
> `QSM-QTE-FATE-Integrated-Seismic-Field-Observation`

---

## 1. Why this case is retained

The passive-off El Centro record provides a second data-semantic stress case under a different control condition. Its Figure 17 remains irregular, but its path history contains a more abrupt mid-record transition than the uncontrolled case.

This case is not removed from the release merely because its work-loop proxy and upper-floor `a*v` alignment are less coherent than the Kobe and Morgan Hill records.

The V11 method preserves the supplied measurement and conversion history so that the following layers remain distinguishable:

```text
structural response
measurement coordinate choice
numerical differentiation
instrument and acquisition behavior
conversion and processing history
possible operational or human-intervention traces
```

Preserving these traces does not mean that every irregularity is interpreted as physical structure. It means that irregularities are not silently filtered away before their influence on the field representation can be observed.

The scientific role of this case is therefore:

```text
QSM power-state sensitivity
→ QTE floor-domain trend observation
→ FATE Aware_power data-quality awareness
```

---

## 2. Method scope

### QSM

QSM is examined through the one-step field sequence:

```text
measurements through k
→ evolve the field to k+1|k
→ compare evolved a*v with measured a*v at k+1
→ assimilate the new measurement
```

### QTE

QTE is examined at the available floor-domain resolution:

```text
1F node ↔ 2F node ↔ 3F node
```

with two inter-floor paths:

```text
1F–2F
2F–3F
```

No member-level BIM/IFC or complete as-built structural graph is available in this record.

### FATE

FATE is represented at the `Aware_power` layer. In this case, awareness includes not only field and path indicators, but also awareness that the measurement representation itself is heterogeneous.

---

## 3. Experimental source

| Item | Value |
|---|---|
| Project | NEES-2011-1076 |
| Project title | RTHS and Shake Table Comparison for Smart Structural Systems |
| Source file | `elcentro_0p50_07312012_poff_donghua_converted.csv` |
| Earthquake input | El Centro |
| Input scale | 0.50 |
| Control state | passive-off |
| Acquisition context | Dong-Hua shake-table record |
| Source rows detected | 586,352 |
| Rows loaded after stride | 117,271 |
| Read stride | 5 |
| Figure event window | 1.609550–115.161450 s |
| Dataset DOI | 10.7277/TPS7-V877 |

The full time history is retained in:

```text
04_qsm_qte_fate_core_history.csv
```

---

## 4. Signal provenance and the central data issue

| Floor | Displacement `u` | Velocity `v` | Acceleration `a` |
|---|---|---|---|
| 1F | `First Floor Relative Displacement Sensor` | derived from `d(displacement)/dt` | `First Floor Acceleration Sensor` |
| 2F | `Second Floor Absolute Displacement Sensor` | derived from `d(displacement)/dt` | `Second Floor Acceleration Sensor` |
| 3F | `Third Floor Absolute Displacement Sensor` | derived from `d(displacement)/dt` | `Third Floor Acceleration Sensor` |

The three floors do not share one fully homogeneous displacement coordinate definition:

```text
1F:
relative displacement

2F and 3F:
absolute displacement
```

Velocity is not a direct channel. It is reconstructed by differentiating the selected displacement signal, while acceleration remains directly measured.

Therefore:

\[
a(t)v(t)
\]

combines a direct acceleration signal with a velocity derived from displacement channels that do not all use the same coordinate semantics.

This does not make the record useless. It changes what can be claimed from it.

The record is retained as a **data-semantic stress test** rather than treated as equal-strength primary evidence for absolute power-state coherence.

---

## 5. V11 execution record

| Execution item | Recorded time |
|---|---:|
| Data preparation | 1.463 s |
| Laplacian floor-state probe | 5.960 s |
| Zero-diagonal floor-state probe | 6.018 s |
| Boundary-input-only reference | 4.640 s |
| Dynamic path without response feedback | 14.190 s |
| Fixed-path reference | 12.640 s |
| Sum of probe-worker elapsed time | 43.448 s |
| Longest probe-worker elapsed time | 14.190 s |
| Case finalization | 3.090 s |
| Accounted case task time | 48.002 s |

Probe-worker times ran in parallel and should not be added as wall-clock time.

---

## 6. Five observation probes

| Probe | Observation role |
|---|---|
| Laplacian floor-state field probe | Main integrated QSM–QTE–FATE observation |
| Zero-diagonal floor-state field probe | Pure relational-transmission comparison |
| Boundary-input-only diagnostic reference | Incoming-wave reference without floor-state assimilation |
| Floor-state dynamic path without response feedback | Response-feedback sensitivity check |
| Fixed-path reference | Separates QSM field alignment from QTE path adaptation |

The five probes do not represent five physical paths. The floor-domain model contains only `1F–2F` and `2F–3F`.

---

## 7. Final path indicators

| Probe | Final `w12` | Final `w23` | Final dominance | Edge-current ratio |
|---|---:|---:|---:|---:|
| Laplacian floor-state | 1.150 | 0.850 | 0.150 | 2.010 |
| Zero-diagonal floor-state | 1.147 | 0.853 | 0.147 | 1.993 |
| Dynamic path without response feedback | 1.146 | 0.854 | 0.146 | 1.986 |
| Boundary-input-only | 0.997 | 1.003 | -0.003 | 0.970 |
| Fixed-path reference | 1.000 | 1.000 | 0.000 | 1.395 |

The three floor-state dynamic probes produce the same higher-weight final path indication:

```text
1F–2F lower-interface indication
```

Support count:

```text
3 / 3
```

The boundary-input-only reference remains:

```text
near-equal / no clear final path indication
```

![Observed final path indicators across field probes](07_energy_path_manifestation_consensus.png)

---

## 8. What the path history shows

The passive-off path history begins with only a mild separation. Around the middle of the record, the two path weights change rapidly: `1F–2F` rises while `2F–3F` falls. The separation later reaches a maximum and then gradually returns.

The main trend is:

```text
weak initial separation
→ abrupt mid-record transition
→ stronger temporary lower-interface concentration
→ gradual redistribution
```

The final dominance is approximately `0.150`, while the mean dominance is about `0.210`. The mean floor-state edge-current ratio is approximately `1.997`.

The abrupt transition is retained rather than smoothed away. It may contain structural, acquisition, conversion, operational, or human-intervention contributions that require later attribution.

![Floor-state-assimilated path-weight evolution](08_floor_assimilated_path_evolution.png)

The boundary-input-only history continues to oscillate around equal weighting and does not form a comparable persistent internal path history.

![Boundary-input-only path-weight evolution](09_boundary_input_only_path_evolution.png)

![Observed path-dominance histories by observation mode](15_boundary_vs_assimilated_path_dominance.png)

The path history is therefore retained as a QTE trend indicator even though the power-state signal provenance is heterogeneous.

---

## 9. Edge-current trend

The mean edge-current ratio across the three floor-state dynamic probes is:

\[
1.997
\]

The main Laplacian ratio is:

\[
2.010
\]

The boundary-only ratio is:

\[
0.970
\]

This difference indicates that the lower-interface tendency appears primarily after floor-state information enters the field representation.

![QSM edge-current concentration ratio across field probes](10_edge_current_concentration.png)

---

## 10. One-step `a*v` comparison

| Floor | Floor-state signed corr | Floor-state abs corr | Boundary signed corr | Boundary abs corr |
|---|---:|---:|---:|---:|
| 1F | 0.680 | 0.799 | -0.054 | 0.857 |
| 2F | 0.053 | 0.501 | 0.016 | 0.667 |
| 3F | 0.040 | 0.468 | 0.150 | 0.687 |

The floor-state mean absolute-envelope correlation is `0.589`. The boundary-only value is `0.737`.

The 1F result remains materially more coherent than the upper-floor results. The 2F and 3F field-state comparisons are weaker, consistent with the mixed relative/absolute displacement coordinates and the use of differentiated velocity.

![1F one-step evolved-field comparison](11_1f_evolved_av_next_vs_measured_av.png)

![2F one-step evolved-field comparison](12_2f_evolved_av_next_vs_measured_av.png)

![3F one-step evolved-field comparison](13_3f_evolved_av_next_vs_measured_av.png)

![Observed a*v alignment by observation mode](14_boundary_vs_assimilated_av_alignment.png)

A higher boundary-only envelope correlation at some floors should not be interpreted as proof that internal floor states are physically unnecessary. In this record, it indicates that the common incoming-wave envelope is more coherent than the heterogeneous floor-state representation used to build `a*v`.

---

## 11. Figure 17: what the irregular work-loop proxy reveals

![Normalized acceleration–displacement work-loop proxy](17_force_displacement_work_loop_proxy.png)

Figure 17 is angular and multi-valued rather than loop-like. The record contains a dense central region together with long connecting segments and episodic excursions. The 1F trace is broader, while the upper-floor traces cluster more closely around the center but still contain large branches.

The global descending orientation remains visible, but the local geometry is discontinuous and unsuitable for direct hysteresis-area interpretation.

The figure therefore records two things at once:

```text
a broad restoring-response tendency
+
a non-homogeneous measurement and processing history
```

The figure should not be cleaned into a smooth loop merely to resemble a conventional hysteresis diagram.

Its irregularity is itself an observation of the data-production chain.

A cautious reading separates three levels:

### 11.1 Persistent physical tendency

Across the cloud, acceleration generally trends opposite to displacement. The dominant orientation is a descending diagonal, consistent with a restoring-response tendency at the broadest level.

### 11.2 Loss of a single-valued loop geometry

At the same normalized displacement, acceleration occupies multiple branches. The record does not form a stable closed loop that can be assigned one unambiguous physical area.

This is consistent with:

- mixed displacement coordinates;
- numerically differentiated velocity;
- multiple frequency components;
- acquisition and conversion effects;
- possible experimental-operation traces.

### 11.3 Preserved human and measurement history

The method does not assume that everything outside a smooth structural loop is disposable noise.

Possible traces of sensor choice, coordinate definition, conversion, experimental handling, and human intervention remain visible as part of the observed system history.

This is useful for FATE `Aware_power`: awareness must include the reliability and origin of the field being observed, not only the field value itself.

---

## 12. Work-compatible proxy distribution

| Floor | Manifested ratio | Unmanifested margin | Maximum downstream response |
|---|---:|---:|---:|
| 1F | 0.010 | 0.990 | 3.578 |
| 2F | 0.703 | 0.297 | 2.556 |
| 3F | 0.952 | 0.048 | 2.627 |

The mean manifested work ratio is `0.555`.

Because the underlying displacement and derived velocity channels are heterogeneous, these values are retained as **case-internal diagnostic proxies**. They are not interpreted as absolute energy fractions.

![Work-compatible proxy ratios by floor](16_work_capacity_summary_by_floor.png)

![Observed downstream displacement-response envelope by floor](18_response_manifestation_by_floor.png)

---

## 13. What this method can still see without removing the irregularities

The El Centro record demonstrates that the method can separate several trends even when the work-loop proxy is not clean:

1. **Input and internal field are distinguishable.**  
   Boundary-only path weights remain near equal, while floor-state probes develop a consistent lower-interface tendency.

2. **Path tendency can be more stable than power-state amplitude agreement.**  
   QTE produces 3/3 floor-state path support even when upper-floor QSM correlations are weak.

3. **The temporal history contains more information than the final bar.**  
   Concentration, transition, recovery, and redistribution remain visible in the path-weight history.

4. **Data semantics become observable.**  
   The method reveals that relative displacement, absolute displacement, derived velocity, and direct acceleration do not behave as one homogeneous state description.

5. **Noise is not automatically discarded.**  
   Irregular branches remain available for later attribution to structure, sensors, processing, operation, or human intervention.

6. **FATE awareness includes epistemic condition.**  
   A living control framework must know not only where a path appears, but also how trustworthy and semantically coherent the observed field is.

---

## 14. What this case currently indicates

### QSM

This case indicates that:

- one-step field alignment remains meaningful at 1F;
- upper-floor `a*v` coherence is sensitive to coordinate and provenance mismatch;
- a weak result can reveal the boundary conditions of the observation method.

### QTE

This case indicates that:

- the three floor-state dynamic probes retain a common `1F–2F` path tendency;
- boundary input alone does not produce the same internal path history;
- path history remains interpretable even when amplitude-level power-state coherence is degraded.

### FATE

This case extends `Aware_power` into:

```text
field awareness
+
path awareness
+
data-semantic awareness
```

It does not yet provide `Alert_control` or `Alive_evolve`.

---

## 15. Relationship to the direct-channel cases

Kobe and Morgan Hill use direct analytical `u`, `v`, and `a` channels and therefore provide stronger primary QSM power-state evidence.

El Centro uses mixed displacement coordinates and differentiated velocity. It should not be forced into the same evidential category.

Its value is different:

```text
Kobe and Morgan Hill:
power-state replication evidence

El Centro:
data-semantic boundary and trace-preservation evidence
```

Compared with the uncontrolled El Centro record, the passive-off case shows a weaker average edge-current concentration but a clearer abrupt transition in the path-weight history. The two cases should therefore be compared as different evolutionary traces, not reduced to their similar final dominance values.

---

## 16. Reproducibility files

The case folder contains the 20 formal V11 outputs:

```text
01_qsm_qte_fate_mode_comparison.csv
02_qsm_qte_fate_manifestation_summary.csv
03_qsm_qte_fate_floor_target_summary.csv
04_qsm_qte_fate_core_history.csv
05_CASE_REPORT.md
06_release_report.txt
07_energy_path_manifestation_consensus.png
08_floor_assimilated_path_evolution.png
09_boundary_input_only_path_evolution.png
10_edge_current_concentration.png
11_1f_evolved_av_next_vs_measured_av.png
12_2f_evolved_av_next_vs_measured_av.png
13_3f_evolved_av_next_vs_measured_av.png
14_boundary_vs_assimilated_av_alignment.png
15_boundary_vs_assimilated_path_dominance.png
16_work_capacity_summary_by_floor.png
17_force_displacement_work_loop_proxy.png
18_response_manifestation_by_floor.png
19_release_run_log.txt
20_release_file_manifest.json
```

---

## 17. Data citation

Zhang, J., Wu, B., and Dyke, S.  
*RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set].  
NEES / DesignSafe Data Depot.  
DOI: `10.7277/TPS7-V877`

---

## 18. Case record

This case is retained because a scientific method should not only display the records that look clean.

It should also preserve the records that reveal:

```text
where the field remains visible
where the representation loses coherence
and where the history of measurement and human effort enters the observation
```

The irregularity is not promoted into a physical conclusion.

It is kept observable.
