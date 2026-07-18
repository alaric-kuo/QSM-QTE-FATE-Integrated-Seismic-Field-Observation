# V11.1 Changelog

## QSM–QTE–FATE Integrated Seismic Field Observation

**Release type:** theory-disclosure and implementation-mapping update  
**Numerical engine:** V11, unchanged  
**Formal outputs:** unchanged from V11

## Added

- Full QSM Schrödinger–Hamiltonian formulation.
- Explicit structural state equation and one-step unitary evolution.
- Canonical QSM Power manifestation equation.
- Fidelity, nodal target-state hit ratio, and accumulated hit-work formulation.
- Exact description of the empirical wavefunction compiled from measured `u`, `v`, and `a`.
- Exact description of source injection, one-step prior, comparison, and measurement assimilation.
- Explicit distinction between canonical QSM and the V11 work-compatible experimental operationalization.
- Full QTE floor-domain graph, adjacency, Laplacian, zero-diagonal Hamiltonian, edge-current, adaptive path, and path-dominance equations.
- Explicit statement that the general QTE background-potential field is not yet implemented.
- Full FATE architecture:
  `Aware_power → Alert_control → Alive_evolve`.
- Detailed inventory of the awareness layers currently implemented.
- Explicit statement that control action, topology/Hamiltonian rewrite, post-intervention evolution, and fractal cross-scale recursion are not yet implemented.
- End-to-end algorithm description.
- Theory-to-code function map.
- Separate `THEORY_IMPLEMENTATION_MAP_V11_1.md`.
- Release-ready `RELEASE_NOTES_V11_1.md`.

## Clarified

- `a·v` is a mass-normalized, work-compatible Power-state proxy because the release does not apply floor mass calibration.
- Fidelity is a target-state hit ratio, not total Power or energy.
- The code contains a complex wavefunction and an explicit Schrödinger unitary.
- V11 performs one-step prior evolution followed by measurement assimilation.
- The boundary-input-only probe is a diagnostic reference rather than a same-class physical probe.
- Dynamic QTE path weights are observational state variables and do not represent a physical modification of the experimental structure.
- The hidden-work quantity is a normalized manifestation–response comparison proxy, not proof of unmeasured physical energy.
- Floor-interface indication is not member-level damage localization.
- V11.1 changes documentation and theory visibility; it does not alter the numerical algorithm or formal case outputs.

## Numerical changes

None.

## Output changes

None. The 80 case artifacts, 11 cross-case artifacts, and root execution log remain the formal V11 numerical evidence carried into V11.1.

## Recommended tag

```text
v11.1.0
```
