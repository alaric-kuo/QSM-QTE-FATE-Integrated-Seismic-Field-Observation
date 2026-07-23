# QSM–QTE–FATE Integrated Seismic Field Observation

## NEES-2011-1076 — Formal Release V12.2

[繁體中文](README_ZH-TW.md)

**Author and theory developer:** Dr. Han-Jung (Alaric) Kuo  
**Organization:** A&J Management Consulting Limited Company  
**Numerical engine:** V12.2  
**Documentation revision:** V12.2

> **One sequential method chain; complete physical observation outputs.**

```text
RPG → QSM → QTE → FATE
```

This repository applies the QSM–QTE–FATE framework to four archived records from the NEES-2011-1076 three-story steel-frame experiment. It asks a direct engineering question:

> **When earthquake motion enters a structure, how does the Power state evolve, how does the spatial path become organized, and what becomes visible after the measured structural state continuously enters the observation?**

V12.2 is organized around three successive methods only:

```text
QSM → QTE → FATE
```

The previous five-probe presentation is no longer used. Edge current, path dominance, target hit, work-compatible proxies, acceleration/force–displacement work loops, and response manifestation remain in the release because they are independent physical observations—not extra algorithms and not sensitivity groups.

---

# 1. Start here: what V12.2 actually implements

| Stage | V12.2 operator and information state | Present role |
|---|---|---|
| **QSM** | `H = -W`; zero diagonal; fixed relational channels; boundary input | Evolves the input-driven Power state through non-diagonal structural relations |
| **QTE** | `H = L(W)`; Laplacian diagonal restored; dynamic path; boundary input | Adds spatial topology and observes path-weight and edge-current evolution |
| **FATE** | QTE evolution + continuous three-floor state assimilation + response feedback | Forms sensor-aware `Aware_power`, including path, target hit, work-compatible manifestation, and response |

The stages are sequential and receive different information. Their correlations are therefore **not a leaderboard between three competing prediction models**.

The current QTE execution is a **topology-only floor-domain implementation**. It does not claim that a complete as-built field diagonal containing physical mass, stiffness, damping, member capacities, joints, damage states, and control-device states has already been inserted.

The complete future QTE field-driven Hamiltonian is represented conceptually as:

$$
H_{QTE}=\kappa L_{\mathrm{geo}}(W)+\alpha_v\operatorname{diag}(V_{\mathrm{bg}})
$$

V12.2 currently executes the first term at the available three-floor resolution.

---

# 2. Main four-case results

## 2.1 Stage-wise one-step observation alignment

Values are reported as:

```text
mean signed correlation / mean absolute-envelope correlation
```

| Case | QSM | QTE | FATE | QSM→QTE Δabs | QTE→FATE Δabs |
|---|---:|---:|---:|---:|---:|
| El Centro 0.50 — uncontrolled | -0.135 / 0.671 | -0.039 / 0.765 | 0.323 / 0.615 | +0.094 | -0.150 |
| El Centro 0.50 — passive-off | 0.002 / 0.617 | 0.037 / 0.737 | 0.258 / 0.589 | +0.121 | -0.148 |
| Kobe 0.35 — semi-active | 0.065 / 0.582 | -0.016 / 0.677 | **0.656 / 0.918** | +0.095 | +0.242 |
| Morgan Hill 1.00 — passive-off | 0.049 / 0.604 | 0.046 / 0.699 | **0.753 / 0.952** | +0.095 | +0.253 |

![Cross-case QSM-QTE-FATE stage-wise alignment](cross_case/03_cross_case_qsm_qte_fate_bar.png)

The repeated QSM→QTE increase indicates that the Laplacian topology organizes the event envelope before continuous floor-state assimilation. Signed correlations remain close to zero at QSM and QTE, showing that boundary-driven evolution alone does not reconstruct the internal floor-specific direction and phase.

Kobe and Morgan Hill use direct analytical displacement, velocity, and acceleration channels on all floors. When those measured floor states continuously enter FATE, the mean absolute-envelope correlations rise to `0.918` and `0.952`.

The two El Centro records use mixed displacement coordinates—1F relative, 2F and 3F absolute—and velocity differentiated from displacement. Their FATE mean-envelope correlations decrease while the 1F signed and envelope alignment remain substantially stronger than the upper-floor values. This is retained as a **data-semantic observation**, not averaged away.

## 2.2 Floor-wise FATE alignment

| Case | 1F signed/abs | 2F signed/abs | 3F signed/abs |
|---|---:|---:|---:|
| El Centro 0.50 — uncontrolled | 0.778 / 0.900 | 0.093 / 0.477 | 0.097 / 0.469 |
| El Centro 0.50 — passive-off | 0.680 / 0.799 | 0.053 / 0.501 | 0.040 / 0.468 |
| Kobe 0.35 — semi-active | 0.567 / 0.851 | 0.709 / 0.949 | 0.693 / 0.955 |
| Morgan Hill 1.00 — passive-off | 0.733 / 0.907 | 0.785 / 0.974 | 0.740 / 0.974 |

![Cross-case three-floor alignment](cross_case/07_cross_case_three_floor_alignment.png)

## 2.3 Sensor-aware path manifestation

| Case | FATE final dominance `D` | FATE mean `D` | FATE maximum `D` | FATE edge-current ratio `J12/J23` | Mean manifested-work ratio |
|---|---:|---:|---:|---:|---:|
| El Centro 0.50 — uncontrolled | 0.140 | 0.435 | 0.692 | 3.763 | 0.507 |
| El Centro 0.50 — passive-off | 0.150 | 0.210 | 0.421 | 2.010 | 0.555 |
| Kobe 0.35 — semi-active | **0.543** | 0.368 | 0.619 | **4.392** | **0.611** |
| Morgan Hill 1.00 — passive-off | 0.079 | 0.205 | 0.462 | 1.368 | 0.552 |

![Cross-case Edge Current Ratio](cross_case/04_cross_case_edge_current_ratio.png)

![Cross-case FATE final path dominance](cross_case/05_cross_case_fate_path_dominance.png)

QSM and QTE remain near equal in path weighting and edge-current ratio under boundary-driven observation. A positive `1F–2F` path indication appears in all four FATE cases after measured floor states enter the field. The temporal histories are not identical:

- **Kobe:** strong and comparatively persistent lower-interface concentration.
- **Morgan Hill:** stronger intermediate concentration followed by substantial redistribution; the final value alone understates the event history.
- **El Centro uncontrolled:** sustained concentration with a modest final return.
- **El Centro passive-off:** sharper mid-record transition and later redistribution.

This is a floor-domain path manifestation. It is not yet independent proof of a member-level damage plane.

## 2.4 Work-compatible manifestation

![Cross-case FATE manifested-work ratio](cross_case/06_cross_case_fate_manifested_work_ratio.png)

The work-compatible ratios are normalized within each case. They support internal reading of manifested and unmanifested proxy capacity; they are **not physical energy percentages for direct comparison between earthquakes**. The repeated 3F ceiling in the current normalization is documented as an implementation-bound behavior rather than an independently calibrated efficiency.

---

# 3. Theoretical and engineering chain

## 3.1 RPG: directly calculable unit-Power language

The theoretical lineage begins with Resonance Power Gradient Theory:

$$
\frac{1}{m}\frac{dm}{dt}=\frac{a\cdot v}{c^2}
$$

At the engineering observation level used here:

$$
\frac{P}{m}=a\cdot v
$$

The NEES release does not provide the physical floor masses required for absolute watts. V12.2 therefore retains `a·v` as a mass-normalized, work-compatible Power-state quantity. It is the direct calculable expression used by the model, not merely a plotting convenience.

The connection to conventional structural dynamics begins from:

$$
m\ddot{x}+c\dot{x}+kx=f(t)
$$

Multiplying by velocity produces the instantaneous Power balance between kinetic change, elastic storage, damping dissipation, and external input. Figure `17_force_displacement_work_loop_proxy.png` is retained in every case as the traditional structural-mechanics entrance to that Power reading.

## 3.2 QSM: zero-diagonal Hamiltonian Power-state evolution

QSM removes the diagonal self-wells and exposes non-diagonal structural relations:

$$
H_{QSM}=-W
$$

Under normalized units, the code evolves the complex structural state through:

$$
U(\Delta t)=e^{-iH\Delta t}
$$

The current V12.2 QSM stage is deliberately clean:

```text
boundary input
→ zero-diagonal relational Hamiltonian
→ one-step Power-state evolution
```

It establishes what the incoming excitation can carry through the relational channel structure before topology and continuous sensing are added.

## 3.3 QTE: Laplacian spatial topology-path evolution

QTE restores the Laplacian diagonal:

$$
L(W)=D(W)-W
$$

and currently executes:

$$
H_{QTE}=L(W)
$$

The two observable floor-domain paths are:

```text
[1F] —— w12 —— [2F] —— w23 —— [3F]
```

with:

$$
w_{12}+w_{23}=2
$$

and path dominance:

$$
D_p(t)=\frac{w_{12}(t)-w_{23}(t)}{w_{12}(t)+w_{23}(t)}
$$

QTE also observes edge current:

$$
J_{ij}(t)=2\,\operatorname{Im}\left(\psi_i^*(t)H_{ij}\psi_j(t)\right)
$$

V12.2 preserves path-weight, dominance, and edge-current histories as separate physical observations.

## 3.4 FATE: sensor-aware evolution

FATE does not introduce a fourth competing Hamiltonian. It places continuously measured structural state into the QSM–QTE evolution chain:

```text
sensor state at t
→ update Ψ(t)
→ evolve topology and path
→ observe target hit, edge current, work proxy, residual, and response
→ assimilate the next measured state
```

The implemented layer is:

```text
Aware_power
```

The future sequence remains:

```text
Aware_power → Alert_control → Alive_evolve
```

V12.2 does not claim an automated alarm threshold, a completed control action, or post-intervention closed-loop re-evolution.

---

# 4. Building-life-cycle position

The three methods form a life-cycle progression rather than isolated software modules.

## Design

BIM/IFC geometry and structural relations can be compiled into nodes, adjacency, and candidate channels. QSM can expose non-diagonal transmission relations; QTE can examine how alternative topologies permit concentration, blockage, reflection, and dissipation.

## Construction, as-built, and commissioning

Verified member properties, mass, stiffness, damping, joints, devices, boundaries, installation state, and commissioning results can form the background field `V_bg`. This is the stage at which the complete field-driven Hamiltonian becomes possible:

$$
H=\kappa L_{\mathrm{geo}}+\alpha_v\operatorname{diag}(V_{\mathrm{bg}})
$$

## Operation and Digital Twin

Sensors continuously update the observed state and path. FATE then provides the path from Power awareness to control strategy, intervention, and re-evolution. The intended operational chain is:

```text
BIM/IFC topology
→ as-built field-driven Hamiltonian
→ live sensing
→ Digital Twin awareness
→ control strategy
→ measured post-intervention re-evolution
```

The present NEES release is a retrospective operation-stage floor-domain observation using archived sensing.

---

# 5. Experimental records and provenance

| Case | Source file | Signal condition | Rows loaded after stride | Waveform event window |
|---|---|---|---:|---|
| El Centro 0.50 — uncontrolled | `elcentro_0p50_07312012_unc_donghua_converted.csv` | 1F relative displacement; 2F–3F absolute displacement; velocity derived | 203,578 | 51.152400–165.785600 s |
| El Centro 0.50 — passive-off | `elcentro_0p50_07312012_poff_donghua_converted.csv` | Same mixed coordinate structure; velocity derived | 117,271 | 1.609550–115.161450 s |
| Kobe 0.35 — semi-active | `kobe_035_semi_active_avg_converted.csv` | Direct analytical `u`, `v`, `a` on all floors | 16,287 | 7.597168–31.025879 s |
| Morgan Hill 1.00 — passive-off | `morgan_1_p_off_avg_converted.csv` | Direct analytical `u`, `v`, `a` on all floors | 16,202 | 4.754883–16.700195 s |

Dataset:

> Zhang, J., Wu, B., and Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)*. DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

The original NEES data and converted source CSV files are not redistributed in this repository.

---

# 6. Repository reading order

## Cross-case synthesis

- [`cross_case/README.md`](cross_case/README.md) — four-case scientific interpretation.
- `01_cross_case_method_summary.csv` — one row per case and stage.
- `02_cross_case_floor_summary.csv` — one row per case, stage, and floor.
- Figures `03–07` — stage alignment, edge current, path dominance, work manifestation, and three-floor comparison.

## Case-level records

- [El Centro 0.50 — uncontrolled](cases/el_centro_050_uncontrolled/README.md)
- [El Centro 0.50 — passive-off](cases/el_centro_050_passive_off/README.md)
- [Kobe 0.35 — semi-active](cases/kobe_035_semi_active/README.md)
- [Morgan Hill 1.00 — passive-off](cases/morgan_hill_100_passive_off/README.md)

Every case uses the same 20-file generated format plus one narrative README.

<details>
<summary>Per-case V12.2 filenames</summary>

```text
01_qsm_qte_fate_method_summary.csv
02_qsm_qte_fate_floor_summary.csv
03_qsm_qte_fate_full_history.csv
04_CASE_REPORT.md
05_release_report.txt
06_qsm_qte_fate_stage_bar.png
07_qsm_three_floor_waveforms.png
08_qte_three_floor_waveforms.png
09_fate_three_floor_waveforms.png
10_qsm_qte_fate_edge_current_ratio.png
11_qte_path_weight_evolution.png
12_fate_sensor_aware_path_evolution.png
13_qte_fate_edge_current_evolution.png
14_qte_fate_path_dominance_evolution.png
15_fate_target_hit_state_awareness.png
16_fate_work_proxy_ratios_by_floor.png
17_force_displacement_work_loop_proxy.png
18_response_manifestation_by_floor.png
19_release_run_log.txt
20_release_file_manifest.json
README.md
```

</details>

`03_qsm_qte_fate_full_history.csv` contains 149 columns and is downsampled to at most 3,000 rows for GitHub inspection. It retains measured channels, all three stages, residuals, target hit, cumulative work-compatible quantities, path weights, path dominance, edge currents, state fidelity, and residual norm.

---

# 7. Reproduction

## 7.1 Requirements

```powershell
conda activate ifcman
pip install -r requirements.txt
```

The tested dependencies are NumPy, pandas, and Matplotlib.

## 7.2 Expected local layout

```text
<base folder>/
├─ QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
│  ├─ code/
│  ├─ scripts/
│  │  ├─ run_all_cases_v12_2.ps1
│  │  ├─ run_smoke_test_morgan_v12_2.ps1
│  │  └─ update_sha256_from_git.ps1
│  └─ ...
└─ Data Source/
   ├─ elcentro_0p50_07312012_unc_donghua_converted.csv
   ├─ elcentro_0p50_07312012_poff_donghua_converted.csv
   ├─ kobe_035_semi_active_avg_converted.csv
   └─ morgan_1_p_off_avg_converted.csv
```

Run all four cases:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\run_all_cases_v12_2.ps1
```

The default result folder is created beside the repository:

```text
outputs_qsm_qte_fate_nees_2011_1076_v12_2
```

Direct Python execution:

```powershell
python .\code\qsm_qte_fate_nees_multicase_release_v12_2.py `
  --root "D:\path\to\Data Source" `
  --out "D:\path\to\outputs_qsm_qte_fate_nees_2011_1076_v12_2" `
  --stride 5 `
  --workers 8 `
  --prepare-workers 2 `
  --chunk-rows 200000
```

---

# 8. Formal run and quality assurance

The formal V12.2 run completed all four records with one unchanged configuration:

```text
24 logical processors
2 CSV preparation workers
8 parallel method workers
12 method tasks
42.881 s total internal elapsed time
```

The numerical engine generated:

```text
4 cases × 20 generated files = 80
10 cross-case generated files = 10
1 root release log = 1
Total formal generated artifacts = 91
```

The five narrative READMEs are maintained separately for interpretation.

Regression checks confirm:

- V12.1 and V12.2 share identical 149-column histories for all four cases; maximum numerical difference is `0`.
- The V12.2 FATE core histories match the former V11 principal sensor-assimilated Laplacian histories for the mapped state, target-hit, path-weight, fidelity, residual, displacement, and hidden-work fields; maximum numerical difference is `0`.
- V12.2 changes method organization and cross-case presentation; it does not silently change the retained FATE result.

See [`QA_REGRESSION.md`](QA_REGRESSION.md) for scope and details.

---

# 9. Evidence boundary

## Currently supported by this executable release

- A clean QSM zero-diagonal input-driven baseline for four records.
- Repeatable QSM→QTE absolute-envelope organization under the Laplacian topology.
- Strong sensor-aware one-step FATE alignment in two direct-channel records.
- Explicit visibility of mixed coordinate and derived-velocity limitations in the El Centro records.
- Floor-domain path-weight, edge-current, target-hit, work-compatible, and response histories.
- A recurring sensor-aware `1F–2F` path indication with case-specific temporal evolution.
- Reproducible code, fixed settings, source provenance, logs, summaries, figures, and file manifests.

## Not yet established

- Absolute watts or joules without physical floor mass and calibrated channel quantities.
- Member-level damage localization or independently verified weak-plane identification.
- A complete as-built `V_bg` field-driven Hamiltonian.
- Long-horizon autonomous prediction without measurement update.
- Automated `Alert_control` criteria.
- Closed-loop intervention and `Alive_evolve` verification.
- Universal structural validity beyond the current experimental records.

---

# 10. Version history and citation

V12.2 replaces the five-probe public presentation with the intended sequential method chain and retains all independent physical observation outputs. See [`CHANGELOG.md`](CHANGELOG.md).

Please cite the original dataset, the theoretical works, and this software release. Machine-readable citation metadata is provided in [`CITATION.cff`](CITATION.cff).

Theoretical references:

- Kuo, H.-J. *Quantum Structural Mechanics: From Stiffness Assets to Value Flow*. DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)
- Kuo, H.-J. *Quantum Topology Express Method*. DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)
- Kuo, H.-J. *Fractal Alive Topology Evolution*. DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

File integrity hashes are listed in [`SHA256SUMS.txt`](SHA256SUMS.txt).
