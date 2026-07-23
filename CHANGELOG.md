# Changelog

## V12.2 — Three-stage public method chain and complete observation presentation

**Numerical engine:** V12.2  
**Documentation revision:** V12.2  
**Release date:** 2026-07-23

### Method architecture

- Replaced the former five-probe public presentation with the intended sequential chain:

  ```text
  QSM → QTE → FATE
  ```

- Defined QSM as zero-diagonal, fixed-channel, boundary-input Power-state evolution with `H = -W`.
- Defined QTE as Laplacian spatial topology-path evolution with `H = L(W)` and no continuous floor-state assimilation.
- Defined FATE as the sensor-aware stage that continuously assimilates the measured three-floor state and response feedback at `Aware_power`.
- Removed boundary-only, fixed-path, no-feedback, and other sensitivity groups from the public method list.

### Physical observation outputs

- Retained independent physical observations under the relevant method instead of treating them as extra algorithms.
- Restored and standardized per-case figures for:
  - Edge Current Ratio;
  - QTE path-weight evolution;
  - FATE sensor-aware path evolution;
  - QTE/FATE edge-current histories;
  - QTE/FATE path-dominance histories;
  - target-hit and state awareness;
  - work-compatible proxy ratios;
  - acceleration/force–displacement work-loop proxy;
  - downstream response manifestation.
- Standardized the main method figures as one QSM, one QTE, and one FATE three-floor waveform figure per case.
- Split cross-case FATE path dominance and manifested-work ratio into independent figures.
- Restored a cross-case three-floor comparison with separate QSM, QTE, and FATE panels.

### Data and documentation

- Replaced the former case CSV arrangement with:
  - `01_qsm_qte_fate_method_summary.csv`;
  - `02_qsm_qte_fate_floor_summary.csv`;
  - `03_qsm_qte_fate_full_history.csv`.
- Expanded the canonical history to 149 columns while retaining a maximum of 3,000 inspection rows.
- Rewrote all four case READMEs and the cross-case README in one consistent format.
- Updated the English and Traditional Chinese GitHub landing pages to V12.2 filenames, results, method boundaries, lifecycle position, and reproduction instructions.

### Numerical continuity

- V12.1 and V12.2 histories are numerically identical for all four cases across all 149 columns.
- V12.2 FATE mapped core histories are numerically identical to the former V11 principal sensor-assimilated Laplacian histories.
- V12.2 changes organization, artifact completeness, and presentation; it does not silently alter the retained FATE result.

---

## V12.1 — Complete physical observation restoration

- Preserved the sequential QSM→QTE→FATE method architecture introduced in V12.
- Restored physical observation outputs that had been hidden by the four-figure V12 compression.
- Restored Edge Current Ratio, path weights, edge-current histories, path dominance, target hit, work proxies, traditional work loops, and response manifestation.
- Restored the full-history trace with measured and three-stage fields.

---

## V12 — Three-stage method refactor

- Replaced the five parallel observation settings with the intended sequential method architecture.
- Introduced separate QSM, QTE, and FATE execution configurations.
- Standardized stage order and three-floor waveform figures.
- The first V12 presentation over-compressed the independent observation outputs; this was corrected in V12.1.

---

## V11.1 — Theory, implementation, and repository presentation

- Documented the canonical distinction between the Hamiltonian channel law and the Hamiltonian Power operator.
- Aligned the QTE methodological mainline and field-driven Hamiltonian roadmap.
- Documented `Aware_power → Alert_control → Alive_evolve`.
- Added the building-life-cycle interpretation.

---

## V11 — Formal integrated observation release

- Established the first four-case integrated executable observation release.
- Preserved source provenance, timing, case manifests, cross-case summaries, and fixed numerical settings.
- Used a five-probe experimental presentation that was later reorganized in V12.

### Repository layout continuity

- Preserved the established public repository structure: `cases/`, `code/`, `cross_case/`, `data/`, `release_logs/`, and `scripts/`.
- Mapped the V12.2 cross-case artifacts into `cross_case/` rather than publishing the generated output-folder name `00_cross_case/` at the repository root.
- Retained dataset provenance in `data/README.md`, execution history in `release_logs/`, and PowerShell utilities in `scripts/`.
