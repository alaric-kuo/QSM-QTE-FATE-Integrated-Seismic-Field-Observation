# Four-Case Scientific Synthesis
## QSM–QTE–FATE Integrated Seismic Field Observation — Formal Release V12.2

> **Recommended location**  
> `cross_case/README.md`
>
> This README is the narrative synthesis for `01_cross_case_method_summary.csv`, `02_cross_case_floor_summary.csv`, and the five V12.2 cross-case figures.

---

## 1. Comparison scope

The four records come from the same three-story steel-frame experimental project, while the earthquake input, scale, control condition, acquisition context, and signal provenance are not fully balanced.

| Case | Earthquake / scale | Control | Signal condition |
|---|---|---|---|
| El Centro 0.50 — uncontrolled | El Centro / 0.50 | uncontrolled | 1F relative displacement; 2F–3F absolute displacement; velocity derived |
| El Centro 0.50 — passive-off | El Centro / 0.50 | passive-off | 1F relative displacement; 2F–3F absolute displacement; velocity derived |
| Kobe 0.35 — semi-active | Kobe / 0.35 | semi-active | Direct analytical `u`, `v`, and `a` on all floors |
| Morgan Hill 1.00 — passive-off | Morgan Hill / 1.00 | passive-off | Direct analytical `u`, `v`, and `a` on all floors |

Only the two El Centro records hold the earthquake and scale approximately fixed while changing control state. The four-case release is therefore a partial cross-wave and cross-control evidence matrix, not a balanced causal control experiment.

All cases use the same public method order and no case-specific parameter fitting:

```text
QSM → QTE → FATE
```

---

## 2. Meaning of the three stages

| Stage | Current V12.2 implementation | Scientific question |
|---|---|---|
| QSM | `H = -W`; zero diagonal; fixed relational channels; boundary input | How much Power-state evolution is carried by the incoming excitation through the relational operator? |
| QTE | `H = L(W)`; dynamic path; boundary input; no continuous floor-state assimilation | How does the Laplacian topology organize the input and evolve spatial path weights? |
| FATE | QTE + continuous floor-state assimilation + response feedback | How does the observed structural state reshape the field, path, target hit, work proxies, and response at `Aware_power`? |

The stages are sequential and receive different information. Stage-wise correlations must not be read as a competition in which the highest bar automatically identifies the “best method.”

The present QTE implementation is topology-only at the NEES floor scale. A hard as-built field diagonal containing mass, stiffness, damping, joints, capacities, and control-device states is not asserted.

---

## 3. Cross-case stage-wise alignment

| Case | QSM signed/abs | QTE signed/abs | FATE signed/abs | QSM→QTE Δabs | QTE→FATE Δabs |
|---|---|---|---|---|---|
| El Centro 0.50 — uncontrolled | -0.135/0.671 | -0.039/0.765 | 0.323/0.615 | +0.094 | -0.150 |
| El Centro 0.50 — passive-off | 0.002/0.617 | 0.037/0.737 | 0.258/0.589 | +0.121 | -0.148 |
| Kobe 0.35 — semi-active | 0.065/0.582 | -0.016/0.677 | 0.656/0.918 | +0.095 | +0.242 |
| Morgan Hill 1.00 — passive-off | 0.049/0.604 | 0.046/0.699 | 0.753/0.952 | +0.095 | +0.253 |

![Cross-case QSM → QTE → FATE stage-wise alignment](03_cross_case_qsm_qte_fate_bar.png)

### 3.1 QSM → QTE

QTE raises mean absolute-envelope alignment relative to QSM in all four cases by approximately `0.094–0.121`. This repeatable increase indicates that the Laplacian topology adds spatial organization to the boundary-driven input even before measured floor states are continuously assimilated.

At the same time, QTE signed correlations remain close to zero. The current topology-only stage captures event envelope more readily than floor-specific Power direction and phase.

### 3.2 QTE → FATE

The direct-channel cases show large gains after sensor-state assimilation:

- Kobe: `0.677 → 0.918` in mean absolute-envelope correlation.
- Morgan Hill: `0.699 → 0.952`.

The El Centro cases move in the opposite direction at the mean-envelope level:

- El Centro uncontrolled: `0.765 → 0.615`.
- El Centro passive-off: `0.737 → 0.589`.

This is a data-semantic result. In El Centro, the 1F displacement is relative, the upper-floor displacements are absolute, and velocity is differentiated from displacement. FATE exposes that heterogeneity when the measured floor states enter the field.

---

## 4. Floor-wise FATE alignment

| Case | 1F signed/abs | 2F signed/abs | 3F signed/abs |
|---|---|---|---|
| El Centro 0.50 — uncontrolled | 0.778/0.900 | 0.093/0.477 | 0.097/0.469 |
| El Centro 0.50 — passive-off | 0.680/0.799 | 0.053/0.501 | 0.040/0.468 |
| Kobe 0.35 — semi-active | 0.567/0.851 | 0.709/0.949 | 0.693/0.955 |
| Morgan Hill 1.00 — passive-off | 0.733/0.907 | 0.785/0.974 | 0.740/0.974 |

![Cross-case three-floor alignment through QSM, QTE, and FATE](07_cross_case_three_floor_alignment.png)

The direct-channel records remain coherent across all three floors. The El Centro records show a distinct pattern: strong 1F FATE alignment and weak upper-floor alignment. This floor split is consistent across the uncontrolled and passive-off records and should be treated as evidence about signal semantics, not averaged away.

---

## 5. Path and edge-current manifestation

| Case | QSM `J12/J23` | QTE `J12/J23` | FATE `J12/J23` | FATE final `D` | FATE mean `D` | FATE max `D` | FATE work ratio | Max-response floor |
|---|---|---|---|---|---|---|---|---|
| El Centro 0.50 — uncontrolled | 0.997 | 0.983 | 3.763 | 0.140 | 0.435 | 0.692 | 0.507 | 3F |
| El Centro 0.50 — passive-off | 1.001 | 0.970 | 2.010 | 0.150 | 0.210 | 0.421 | 0.555 | 1F |
| Kobe 0.35 — semi-active | 0.998 | 0.958 | 4.392 | 0.543 | 0.368 | 0.619 | 0.611 | 3F |
| Morgan Hill 1.00 — passive-off | 0.992 | 0.958 | 1.368 | 0.079 | 0.205 | 0.462 | 0.552 | 2F |

![Cross-case edge-current concentration ratio](04_cross_case_edge_current_ratio.png)

![Cross-case FATE final path dominance](05_cross_case_fate_path_dominance.png)

### 5.1 QSM and QTE remain near equal

Across all four cases, QSM and QTE edge-current ratios remain close to `1.0`, and QTE final path dominance stays close to zero. The boundary-driven topology does not independently reproduce the sensor-aware internal path.

### 5.2 FATE produces case-specific 1F–2F manifestation

Every FATE case ends with positive `D`, indicating a higher final `1F–2F` path weight. The strength and temporal history differ:

- **Kobe** has the strongest final concentration (`D = 0.543`, edge ratio `4.392`).
- **El Centro uncontrolled** has a modest final value (`0.140`) but the largest sustained mean dominance (`0.435`) among the two El Centro cases.
- **El Centro passive-off** ends at `0.150`, with a sharper mid-record transition and lower edge concentration (`2.010`).
- **Morgan Hill** ends at only `0.079`, while its full history reaches a much stronger intermediate concentration before redistribution.

A common final interface does not imply one common evolution history. The full histories preserve formation, concentration, transition, recovery, and redistribution.

---

## 6. FATE work-compatible manifestation

| Case | 1F ratio | 2F ratio | 3F ratio | Mean ratio | Max-response floor | Max response |
|---|---|---|---|---|---|---|
| El Centro 0.50 — uncontrolled | 0.008 | 0.560 | 0.952 | 0.507 | 3F | 3.658619 |
| El Centro 0.50 — passive-off | 0.010 | 0.703 | 0.952 | 0.555 | 1F | 3.577778 |
| Kobe 0.35 — semi-active | 0.208 | 0.672 | 0.952 | 0.611 | 3F | 4.173876 |
| Morgan Hill 1.00 — passive-off | 0.166 | 0.539 | 0.952 | 0.552 | 2F | 2.804271 |

![Cross-case FATE manifested-work ratio](06_cross_case_fate_manifested_work_ratio.png)

The work-compatible ratios are normalized within each case. They support internal reading of manifestation and unmanifested margin; they do not support claims that one earthquake dissipated an exact physical percentage more energy than another.

The repeated `3F = 0.952` ceiling in the normalized proxy should be read as a normalization-bound behavior of the current implementation, not as an independently calibrated physical efficiency.

---

## 7. Evidence status by method

### 7.1 QSM

Current evidence:

- A clean zero-diagonal input-driven baseline is executable for all four records.
- The boundary-driven stage retains a moderate event envelope (`0.582–0.671` mean absolute correlation).
- Signed alignment remains weak, showing that incoming-wave evolution alone does not reconstruct the internal floor state.

Current boundary:

- V12.2 QSM is a first-stage input-driven evolution, not the sensor-assimilated V11 main probe.
- The release does not demonstrate long-horizon free prediction.

### 7.2 QTE

Current evidence:

- Laplacian topology improves the input-driven envelope in every case.
- Dynamic path and edge-current histories are executable and case-specific.
- QTE remains near equal without the hard as-built field diagonal and without continuous floor-state assimilation.

Current boundary:

- The present graph has only three floor nodes and two inter-floor paths.
- The release does not locate a member-level weak plane.
- The full field-driven Hamiltonian remains a lifecycle extension requiring as-built structural parameters.

### 7.3 FATE

Current evidence:

- Direct-channel Kobe and Morgan Hill reproduce strong sensor-aware one-step alignment using the same method settings.
- All four cases develop a positive sensor-aware 1F–2F path indication.
- Edge current, target hit, work-compatible manifestation, and measured response are retained in one continuous `Aware_power` record.
- El Centro demonstrates that awareness must include the semantic and provenance quality of the sensor state itself.

Current boundary:

- `Alert_control` and `Alive_evolve` are not implemented in this release.
- Path dominance is an observation index, not proof of physical damage.

---

## 8. Relationship to the structural lifecycle

```text
Design stage
  BIM/IFC topology
  → zero-diagonal relational channels
  → topology alternatives

Construction / as-built stage
  actual mass, stiffness, damping, joints, devices, and boundary states
  → field-driven Hamiltonian

Operational Digital Twin stage
  continuous sensing
  → FATE Aware_power
  → future Alert_control
  → future Alive_evolve
```

The four NEES records currently provide retrospective operational observations at floor-domain resolution. They do not yet instantiate the complete design-to-as-built-to-control lifecycle.

---

## 9. How to use the cross-case files

| File | Role |
|---|---|
| `01_cross_case_method_summary.csv` | One row per case × method; canonical stage-level values |
| `02_cross_case_floor_summary.csv` | One row per case × method × floor; canonical floor comparison |
| `03_cross_case_qsm_qte_fate_bar.png` | Stage-wise alignment overview |
| `04_cross_case_edge_current_ratio.png` | Edge-current concentration by stage and case |
| `05_cross_case_fate_path_dominance.png` | FATE final path dominance only |
| `06_cross_case_fate_manifested_work_ratio.png` | FATE manifested-work ratio only |
| `07_cross_case_three_floor_alignment.png` | Three-floor alignment for QSM, QTE, and FATE |
| `08_CROSS_CASE_REPORT.md` | Machine-generated compact report |
| `09_case_registry.json` | Case metadata and method scope |
| `10_cross_case_file_manifest.json` | Cross-case artifact manifest |

Recommended reading order:

```text
03 stage-wise alignment
→ 07 floor-wise alignment
→ 04 edge current
→ 05 path dominance
→ 06 work manifestation
→ individual case README and full-history CSV
```

---

## 10. Main scientific conclusions

1. **The method chain is sequential.** QSM, QTE, and FATE represent increasing structural information, not competing algorithms.
2. **Laplacian topology adds repeatable envelope organization.** QTE improves absolute-envelope alignment in every record relative to zero-diagonal QSM.
3. **Topology alone does not establish the internal path.** QSM and QTE remain near equal in final path and edge-current concentration.
4. **Sensor-state assimilation produces the observed path.** FATE develops positive 1F–2F dominance and edge-current concentration in every case.
5. **Direct-channel replication is strong.** Kobe and Morgan Hill reach FATE mean signed/absolute-envelope correlations of `0.656/0.918` and `0.753/0.952`.
6. **Data semantics are part of the system.** El Centro retains strong 1F alignment and path awareness while exposing upper-floor coordinate and differentiation mismatch.
7. **Final bars are insufficient.** Morgan Hill and El Centro uncontrolled show why mean, maximum, and full path histories must accompany final dominance.
8. **Work proxies and structural loops are supporting evidence.** They connect field observation to measured response without being promoted to absolute energy accounting.

---

## 11. Bounded overall statement

V12.2 provides an executable, traceable four-case observation chain in which zero-diagonal input evolution, Laplacian topology evolution, and sensor-aware FATE manifestation are kept distinct and connected. The strongest present result is the repeatable direct-channel FATE alignment together with case-specific sensor-aware path and edge-current histories. The evidence remains bounded to one-step, floor-domain, retrospective observation without a complete as-built field diagonal or closed-loop control.

## 12. Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. DOI: `10.7277/TPS7-V877`.