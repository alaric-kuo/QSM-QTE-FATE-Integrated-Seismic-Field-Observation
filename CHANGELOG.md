# Changelog

## V11.1 — Theory, implementation, and repository presentation

**Documentation revision:** V11.1  
**Numerical engine:** V11  
**Formal numerical outputs:** unchanged

### Theory alignment

- Restored the canonical QSM distinction between the Hamiltonian channel law $\hat H$ and the Hamiltonian Power operator $\hat H_p=-i(\hat H/\hbar)$.
- Documented the QSM evolution $\lvert\Psi(t)\rangle=e^{\hat H_p t}\lvert\Psi(0)\rangle$ and the Power manifestation equation $P(t)=(a\cdot v)\hat H_p\lvert\Psi(t)\rangle$.
- Documented fidelity as the target-state hit ratio and separated it from total Power manifestation.
- Aligned the QTE methodological mainline as `Viewpoint → Topology → Channel → Evolution → Manifestation → Action`.
- Corrected the QTE dataflow to include $\rho(t)$ between $\psi(t)$ and $\Delta V_{\mathrm{resp}}(t)$.
- Documented the bridge from QSM channels to the QTE field-driven Hamiltonian through $V_{\mathrm{bg}}$.
- Documented the FATE sequence `Aware_power → Alert_control → Alive_evolve`.

### Implementation map

- Recorded the empirical complex state compiled from measured displacement, velocity, and acceleration.
- Recorded the numerical evolution `U = exp(-iHΔt)` and its relation to $e^{\hat H_p\Delta t}$ under normalized units.
- Recorded state fidelity, nodal fidelity, target-hit work-compatible reconstruction, edge current, and dynamic floor-path manifestation.
- Marked the present implementation as floor-domain `Aware_power`.
- Identified the open layers: physical Power calibration, member-level topology, background Power field, complete manifestation score, alert control, intervention, and post-intervention re-evolution.

### Building life cycle

- Added design-stage exploration of Power input, geometry, topology, channel continuity, blockage, weak-plane placement, and dissipation alternatives.
- Added as-built and commissioning use of verified geometry, materials, members, joints, devices, and boundary conditions to form field-driven channels.
- Added operation-stage sensing, state correction, feedback, active control, and re-evolution.

### Repository presentation

- Reorganized the repository root around seven public-facing files.
- Consolidated V11 and V11.1 history into this `CHANGELOG.md`.
- Removed local publishing instructions and duplicate release documents from the repository root.
- Improved README equation rendering, matrix rendering, arrow-flow layout, citations, DOI placement, and rights attribution.
- Regenerated `SHA256SUMS.txt` after the final root cleanup.

---

## V11 — Formal integrated observation release

### Method-chain presentation

- Renamed the release to **QSM–QTE–FATE Integrated Seismic Field Observation**.
- Added QSM–QTE–FATE to every case and cross-case figure title.
- Added the integrated method chain to generated CSV tables.
- Renamed the four case CSV files to include `qsm_qte_fate`.

### Interpretation

- Reported QTE as a floor-domain path indication at the available experimental resolution.
- Reported FATE as `Aware_power`.
- Retained displacement as downstream response evidence.
- Used `near-equal / no clear final path indication` for near-zero path dominance.
- Applied one unchanged numerical configuration across all cases without case-specific fitting.

### Timing and provenance

- Added preparation, probe-worker, artifact-generation, and wall-clock timing.
- Added a root release log.
- Added execution timing to each case JSON manifest.
- Preserved source-file and signal-provenance information.

### Numerical engine

- Retained the V10 multi-core process engine.
- Retained chunked C-engine CSV parsing.
- Retained memory-mapped case feature sharing.
- Retained the O(n) running work maximum.
