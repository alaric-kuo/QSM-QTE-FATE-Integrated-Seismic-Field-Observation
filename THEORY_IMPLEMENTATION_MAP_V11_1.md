# Theory–Implementation Map — V11.1

## QSM–QTE–FATE Integrated Seismic Field Observation

**Release:** V11.1  
**Numerical engine:** V11, unchanged  
**Purpose:** make the theoretical objects, numerical operationalization, outputs, and unresolved layers readable in one audit document.

This document does not introduce a new numerical result. It explains what the existing code actually computes and how each computation relates to Quantum Structural Mechanics (QSM), Quantum Topology Express (QTE), and Fractal Alive Topology Evolution (FATE).

---

# 1. Status vocabulary

| Status | Meaning |
|---|---|
| **Implemented** | A corresponding code object and output exist in the V11 numerical engine. |
| **Implemented as proxy** | A computational quantity exists, but it is work-compatible or normalized rather than an absolute physical quantity. |
| **Partially implemented** | The release implements a bounded operational form of a broader theoretical object. |
| **Not implemented** | The theoretical object does not yet have a code path in this release. |
| **Not established** | The code may produce a related quantity, but the present dataset or experiment does not verify the claimed physical meaning. |

---

# 2. QSM map

## 2.1 Canonical state evolution

The canonical QSM evolution is:

$$
i\hbar\frac{\partial}{\partial t}|\Psi(t)\rangle
=
\hat H_p(t)|\Psi(t)\rangle
$$

and, for a discrete step:

$$
|\Psi(t+\Delta t)\rangle
=
\exp\!\left(
-\frac{i}{\hbar}\hat H_p(t)\Delta t
\right)
|\Psi(t)\rangle
$$

The V11 engine sets $\hbar=1$ and computes:

$$
U_k=e^{-iH_k\Delta t}
$$

through eigendecomposition of a real symmetric $3\times3$ Hamiltonian.

| Theory object | Code location | Code object | Status |
|---|---|---|---|
| Structural state $|\Psi\rangle$ | QSM core | `psi`, `psi_meas`, `psi_prior` | **Implemented** |
| Hamiltonian $H$ | `build_path_operator(...)` | `H` | **Implemented** |
| Unitary $U=e^{-iH\Delta t}$ | `build_path_operator_and_unitary(...)` | `U` | **Implemented** |
| Autonomous long-horizon evolution | `run_probe(...)` | no autonomous full-record branch | **Not implemented** |
| One-step prior followed by assimilation | `run_probe(...)` | `psi_prior`, residual update | **Implemented** |

## 2.2 Empirical measured wavefunction

The code maps measured floor motion into a complex state.

For each floor $i$:

$$
E_i
=
\tilde v_i^2
+
(\bar\omega_i\tilde u_i)^2
+
0.25\tilde a_i^2
+
\varepsilon
$$

$$
A_i
=
\sqrt{\frac{E_i}{\sum_jE_j}}
$$

$$
\theta_i
=
\operatorname{atan2}
(\bar\omega_i\tilde u_i,\tilde v_i)
$$

$$
\Psi_i^{meas}=A_ie^{i\theta_i}
$$

| Theory role | Code expression | Status | Boundary |
|---|---|---|---|
| State amplitude | `amp = sqrt(energy / sum(energy))` | **Implemented** | empirical normalized intensity, not absolute energy |
| State phase | `phase = atan2(omega_norm*u_norm, v_norm)` | **Implemented** | displacement–velocity phase construction |
| Complex floor state | `psi = amp * exp(1j*phase)` | **Implemented** | three-floor state only |
| Member-level state | none | **Not implemented** | no member-level sensor/BIM graph |
| Alternative calibrated wavefunction | none | **Not implemented** | current formula is one operationalization |

## 2.3 Power-state source and one-step prior

The local work-compatible proxy is:

$$
p_i(t)=a_i(t)v_i(t)
$$

The source uses normalized `a·v` magnitude, sign, and measured phase:

$$
s_{i,k}
=
\sqrt{|\tilde p_{i,k}|}
e^{i(\theta_{i,k}+\pi\mathbf 1_{p_{i,k}<0})}
$$

The one-step prior is:

$$
|\Psi^-_{k+1}\rangle
=
\mathcal N
\left[
U_k
\left(
|\Psi_k\rangle
+
g_s\Delta t|s_k\rangle
\right)
\right]
$$

with:

$$
g_s=0.08
$$

| Mode | Source information used | Assimilation after comparison |
|---|---|---|
| Floor-state assimilated | all three floor `a·v` source components | $g_m=0.20$ |
| Boundary-input-only | first-floor boundary source only | measurement gain forced to zero |

The boundary-input-only mode is a diagnostic reference. It is not the same observational class as the floor-state-assimilated field.

## 2.4 Fidelity

State fidelity:

$$
F_{\mathrm{state},k+1}
=
\left|
\langle\Psi^{meas}_{k+1}|\Psi^-_{k+1}\rangle
\right|^2
$$

Nodal fidelity:

$$
F_{i,k+1}=|\Psi^-_{i,k+1}|^2
$$

| Quantity | Code | Status |
|---|---|---|
| State overlap | `state_fidelity` | **Implemented** |
| Floor target-state hit ratio | `fid = abs(psi_prior)**2` | **Implemented** |
| Arbitrary structural target vector | no general target API | **Partially implemented** |
| Verified damage-state probability | none | **Not established** |

## 2.5 Canonical Power manifestation and current operationalization

Canonical QSM:

$$
\mathbf P(t)
=
(a\cdot v)\hat H_p|\Psi(t)\rangle
$$

V11 operationalization:

$$
P_{\mathrm{scale},k}
=
\sum_i|a_{i,k}v_{i,k}|
$$

or, for the boundary reference:

$$
P_{\mathrm{scale},k}^{boundary}
=
|a_{1,k}v_{1,k}|
$$

Then:

$$
\widehat p_{i,k+1|k}
=
P_{\mathrm{scale},k}
F_{i,k+1}
\operatorname{sign}
[-\sin(2\arg\Psi^-_{i,k+1})]
$$

| QSM object | Code | Status | Interpretation |
|---|---|---|---|
| Local `a·v` | `p_av = a*v` | **Implemented as proxy** | mass-normalized, work-compatible |
| Direct operator-valued $\mathbf P=(a\cdot v)H\Psi$ | no direct exported physical vector | **Partially implemented** | operator evolution is present; observable projection uses nodal fidelity |
| One-step manifested floor field | `evolved_av_next` | **Implemented as proxy** | prediction/observation target for next measured `a·v` |
| Signed manifestation residual | `evolved_av_next_residual` | **Implemented** | next measured field minus one-step evolved field |
| Physical watts | none | **Not implemented** | floor masses/calibration absent |

## 2.6 Work-compatible accumulation

The code records:

$$
p_{\mathrm{hit},i}=|\widehat p_i|
$$

$$
W_{\mathrm{hit},i}(T)
=
\int_0^T p_{\mathrm{hit},i}(t)\,dt
$$

and separate positive and negative directional accumulations.

| Quantity | Code | Status |
|---|---|---|
| Absolute hit-work proxy | `w_hit` | **Implemented as proxy** |
| Positive directional accumulation | `pos_hit_work` | **Implemented as proxy** |
| Negative directional accumulation | `neg_hit_work` | **Implemented as proxy** |
| Measured absolute `a·v` work proxy | `measured_abs_work` | **Implemented as proxy** |
| Measured signed `a·v` work proxy | `measured_signed_work` | **Implemented as proxy** |
| Physical energy dissipation | none | **Not established** |

---

# 3. QTE map

## 3.1 Viewpoint and topology

The implemented viewpoint is fixed:

```text
1F — 2F — 3F
```

The adjacency matrix is:

$$
W=
\begin{bmatrix}
0&w_{12}&0\\
w_{12}&0&w_{23}\\
0&w_{23}&0
\end{bmatrix}
$$

The Laplacian is:

$$
L=D-W
$$

The two implemented Hamiltonians are:

$$
H_L=L
$$

and:

$$
H_Z=-W
$$

| QTE object | Code | Status | Boundary |
|---|---|---|---|
| Viewpoint | hard-coded floor graph | **Implemented, fixed** | no viewpoint compiler |
| Topology nodes | `FLOORS` | **Implemented** | three floor nodes |
| Edges | `w12`, `w23` | **Implemented** | no `1F–3F` edge |
| Laplacian field | `operator_key="laplacian"` | **Implemented** | floor domain |
| Zero-diagonal relational field | `operator_key="zero_diagonal"` | **Implemented** | floor domain |
| Background potential $V_{bg}$ | none | **Not implemented** | no separate diagonal potential field |
| BIM/IFC member graph | none | **Not implemented** | absent from dataset model |

## 3.2 Edge current

The code computes:

$$
J_{12}
=
2\operatorname{Im}
(\Psi_1^*H_{12}\Psi_2)
$$

$$
J_{23}
=
2\operatorname{Im}
(\Psi_2^*H_{23}\Psi_3)
$$

| Object | Code | Status |
|---|---|---|
| Instantaneous lower-edge current | `j12_hist` | **Implemented** |
| Instantaneous upper-edge current | `j23_hist` | **Implemented** |
| Record-level current ratio | summary output | **Implemented** |
| Member-level current field | none | **Not implemented** |

## 3.3 Dynamic path update

The code updates:

$$
\widetilde w_{ij,k+1}
=
(1-\lambda\Delta t)w_{ij,k}
+
\alpha_J|J_{ij,k}|\Delta t
+
\alpha_P\Delta P_{ij,k}\Delta t
+
\alpha_R\Delta r_{ij,k}\Delta t
+
\alpha_H\Delta h_{ij,k}\Delta t
$$

with:

| Parameter | Value |
|---|---:|
| $\lambda$ | 0.02 |
| $\alpha_J$ | 0.15 |
| $\alpha_P$ | 0.30 |
| $\alpha_R$ | 0.06 |
| $\alpha_H$ | 0.05 |

The weights are normalized to:

$$
w_{12}+w_{23}=2
$$

| Driver | Code expression | Status |
|---|---|---|
| Current concentration | `abs(j12)`, `abs(j23)` | **Implemented** |
| Power-state gradient | `dP12`, `dP23` | **Implemented** |
| Assimilation-residual gradient | `r12`, `r23` | **Implemented** |
| Hidden-work/response gradient | `h12`, `h23` | **Implemented, optional** |
| Path decay | `path_decay` | **Implemented** |
| Physical intervention in the real structure | none | **Not implemented** |

The dynamic weights are observational state variables. Their evolution does not mean that the physical steel frame was altered during post-processing.

## 3.4 Path manifestation

$$
D_p
=
\frac{w_{12}-w_{23}}{w_{12}+w_{23}}
$$

| Output | Meaning |
|---|---|
| `w12_hist`, `w23_hist` | evolving relative path weights |
| `path_dominance` | normalized lower-vs-upper edge tendency |
| final path label | cautious floor-interface indication |
| mean path dominance | persistence over the record |
| full history | formation, concentration, transition, recovery, redistribution |

A floor-interface indication is not a verified member-level damage location.

---

# 4. FATE map

## 4.1 Full operational architecture

```text
Aware_power
→ Alert_control
→ Alive_evolve
```

The intended full loop requires:

1. observe the incoming Power and formed field;
2. identify path concentration, blockage, or dangerous target-state alignment;
3. determine whether an alert or intervention is justified;
4. modify a control state, topology, boundary, or Hamiltonian;
5. re-evolve the field;
6. compare survival, release, redistribution, or failure outcomes;
7. repeat across relevant scales.

## 4.2 `Aware_power` currently implemented

| Awareness layer | Evidence object | Status |
|---|---|---|
| Incoming-wave awareness | boundary-input-only probe | **Implemented** |
| Internal field awareness | floor-state-assimilated probe | **Implemented** |
| State-overlap awareness | state fidelity | **Implemented** |
| Floor target awareness | nodal fidelity | **Implemented** |
| Path awareness | weights, dominance, currents | **Implemented** |
| Manifestation awareness | evolved `a·v`, hit work | **Implemented as proxy** |
| Downstream response awareness | causal displacement envelope | **Implemented** |
| Manifestation–response gap | hidden-work proxy | **Implemented as proxy** |
| Data-semantic awareness | signal map and case interpretation | **Implemented** |
| Provenance awareness | source manifest and no silent preprocessing statement | **Implemented** |
| Ablation awareness | five probes | **Implemented** |

## 4.3 Hidden-work proxy

The code computes:

$$
h_i(t)
=
\widetilde W_{\mathrm{hit},i}(t)
-
\widetilde u_{\mathrm{env},i}(t)
$$

This quantity compares normalized accumulated manifestation with normalized downstream displacement. It is a diagnostic contrast. It is not proof of unmeasured physical energy.

## 4.4 FATE layers not yet implemented

| FATE layer | Missing element |
|---|---|
| `Alert_control` | alert threshold, confidence rule, hazard-state decision, intervention policy |
| Physical control | actuator command, damper command, boundary change, structural action |
| Hamiltonian rewrite | action-conditioned update of $H$ or topology |
| `Alive_evolve` | post-action state evolution and survival comparison |
| Counterfactual testing | controlled comparison of alternative interventions |
| Fractal recursion | nested component–member–story–building–site scales |
| Outcome validation | verified reduction of damage or improvement in survival |

---

# 5. Probe-to-theory separation

| Probe | QSM content | QTE content | FATE content |
|---|---|---|---|
| Laplacian floor-state field | full one-step state evolution | Laplacian path/current | full present `Aware_power` |
| Zero-diagonal floor-state field | same one-step state evolution | relational Hamiltonian comparison | operator awareness |
| Boundary-input-only | boundary source evolution | no internal measurement-driven path | incoming-wave reference |
| Dynamic path without response feedback | same one-step evolution | current/Power/residual path update | removes response-awareness feedback |
| Fixed-path reference | isolates one-step QSM alignment | adaptive path disabled | ablation awareness |

The fixed-path result is why one-step correlation is treated primarily as QSM evidence. Dynamic weights and edge current provide the separate QTE evidence. The weak effect of current response feedback is why FATE remains at `Aware_power`.

---

# 6. Current evidence boundary

## Supported by the present release

- the code contains an explicit complex wavefunction;
- the code contains an explicit Hamiltonian;
- the code computes the Schrödinger unitary `exp(-iHΔt)`;
- the code computes state and nodal fidelity;
- the code projects a work-compatible `a·v` scale through the evolved state;
- two direct-channel records reproduce strong one-step floor-state alignment;
- floor-state assimilation and boundary-only evolution are distinguishable;
- four cases produce a repeated lower-interface floor-domain indication;
- edge current independently supports the lower-interface tendency;
- signal provenance materially affects field coherence;
- the integrated chain reaches FATE `Aware_power`.

## Still open

- calibrated absolute Power and energy;
- a direct physical evaluation of the complete canonical Power-manifestation vector;
- autonomous multi-step evolution without measurement assimilation;
- member-level structural topology and background potential;
- verified weak-plane or damage localization;
- causal attribution among earthquake, control state, sensor system, and processing;
- FATE alert, control, Hamiltonian rewrite, and post-action evolution;
- cross-scale fractal implementation;
- universal validity across structural systems.

---

# 7. Concise implementation verdict

```text
QSM:
the complex state, Hamiltonian evolution, fidelity,
one-step manifestation, and assimilation are implemented.

QTE:
the floor topology, Laplacian/zero-diagonal operators,
edge currents, adaptive path weights, and path history are implemented.

FATE:
Aware_power is implemented as an integrated observation layer.

Still open:
absolute physical calibration, member-level topology,
Alert_control, Alive_evolve, and cross-scale fractal recursion.
```
