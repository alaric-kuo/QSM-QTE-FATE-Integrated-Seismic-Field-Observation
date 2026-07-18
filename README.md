# QSM–QTE–FATE Integrated Seismic Field Observation

## NEES-2011-1076 · Formal Release V11

**Initial integrated computational observation and partial validation of Quantum Structural Mechanics (QSM), Quantum Topology Express (QTE), and the `Aware_power` layer of Fractal Alive Topology Evolution (FATE).**

This repository records a four-case seismic experiment on a three-story steel-frame dataset. It connects three previously separate theoretical layers into one reproducible computational chain:

```text
measured structural state
→ QSM one-step power-state evolution
→ QTE floor-domain topology-path indication
→ FATE Aware_power observation
```

The present release is deliberately bounded:

| Theory layer | What V11 currently examines | Current evidence boundary |
|---|---|---|
| **QSM** | One-step structure-coupled `a·v` power-state evolution | Repeated strongly in two direct-channel records; not yet a long-horizon free evolution test |
| **QTE** | Dynamic path-weight and edge-current indication on a three-floor observation graph | Floor-domain only; no complete member-level BIM/IFC or as-built topology |
| **FATE** | `Aware_power`: field, path, response, and data-semantic awareness | `Alert_control` and `Alive_evolve` are not yet implemented |

The central achievement of V11 is therefore not a claim that the full theory has been completed. It is that QSM, QTE, and FATE now leave a **shared, executable, inspectable, and cross-case computational trace**.

---

## Theoretical foundations

This repository operationalizes ideas developed in the following ResearchGate preprints.

### Quantum Structural Mechanics

**Quantum Structural Mechanics: From Stiffness Assets to Value Flow**  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)

QSM treats the structural state as an evolving field rather than only as a collection of stiffness assets and downstream responses. In this release, the work-compatible power-state proxy is:

\[
p_i(t)=a_i(t)v_i(t)
\]

where acceleration and velocity jointly describe the local rate and direction of work-compatible state change.

### Quantum Topology Express

**Quantum Topology Express Method**  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)

QTE observes how an evolving field manifests through topology. The V11 experiment uses a three-node floor-domain graph:

```text
[1F] —— w12 —— [2F] —— w23 —— [3F]
```

with no direct `1F–3F` edge. The path-dominance indicator is:

\[
D_p=\frac{w_{12}-w_{23}}{w_{12}+w_{23}}
\]

A positive value indicates a higher `1F–2F` path weight; a value near zero indicates no clear final path separation.

### Fractal Alive Topology Evolution

**Fractal Alive Topology Evolution**  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

FATE extends observation into an operational survival loop:

```text
Aware_power
→ Alert_control
→ Alive_evolve
```

V11 currently reaches `Aware_power`. It observes the incoming state, structure-coupled field, topology-path history, work-compatible manifestation, downstream response, and—in the El Centro records—the semantic condition of the data itself.

---

## BIM-enabled life-cycle interpretation

The three methods also correspond to different information conditions across a BIM-enabled life cycle.

| Life-cycle condition | Available information | Methodological viewpoint |
|---|---|---|
| Early design | Proposed nodes and relationships; incomplete physical parameters | **QSM zero-diagonal relational transmission** |
| As-built / commissioning | Physicalized nodes, channels, boundaries, and tested system conditions | **QTE Laplacian topology field** |
| Operation / seismic event | Incoming excitation, measured state, intervention, and re-evolution | **FATE operational evolution** |

The zero-diagonal and Laplacian operators are therefore not treated as two arbitrary algorithms competing for the best score.

- The **zero-diagonal operator** isolates inter-node relational transmission.
- The **Laplacian operator** includes node–channel balance in a physicalized topology.
- **FATE** places the observed topology inside an operational loop in which action may later rewrite the field.

In V11, both zero-diagonal and Laplacian floor-state probes are retained to examine whether the same floor-domain tendency remains visible under different operator structures.

---

## Research questions

The formal release asks five narrow questions:

1. Can the current measured floor state evolve into a one-step `a·v` field that aligns with the next measured state?
2. Does floor-state assimilation reveal information that is absent from boundary-input-only evolution?
3. Can the evolving field indicate a persistent or temporary internal floor-domain path?
4. Do path location and maximum downstream displacement describe different observational layers?
5. Can the method reveal when data coordinates, derivation methods, or measurement provenance weaken the physical coherence of the field?

---

## Experimental dataset

All four records come from:

**Zhang, J., Wu, B., and Dyke, S.**  
*RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set].  
NEES / DesignSafe Data Depot.  
DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

The original and converted source records are **not redistributed** in this repository. See [`data/README.md`](data/README.md) for expected filenames and local data placement.

### Four formal cases

| Case | Earthquake | Scale | Control condition | Evidence role |
|---|---|---:|---|---|
| [El Centro 0.50 — uncontrolled](cases/el_centro_050_uncontrolled/) | El Centro | 0.50 | Uncontrolled | Data-semantic stress test; sustained lower-interface tendency |
| [El Centro 0.50 — passive-off](cases/el_centro_050_passive_off/) | El Centro | 0.50 | Passive-off | Data-semantic stress test; abrupt mid-record transition |
| [Kobe 0.35 — semi-active](cases/kobe_035_semi_active/) | Kobe | 0.35 | Semi-active | Initial integrated QSM–QTE–FATE observation record |
| [Morgan Hill 1.00 — passive-off](cases/morgan_hill_100_passive_off/) | Morgan Hill | 1.00 | Passive-off | Cross-scenario replication with a distinct redistribution history |

The four cases form a **partial cross-wave and cross-control robustness matrix**, not a balanced factorial experiment. Only the two El Centro cases hold the earthquake and scale approximately fixed while changing the control condition.

---

## Five observation probes

Every case is processed with the same five probes.

| Probe | Purpose |
|---|---|
| **Laplacian floor-state field probe** | Main integrated QSM–QTE–FATE observation |
| **Zero-diagonal floor-state field probe** | Pure relational-transmission comparison inherited from early QSM |
| **Boundary-input-only diagnostic reference** | Tests what can be observed from the incoming wave without internal floor-state assimilation |
| **Floor-state dynamic path without response feedback** | Tests sensitivity to the current downstream response-feedback term |
| **Fixed-path reference** | Separates QSM one-step field alignment from QTE path adaptation |

These are five computational observation settings, not five physical paths. The present floor graph contains only:

```text
1F–2F
2F–3F
```

All four cases use the same numerical settings and the same initial condition:

\[
w_{12}=w_{23}=1
\]

No case-specific optimizer, grid search, or target-driven parameter fitting is used.

---

## Cross-case findings

A detailed scientific synthesis is available in:

**[Four-Case Scientific Synthesis](cross_case/README.md)**

### 1. QSM repeats strongly in two direct-channel records

Kobe and Morgan Hill use direct analytical displacement, velocity, and acceleration channels on all three floors.

| Case | Boundary-only mean absolute-envelope correlation | Floor-state-assimilated correlation |
|---|---:|---:|
| Kobe 0.35 — semi-active | 0.677 | **0.918** |
| Morgan Hill 1.00 — passive-off | 0.699 | **0.952** |

Under one unchanged V11 configuration, both cases reproduce strong one-step structure-coupled power-state alignment.

![Cross-case a*v alignment by observation mode](cross_case/05_cross_case_mean_abs_correlation.png)

This is the strongest current evidence that QSM has moved beyond a single-case computational result. It remains a one-step evolved-field test and should not be described as unrestricted multi-step prediction.

### 2. Boundary input and internal structural field are distinguishable

Across all four records, boundary-input-only evolution ends near equal path weighting. It does not produce a clear internal final path indication.

After floor-state assimilation, every case ends with a positive `1F–2F` floor-domain indication.

![Cross-case final path indicators](cross_case/07_cross_case_path_dominance.png)

The cross-case result supports the distinction:

```text
incoming seismic wave
≠
field formed after wave–structure coupling
```

### 3. A common interface does not erase event-specific evolution

All four cases indicate the `1F–2F` floor interface, but their histories differ.

```text
El Centro uncontrolled:
early concentration → sustained separation → partial redistribution

El Centro passive-off:
weak separation → abrupt mid-record transition → gradual redistribution

Kobe:
strong and comparatively persistent concentration

Morgan Hill:
strong intermediate concentration → substantial return toward equality
```

The method therefore retains formation, concentration, transition, recovery, and redistribution rather than reducing each event to one final label.

### 4. Edge current provides a second path indicator

The main floor-state edge-current ratio is above one in all four cases:

| Case | RMS edge-current ratio `1F–2F / 2F–3F` |
|---|---:|
| El Centro 0.50 — uncontrolled | 3.763 |
| El Centro 0.50 — passive-off | 2.010 |
| Kobe 0.35 — semi-active | 4.392 |
| Morgan Hill 1.00 — passive-off | 1.368 |

![Cross-case floor-state edge-current ratios](cross_case/08_cross_case_edge_current_ratio.png)

Path weights and edge current are distinct metrics. Their agreement on the lower interface provides mutually supporting floor-domain QTE evidence.

### 5. El Centro exposes the semantic boundary of `a·v`

The El Centro records combine:

```text
1F:
relative displacement

2F and 3F:
absolute displacement

velocity:
numerically differentiated from displacement

acceleration:
directly measured
```

Their Figure 17 work-loop proxies retain a broad restoring-response orientation but contain multiple branches, crossings, and long excursions. These irregularities are not silently removed.

The method preserves possible traces of:

- physical response;
- coordinate choice;
- numerical differentiation;
- sensor and acquisition behavior;
- conversion and processing;
- experimental operation and human intervention.

This does not turn every irregularity into a structural conclusion. It makes the origin and trustworthiness of the observed field part of FATE awareness.

### 6. QSM, QTE, and FATE require separate evidence

The fixed-path and dynamic-path probes produce almost identical one-step absolute-envelope correlations. Therefore:

```text
one-step a·v alignment
→ primarily QSM evidence

path-weight evolution and edge-current concentration
→ QTE evidence
```

Removing response feedback changes the current path indication only slightly. V11 has therefore not yet demonstrated a strong feedback-driven topology rewrite, which is consistent with FATE remaining at `Aware_power`.

---

## Evidence status

### Currently supported

- Repeatable one-step QSM power-state alignment in two direct-channel records.
- Empirical distinction between boundary-input information and a structure-coupled floor-state field.
- Repeated `1F–2F` floor-domain path indication across four records.
- Independent lower-interface tendency in both path weight and edge current.
- Convergence of zero-diagonal and Laplacian probes on the same floor-domain tendency.
- Separation between internal path indication and maximum downstream displacement response.
- Detection of data-semantic inconsistency without automatically discarding irregular traces.
- First integrated computational chain from QSM through QTE to FATE `Aware_power`.

### Not yet established

- Member-, joint-, or component-level topology localization.
- A complete BIM/IFC or as-built structural field.
- Absolute physical power in watts or absolute energy dissipation percentages.
- Damage probability or verified weak-plane identification.
- Multi-step free evolution without intermediate assimilation.
- Causal separation of earthquake-wave and control-mode effects across all four cases.
- FATE `Alert_control`.
- FATE `Alive_evolve` after a topology or Hamiltonian rewrite.
- Universal validity across structural systems.

---

## Repository structure

```text
QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
├── README.md
├── CITATION.cff
├── V11_CHANGELOG.md
├── QA_REGRESSION.md
├── requirements.txt
├── code/
│   └── qsm_qte_fate_nees_multicase_release_v11.py
├── scripts/
│   ├── run_all_cases_v11_ascii_path.ps1
│   └── run_smoke_test_morgan_v11_ascii_path.ps1
├── data/
│   └── README.md
├── cases/
│   ├── el_centro_050_uncontrolled/
│   ├── el_centro_050_passive_off/
│   ├── kobe_035_semi_active/
│   └── morgan_hill_100_passive_off/
├── cross_case/
│   ├── README.md
│   └── 11 formal cross-case artifacts
└── release_logs/
    └── 00_RELEASE_RUN_LOG.txt
```

Each case folder contains 20 formal artifacts:

```text
4 CSV evidence tables / histories
2 generated text reports
12 PNG figures
1 execution log
1 JSON provenance manifest
```

The full formal release contains:

```text
80 case artifacts
11 cross-case artifacts
1 root execution log
= 92 generated files
```

---

## Reproducing V11

### Requirements

- Python 3.10 or later
- NumPy
- pandas
- Matplotlib

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

The original formal run used a Conda environment named `ifcman`.

### Expected local data files

Place the following converted files in a local data directory:

```text
elcentro_0p50_07312012_unc_donghua_converted.csv
elcentro_0p50_07312012_poff_donghua_converted.csv
kobe_035_semi_active_avg_converted.csv
morgan_1_p_off_avg_converted.csv
```

### Direct execution

```powershell
python .\code\qsm_qte_fate_nees_multicase_release_v11.py `
    --root "D:\path\to\Data Source" `
    --out ".\outputs_qsm_qte_fate_nees_2011_1076_v11" `
    --stride 5 `
    --workers 8 `
    --prepare-workers 2 `
    --chunk-rows 200000
```

### Windows paths containing Chinese characters

The formal run used temporary drive mappings so that Conda received ASCII-only paths:

```powershell
$RepoRoot = (Get-Location).Path
$DataRoot = "D:\path\to\Data Source"
$Conda = "D:\Application\miniconda3\Scripts\conda.exe"

cmd /c "subst Q: /d" 2>$null | Out-Null
cmd /c "subst S: /d" 2>$null | Out-Null

try {
    cmd /c "subst Q: `"$RepoRoot`""
    cmd /c "subst S: `"$DataRoot`""

    & $Conda run -n ifcman python `
        "Q:\code\qsm_qte_fate_nees_multicase_release_v11.py" `
        --root "S:\" `
        --out "Q:\outputs_qsm_qte_fate_nees_2011_1076_v11" `
        --stride 5 `
        --workers 8 `
        --prepare-workers 2 `
        --chunk-rows 200000
}
finally {
    cmd /c "subst Q: /d" 2>$null | Out-Null
    cmd /c "subst S: /d" 2>$null | Out-Null
}
```

---

## Formal execution record

The formal V11 four-case release used:

```text
24 logical processors
2 CSV preparation workers
8 parallel probe workers
20 probe tasks
```

Recorded timing:

| Phase | Time |
|---|---:|
| Data reading and case-field preparation | 3.2 s |
| Parallel QSM–QTE–FATE probes | 19.9 s |
| Case and cross-case artifact generation | 13.6 s |
| Internal V11 wall-clock time | 36.8 s |
| End-to-end PowerShell time | 39.17 s |

Probe-worker times are recorded separately in every case log. Because probes run concurrently, their sum is a computational-load indicator rather than wall-clock time.

V11 retains the V10 numerical evolution settings. Regression checks on Kobe and Morgan Hill found only floating-point-scale numerical differences:

```text
Kobe:        4.18 × 10⁻14
Morgan Hill: 1.53 × 10⁻13
```

---

## How to cite

### Theoretical preprints

Kuo, Han-Jung (Alaric).  
*Quantum Structural Mechanics: From Stiffness Assets to Value Flow.*  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)

Kuo, Han-Jung (Alaric).  
*Quantum Topology Express Method.*  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)

Kuo, Han-Jung (Alaric).  
*Fractal Alive Topology Evolution.*  
ResearchGate preprint.  
DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

### Experimental dataset

Zhang, J., Wu, B., and Dyke, S.  
*RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set].  
NEES / DesignSafe Data Depot.  
DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

### Software release

Use the repository's [`CITATION.cff`](CITATION.cff) for the formal software citation.

---

## Bounded scientific statement

> Under one unchanged V11 computational configuration, two direct-channel earthquake records reproduce strong one-step QSM power-state alignment, while all four records distinguish boundary input from a floor-state-assimilated internal path indication. The four cases repeatedly indicate the `1F–2F` floor interface, but preserve different concentration and redistribution histories. The El Centro records further show that signal provenance and coordinate semantics materially affect `a·v` coherence. Together, the results provide preliminary cross-case evidence for QSM field evolution, floor-domain QTE path manifestation, and the `Aware_power` layer of FATE, while leaving member-level topology validation and closed-loop FATE intervention unresolved.

---

## Release status

**Formal Release V11**

This repository is the first integrated public computational record of:

```text
QSM
→ QTE
→ FATE Aware_power
```

It is not the endpoint of the theory.

It is the point at which the theory becomes reproducible, inspectable, and open to independent evaluation.
