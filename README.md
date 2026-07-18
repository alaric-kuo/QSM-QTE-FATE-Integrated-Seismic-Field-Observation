# QSM-QTE-FATE Integrated Seismic Field Observation

## NEES-2011-1076 - Formal Release V11.1

**Author and theory developer:** Dr. Han-Jung (Alaric) Kuo  
**Organization:** A&J Management Consulting Limited  
**Numerical engine:** V11  
**Documentation revision:** V11.1

This repository records a four-case seismic field observation using the archived NEES-2011-1076 experimental records.

**Theoretical order:** RPG → QSM → QTE → FATE

**Implemented chain:** measured floor motion → work-compatible input scale `a·v` → empirical structural state for measurement-driven computation → QSM Hamiltonian Power-state evolution → target-state fidelity and target-hit work → QTE floor-domain path and edge-current manifestation → FATE `Aware_power`

The V11 numerical engine and the 92 formal output artifacts remain unchanged. V11.1 records the theoretical equations, the exact role of the Hamiltonian Power operator, and the boundary between the canonical theories and the current code. It also places the method across the building life cycle: design explores Power input and geometric topology, the as-built stage introduces verified material fields, and operation adds sensing, correction, feedback, and active control.

---

# 1. Theory hierarchy and implementation scope

| Layer | Theoretical role | V11 implementation |
|---|---|---|
| **RPG** | Provides the unit-Power and mass-boundary language through $a\cdot v$ | Uses measured floor acceleration and velocity to form the work-compatible input scale |
| **QSM** | Converts stiffness coupling into Hamiltonian Power channels and evolves the structural Power state | Uses effective three-floor channel matrices, complex state evolution, fidelity, and target-hit work |
| **QTE** | Compiles viewpoint, topology, channel, evolution, manifestation, and action | Implements a floor-domain topology, Laplacian and zero-diagonal probes, edge current, and dynamic path indication |
| **FATE** | Extends QTE into `Aware_power · Alert_control · Alive_evolve` | Reaches the `Aware_power` observation layer |

The current state space contains three floor nodes and two inter-floor paths:

```text
[1F] —— w12 —— [2F] —— w23 —— [3F]
```

This floor-domain graph is the observational resolution available from the archived records. Member-, joint-, and component-level topology requires a corresponding BIM/IFC or as-built structural graph.

---

# 2. Resonance Power Gradient input language

The FATE theoretical hierarchy begins with the RPG mass generation-dissolution equation:

$$ \frac{1}{m}\frac{dm}{dt}=\frac{a\cdot v}{c^2} $$

The local unit-Power criterion is:

$$ P_u(t)=a(t)\cdot v(t) $$

At engineering scale, $a\cdot v$ expresses Power per unit mass:

$$ \frac{P}{m}=a\cdot v $$

The NEES records do not provide the physical floor masses required to convert every floor channel into absolute watts. V11 therefore uses $a\cdot v$ as a mass-normalized, work-compatible Power input:

$$ \frac{dW}{m}\approx a\cdot du=a\cdot v\cdot dt $$

The code preserves both the signed quantity $a\cdot v$ and its absolute accumulated work-compatible quantity.

---

# 3. Quantum Structural Mechanics

## 3.1 From stiffness assets to Power channels

Classical structural mechanics writes:

$$ F=Kx $$

QSM rereads the stiffness matrix as both a resistance asset and a map of structural coupling. In the first QSM channel condition, the diagonal self-Power wells are removed so that the off-diagonal transmission channels become visible.

**QSM transformation:** stiffness matrix $K$ → remove diagonal self-Power wells → retain off-diagonal coupling → form Hamiltonian Power channels

A channel transmission coefficient $\gamma_{ij}$ describes the ability of Power to pass between nodes $i$ and $j$. Channel narrowing, damage, or obstruction changes $\gamma_{ij}$ and redirects the evolving structural state.

## 3.2 Hamiltonian Power operator

QSM begins from the standard Hamiltonian evolution equation:

$$ i\hbar\frac{d}{dt}\lvert\Psi(t)\rangle=\hat H\lvert\Psi(t)\rangle $$

QSM defines the **Hamiltonian Power operator** as:

$$ \hat H_p=-i\left(\frac{\hat H}{\hbar}\right) $$

The structural Power state therefore satisfies:

$$ \frac{d}{dt}\lvert\Psi(t)\rangle=\hat H_p\lvert\Psi(t)\rangle $$

Its formal time evolution is:

$$ \lvert\Psi(t)\rangle=e^{\hat H_p t}\lvert\Psi(0)\rangle $$

This operator definition is central to QSM:

- $\hat H$ is the Hamiltonian description of the structural channel law.
- $\hat H_p$ absorbs the phase factor $-i$ and the scale factor $\hbar^{-1}$.
- $e^{\hat H_p t}$ advances the structural Power state directly.

## 3.3 QSM Power manifestation

The QSM Power manifestation equation is:

$$ P(t)=(a\cdot v)\hat H_p\lvert\Psi(t)\rangle $$

For a spatial structural state:

$$ P(x,t)=(a\cdot v)\hat H_p\lvert\Psi(x,t)\rangle $$

The three factors have distinct roles:

| QSM object | Role |
|---|---|
| $a\cdot v$ | Real dynamic Power input scale per unit mass |
| $\hat H_p$ | Hamiltonian Power transformation through structural channels |
| $\lvert\Psi(t)\rangle$ | Evolving structural Power state |

For experimental applications, the effective input may be written as $P_{\mathrm{input}}(t)$:

$$ P(t)\sim P_{\mathrm{input}}(t)\hat H_p\lvert\Psi(t)\rangle $$

The measured $a(t)\cdot v(t)$ provides the direct first-order basis for $P_{\mathrm{input}}(t)$ in this release.

## 3.4 Fidelity as target-state hit ratio

QSM observes where the evolving state hits through fidelity:

$$ Fid(t)=\left\lvert\langle\Psi_{\mathrm{target}}\vert\Psi(t)\rangle\right\rvert^2 $$

For a target reduced to structural node $n$:

$$ Fid^{(n)}(t)=\lvert\Psi_n(t)\rvert^2 $$

Fidelity is the target-state hit ratio. The real target-hit Power is interpreted as:

$$ P_{\mathrm{real}}^{\mathrm{target}}(t)\sim P_{\mathrm{input}}(t)Fid^{\mathrm{target}}(t) $$

The accumulated target-hit effective work is:

$$ W_{\mathrm{hit}}^{\mathrm{target}}(T)=\int_0^T P_{\mathrm{input}}(t)Fid^{\mathrm{target}}(t)\,dt $$

These equations separate the input scale, the evolving state, and the target hit.

## 3.5 Exact correspondence between QSM theory and V11 code

The V11 code stores the effective channel matrix in the variable `H`. It then computes:

```python
evals, evecs = np.linalg.eigh(H)
U = (evecs * np.exp(-1j * evals * dt)) @ evecs.conj().T
```

This is the numerical form:

$$ U(\Delta t)=e^{-iH\Delta t} $$

Under normalized units $\hbar=1$, this corresponds to:

$$ e^{\hat H_p\Delta t}=e^{-iH\Delta t} $$

The code does **not** redefine $\hat H_p$ as the matrix `H`. The correspondence is:

| Representation level | Object |
|---|---|
| Theoretical Hamiltonian channel law | $\hat H$ |
| QSM Hamiltonian Power operator | $\hat H_p=-i(\hat H/\hbar)$ |
| Code-level effective channel matrix | `H` |
| Code-level evolution operator | `U = exp(-iHΔt)` |

The code uses two effective channel matrices:

```python
if operator_key == "laplacian":
    H = L
elif operator_key == "zero_diagonal":
    H = -W
```

The zero-diagonal form isolates off-diagonal transmission channels. The Laplacian form carries the pure-topology channel condition used in the QTE bridge.

## 3.6 Measurement-driven state construction in V11

The theoretical QSM state is $\lvert\Psi(t)\rangle$. The archived experiment provides displacement, velocity, and acceleration records rather than a directly measured complex wavefunction.

V11 therefore compiles the measured floor signals into a normalized complex state. The code uses:

```python
energy = v_norm**2 + (omega_norm * u_norm)**2 + 0.25 * a_norm**2
amp = np.sqrt(energy / np.sum(energy, axis=1, keepdims=True))
phase = np.arctan2(omega_norm * u_norm, v_norm)
psi = amp * np.exp(1j * phase)
```

This is the **V11 measurement encoding** used to enter the QSM state space. It is an implementation choice for this dataset. It does not replace the canonical QSM equations and does not create a new theoretical definition of $\lvert\Psi(t)\rangle$.

## 3.7 One-step evolution and measurement update

For each time step, V11 uses measurements through time $k$ → builds the current complex structural state → evolves that state with `U = exp(-iHΔt)` → reads the evolved target-state fidelity → reconstructs the next floor-wise `a·v` manifestation → compares it with measured `a·v` at $k+1$ → assimilates the $k+1$ state.

The code-level evolution is:

```python
psi_prior = normalize_complex(U @ (psi + source_gain * dt * source))
```

The state fidelity and nodal fidelity are computed as:

```python
state_fidelity = abs(np.vdot(psi_meas[k + 1], psi_prior)) ** 2
fid = np.abs(psi_prior) ** 2
```

The floor-wise work-compatible manifestation used for the one-step comparison is:

```python
evolved_av_next[k + 1] = p_total * fid * evolved_sign
```

This line is the V11 observational reconstruction of the next signed $a\cdot v$ field. It is a code-level operationalization of target-hit Power. The canonical QSM Power equation remains:

$$ P(t)=(a\cdot v)\hat H_p\lvert\Psi(t)\rangle $$

V11 currently validates the state-evolution and fidelity-weighted manifestation chain. Absolute calibration of the full operator-valued Power vector remains a later engineering step.

## 3.8 QSM implementation status

| QSM element | V11 status | Current implementation |
|---|---|---|
| Stiffness-to-channel ontology | **Implemented at floor-domain level** | Three-floor effective channel graph |
| Off-diagonal channel condition | **Implemented** | Zero-diagonal probe with `H = -W` |
| Hamiltonian Power operator evolution | **Implemented numerically** | `U = exp(-iHΔt)` corresponds to `exp(H_p Δt)` under normalized units |
| Structural complex state | **Implemented as measurement encoding** | Complex state compiled from measured `u`, `v`, and `a` |
| Target-state fidelity | **Implemented** | Full-state overlap and nodal modulus square |
| Target-hit Power | **Implemented as work-compatible reconstruction** | Measured `a·v` scale distributed through nodal fidelity and evolved phase |
| Target-hit work | **Implemented as proxy** | Time integration of the reconstructed floor manifestation |
| Absolute watts and joules | **Open calibration task** | Requires physical floor masses and complete channel calibration |
| Long-horizon autonomous evolution | **Open validation task** | Current record uses one-step evolution followed by measurement update |
| Member-level target states | **Open model-resolution task** | Current targets are three floor nodes |

---

# 4. Quantum Topology Express

## 4.1 QTE methodological mainline

The QTE methodological mainline is:

**Viewpoint → Topology → Channel → Evolution → Manifestation → Action**

Here, **Manifestation** is the readable emergence of density, Power difference, edge current, manifestation rate, cumulative manifestation quantity, and manifestation score from the evolving topology-field state.

The computational dataflow is:

**$R$ → $A$ → $W$ → $L_{\mathrm{geo}}$ → $V_{\mathrm{bg}}$ → $H$ → $\psi(0)$ → $\psi(t)$ → $\rho(t)$ → $\Delta V_{\mathrm{resp}}(t)$ → $J(t)$ → $\Gamma(t)$ → $m(t)$ → $M(t)$**

where:

| Symbol | QTE meaning |
|---|---|
| $R$ | Node set |
| $A$ | Adjacency matrix |
| $W$ | Geometric or channel weights |
| $L_{\mathrm{geo}}$ | Geometric Laplacian |
| $V_{\mathrm{bg}}$ | Background Power field |
| $H$ | Complete field-driven Hamiltonian |
| $\psi(t)$ | Evolving QTE state |
| $\rho(t)$ | Power density |
| $\Delta V_{\mathrm{resp}}(t)$ | Dynamic Power difference |
| $J(t)$ | Edge current |
| $\Gamma(t)$ | Manifestation rate |
| $m(t)$ | Cumulative manifestation quantity |
| $M(t)$ | Manifestation score |

## 4.2 Bridge from QSM to QTE

In the QTE pure-topology condition:

$$ \hat H_p=\kappa L_{\mathrm{geo}} $$

QTE restores the background Power wells and forms the complete field-driven Hamiltonian:

$$ H=\hat H_p+\alpha_v\mathrm{diag}(V_{\mathrm{bg}}) $$

Therefore:

$$ H=\kappa L_{\mathrm{geo}}+\alpha_v\mathrm{diag}(V_{\mathrm{bg}}) $$

**QSM →** removes self-Power wells and exposes Power channels.  
**QTE →** uses the channel term $\hat H_p$ and restores the background Power field $V_{\mathrm{bg}}$.

The full QTE state evolves as:

$$ i\hbar\frac{d}{dt}\lvert\Psi(t)\rangle=H\lvert\Psi(t)\rangle $$

with:

$$ \lvert\Psi(t)\rangle=e^{-iHt/\hbar}\lvert\Psi(0)\rangle $$

Here, $H$ is the complete QTE field-driven Hamiltonian. It contains both the channel term and the background Power wells.

## 4.3 QTE observables

Power density is:

$$ \rho_i(t)=\lvert\psi_i(t)\rvert^2 $$

The dynamic Power difference is:

$$ \Delta V_{\mathrm{resp}}(t)=-L_{\mathrm{geo}}\rho(t) $$

The edge current is:

$$ J_{ij}(t)=2\,\mathrm{Im}\left(\psi_i^*(t)H_{ij}\psi_j(t)\right) $$

The local velocity field is derived from edge flow:

$$ v_i(t)=\frac{\sum_j J_{ij}(t)u_{ij}}{\rho_i(t)+\epsilon} $$

The local acceleration is:

$$ a_i(t)\approx\frac{v_i(t+\Delta t)-v_i(t)}{\Delta t} $$

The local unit Power and manifestation rate are:

$$ P_{u,i}(t)=a_i(t)\cdot v_i(t) $$

$$ \Gamma_i(t)=\frac{a_i(t)\cdot v_i(t)}{c^2}=\frac{1}{m_i}\frac{dm_i}{dt} $$

The cumulative manifestation quantity is:

$$ m_i(t)=m_i(0)\exp\left(\int_0^t\Gamma_i(\tau)\,d\tau\right) $$

The manifestation score integrates the QTE observables and engineering criteria:

$$ M_i(t)=\lambda_1\lvert\Delta V_{\mathrm{resp},i}(t)\rvert+\lambda_2\max(\Gamma_i(t),0)+\lambda_3\max(\Delta V_{\mathrm{bg},i},0)+\lambda_4\log m_i(t) $$

## 4.4 Floor-domain QTE implemented in V11

V11 implements the beginning and middle of the QTE dataflow at floor-domain resolution:

**$R$ → $A$ → $W(t)$ → $L_{\mathrm{geo}}(t)$ → effective $H(t)$ → $\psi(t)$ → nodal density/fidelity → $J_{12}(t),J_{23}(t)$ → dynamic floor-path manifestation**

The node set is:

```text
R = {1F, 2F, 3F}
```

The weighted adjacency matrix is:

$$ W=\begin{bmatrix} 0 & w_{12} & 0 \\\\ w_{12} & 0 & w_{23} \\\\ 0 & w_{23} & 0 \end{bmatrix} $$

The degree matrix and Laplacian are:

$$ D_{ii}=\sum_j W_{ij} $$

$$ L_{\mathrm{geo}}=D-W $$

The two V11 observation probes are:

| Probe | Code matrix | Theoretical reading |
|---|---|---|
| Zero-diagonal | `H = -W` | QSM off-diagonal Power-channel observation |
| Laplacian | `H = Lgeo` | QTE pure-topology channel condition with normalized $\kappa=1$ |

The full background field $V_{\mathrm{bg}}$ is not yet constructed from material capacity, structural strength, damage state, BIM semantics, or sensor-returned component conditions. The Laplacian probe therefore represents the QTE **pure-topology condition**, rather than the complete field-driven Hamiltonian.

## 4.5 Edge-current and path observation

V11 computes:

$$ J_{12}(t)=2\,\mathrm{Im}\left(\psi_1^*(t)H_{12}\psi_2(t)\right) $$

$$ J_{23}(t)=2\,\mathrm{Im}\left(\psi_2^*(t)H_{23}\psi_3(t)\right) $$

The path weights begin at:

$$ w_{12}(0)=w_{23}(0)=1 $$

The code updates the two path weights from:

- edge-current magnitude;
- floor-to-floor $a\cdot v$ difference;
- measurement residual difference;
- optional displacement-response feedback;
- path-memory decay.

The weights are normalized to:

$$ w_{12}(t)+w_{23}(t)=2 $$

The floor-domain path-dominance indicator is:

$$ D_p(t)=\frac{w_{12}(t)-w_{23}(t)}{w_{12}(t)+w_{23}(t)} $$

Interpretation:

| Indicator | Floor-domain reading |
|---|---|
| $D_p>0$ | Greater `1F-2F` path manifestation |
| $D_p<0$ | Greater `2F-3F` path manifestation |
| $\lvert D_p\rvert\le 0.02$ | Near-equal final path weights |

This adaptive path rule is the V11 floor-domain observation mechanism. It is not yet the complete QTE chain through $\Gamma(t)$, $m(t)$, and $M(t)$.

## 4.6 QTE implementation status

| QTE element | V11 status |
|---|---|
| Viewpoint | Three-floor observation viewpoint |
| Node set $R$ | Implemented |
| Adjacency $A$ | Implemented |
| Dynamic weights $W(t)$ | Implemented |
| Geometric Laplacian $L_{\mathrm{geo}}(t)$ | Implemented |
| QSM channel probe | Implemented through zero-diagonal `H = -W` |
| QTE pure-topology probe | Implemented through Laplacian `H = Lgeo` |
| Complex state evolution | Implemented |
| Density/fidelity $\rho_i=\lvert\psi_i\rvert^2$ | Implemented |
| Edge current $J_{ij}$ | Implemented |
| Dynamic floor-path indication | Implemented |
| Background Power field $V_{\mathrm{bg}}$ | Open |
| Complete field-driven Hamiltonian $H=\hat H_p+\alpha_v\mathrm{diag}(V_{\mathrm{bg}})$ | Open |
| Canonical $\Delta V_{\mathrm{resp}}$ field | Open as a direct QTE output |
| Manifestation rate $\Gamma$ | Open |
| Cumulative manifestation quantity $m$ | Open |
| Manifestation score $M$ | Open |
| Governance trigger and action | Open |
| BIM/IFC member-level topology | Open |

---

# 5. Fractal Alive Topology Evolution

## 5.1 Core equation

FATE is:

$$ \mathrm{F.A.T.E.}=\mathrm{Aware}_{\mathrm{power}}\cdot\mathrm{Alert}_{\mathrm{control}}\cdot\mathrm{Alive}_{\mathrm{evolve}} $$

**Engineering sequence:** sense the paths of Power fluctuation → alert and control fatal topologies → survive through evolution and open dissipation

The three stages connect to QTE as follows:

| FATE stage | QTE relation | Engineering role |
|---|---|---|
| `Aware_power` | Viewpoint → Topology → Channel → Evolution → Manifestation | Read Power influx, channel flow, concentration, response, and provenance |
| `Alert_control` | Manifestation → Action | Identify fatal topology and issue an engineering intervention |
| `Alive_evolve` | Action → Re-evolution | Rewrite $V_{\mathrm{bg}}$, $W$, $L_{\mathrm{geo}}$, $\hat H_p$, or $H$, then observe the new state |

A FATE intervention may change damping, stiffness, coupling intensity, reaction force, or Power-transmission routes. The rewritten field then enters the next evolution cycle.

## 5.2 `Aware_power` in V11

V11 implements an `Aware_power` observation record through:

1. **Incoming-wave awareness**  
   The boundary-input-only probe reads what the boundary source can produce through the floor topology.

2. **Structure-coupled state awareness**  
   Floor-state assimilation inserts the measured internal structural state into the QSM evolution cycle.

3. **Target-state awareness**  
   Fidelity records where the evolved structural Power state hits.

4. **Topology-path awareness**  
   Dynamic $w_{12}$, $w_{23}$, $D_p$, $J_{12}$, and $J_{23}$ preserve the evolving floor-domain path.

5. **Work and response awareness**  
   Target-hit work is compared with a work-compatible displacement-side record.

6. **Provenance awareness**  
   Direct and derived signal channels, coordinate differences, numerical differentiation, acquisition, and processing remain visible in each case record.

7. **Ablation awareness**  
   Floor-state, boundary-only, fixed-path, zero-diagonal, Laplacian, and response-feedback conditions separate the roles of QSM, QTE, and the current response term.

## 5.3 FATE implementation status

| FATE element | V11 status |
|---|---|
| `Aware_power` | Implemented at floor-domain observation level |
| Incoming-wave observation | Implemented |
| Structure-coupled field observation | Implemented |
| Target-state hit observation | Implemented |
| Floor-path and edge-current observation | Implemented |
| Work/response observation | Implemented as normalized proxies |
| Provenance and data-semantic observation | Implemented |
| Fatal-topology criterion | Open |
| Manifestation score governance threshold | Open |
| `Alert_control` | Open |
| Physical control command | Open |
| Rewrite of $V_{\mathrm{bg}}$, $W$, $L_{\mathrm{geo}}$, $\hat H_p$, or $H$ | Open |
| `Alive_evolve` after intervention | Open |
| Cross-scale fractal recursion | Open |

---

# 6. Lifecycle deployment: design, as-built, and operation

QSM, QTE, and FATE use the same theoretical chain across the building life cycle, while the available evidence changes from design assumptions to verified physical properties and then to live feedback. The method therefore develops from **exploring possible Power channels**, to **constructing field-driven channels from actual building data**, and finally to **correcting and controlling the evolving field during operation**.

| Life-cycle stage | Available evidence | QSM-QTE-FATE role |
|---|---|---|
| **Design** | Geometry, topology, boundary conditions, design materials, candidate structural systems, and possible seismic inputs | Explore how the input Power field interacts with geometric and topological relationships. Compile $R$, $A$, $W$, and $L_{\mathrm{geo}}$; compare channel continuity, concentration, blockage, weak-plane placement, and dissipation alternatives before construction. |
| **As-built / commissioning** | Actual geometry, installed member sections, material properties, joints, connections, dampers, isolation devices, test results, and verified boundary conditions | Convert the design topology into a field-driven channel model. Actual material and capacity information forms the background Power field $V_{\mathrm{bg}}$, allowing the channel term and the physical Power wells to enter the complete Hamiltonian. |
| **Operation** | Sensor measurements, displacement, velocity, acceleration, strain, drift, device states, inspection records, maintenance history, and observed damage | Continuously update $\Psi(t)$, $V_{\mathrm{bg}}(t)$, $W(t)$, and $H(t)$. FATE reads the evolving field through `Aware_power`, evaluates intervention through `Alert_control`, and returns the modified system to `Alive_evolve`. |

## 6.1 Design-stage topology and Power-input exploration

During design, the main task is to examine how possible Power inputs encounter the proposed geometry and topology:

**candidate seismic input → geometric and semantic relationships → $R$ → $A$ → $W$ → $L_{\mathrm{geo}}$ → possible Power channels → concentration, blockage, reflection, and dissipation paths**

At this stage, QSM exposes the transmission relationships carried by structural coupling, while QTE manifests how different viewpoints, topologies, and channel arrangements change the possible evolution. The comparison can support decisions on structural layout, weak-plane governance, damping placement, isolation strategy, and acceptable local dissipation routes.

## 6.2 As-built field-driven channels

After construction, the model can incorporate the physical building that was actually delivered. Verified material properties, member dimensions, joint conditions, installed devices, and commissioning results provide the background Power field:

$$ H=\hat H_p+\alpha_v\mathrm{diag}(V_{\mathrm{bg}}) $$

or, under the QTE channel expression:

$$ H=\kappa L_{\mathrm{geo}}+\alpha_v\mathrm{diag}(V_{\mathrm{bg}}) $$

The as-built stage therefore joins **actual material capacity** with **actual topology**. It establishes the initial field-driven Hamiltonian against which later sensing and structural change can be interpreted.

## 6.3 Operational sensing, correction, and active control

During operation, sensing returns the structure's current state to the model:

**sensor return → state and field correction → $\Psi(t)$, $V_{\mathrm{bg}}(t)$, $W(t)$, $H(t)$ → renewed QSM-QTE evolution → FATE awareness, alert, intervention, and re-evolution**

An active or semi-active intervention may alter damping, stiffness, coupling strength, reaction force, or a Power-transmission path. The altered system is then observed again. This closes the FATE cycle:

$$ \mathrm{Aware}_{\mathrm{power}}\rightarrow\mathrm{Alert}_{\mathrm{control}}\rightarrow\mathrm{Alive}_{\mathrm{evolve}} $$

The present NEES release occupies the **operation-stage observation** position: it uses archived sensor records to reconstruct floor-level state evolution and topology-path manifestation. Design-stage BIM/geometry compilation, as-built material-field construction, and live closed-loop control define the next implementation layers.


# 7. End-to-end V11 computational flow

```text
1. Read the original NEES source files.

2. Select or derive floor displacement u(t), velocity v(t), and acceleration a(t).

3. Form the measured unit-Power record:
   Pu(t) = a(t)·v(t).

4. Compile u, v, and a into the V11 complex measurement state.

5. Build the current floor-domain channel matrix:
   zero-diagonal H = -W
   or
   Laplacian H = Lgeo.

6. Compute:
   U = exp(-iHΔt).

7. Evolve the current state one time step.

8. Compute:
   full-state fidelity
   and
   nodal fidelity |ψi|².

9. Reconstruct the next floor-wise signed a·v manifestation.

10. Compare the evolved manifestation at k+1|k
    with measured a·v at k+1.

11. Assimilate the new measured state.

12. Compute edge currents J12 and J23.

13. Update w12 and w23 for the dynamic-path probes.

14. Accumulate target-hit work and downstream response evidence.

15. Save the complete history, figures, summaries, provenance, and logs.
```

---

# 8. Five observation probes

Each case uses the same five observation settings:

| Probe | Channel matrix / condition | Function |
|---|---|---|
| Laplacian floor-state field | `H = Lgeo`, floor-state assimilation, dynamic path, response feedback | Main integrated QSM-QTE observation |
| Zero-diagonal floor-state field | `H = -W`, floor-state assimilation, dynamic path, response feedback | QSM off-diagonal channel observation |
| Boundary-input-only reference | Laplacian, boundary source, no upper-floor assimilation | Separates input-driven evolution from internal structure-coupled observation |
| Dynamic path without response feedback | Laplacian, floor-state assimilation, response term removed | Tests the influence of downstream response feedback |
| Fixed-path reference | Laplacian with `w12 = w23 = 1` | Separates QSM state alignment from QTE path adaptation |

The numerical coefficients are unchanged across all cases.

---

# 9. Dataset and formal cases

**Project:** NEES-2011-1076  
**Title:** *RTHS and Shake Table Comparison for Smart Structural Systems*  
**Dataset DOI:** [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)  
**NSF award:** CMMI-1011534 (NEESR)

The source files are read directly from the original dataset package:

```text
elcentro_0p50_07312012_unc_donghua_converted.csv
elcentro_0p50_07312012_poff_donghua_converted.csv
kobe_035_semi_active_avg_converted.csv
morgan_1_p_off_avg_converted.csv
```

The four formal cases are:

| Case | Event | Scale | Control condition | Velocity provenance |
|---|---|---:|---|---|
| El Centro uncontrolled | El Centro | 0.50 | Uncontrolled | Derived from displacement |
| El Centro passive-off | El Centro | 0.50 | Passive-off | Derived from displacement |
| Kobe semi-active | Kobe | 0.35 | Semi-active | Direct velocity channels |
| Morgan Hill passive-off | Morgan Hill | 1.00 | Passive-off | Direct velocity channels |

The El Centro cases provide a signal-semantic stress test because acceleration is direct while velocity is differentiated from displacement records that do not share exactly the same coordinate semantics.

---

# 10. Cross-case findings

## 10.1 QSM one-step state evolution

The direct-channel Kobe and Morgan Hill records show the strongest signed and absolute-envelope alignment between the evolved floor-wise $a\cdot v$ manifestation and the next measured record.

| Case | Mean signed correlation | Mean absolute-envelope correlation |
|---|---:|---:|
| Kobe 0.35 semi-active | 0.656 | 0.918 |
| Morgan Hill 1.00 passive-off | 0.649 | 0.916 |

The El Centro cases retain lower signed coherence while preserving substantial absolute-envelope correspondence. Their result follows the mixed coordinate and derived-velocity provenance recorded in the source channels.

## 10.2 Boundary input and internal structural state

The boundary-input-only reference remains close to equal final path weighting across the four records. Floor-state assimilation repeatedly produces an internal lower-interface indication.

This difference shows that the observed floor path depends on the structure-coupled state and cannot be recovered from the boundary input alone under the present observation settings.

## 10.3 Repeated floor-domain path indication

All four floor-state cases indicate the `1F-2F` floor interface. The histories differ in concentration, transition, recovery, and redistribution.

The common interface is a repeated floor-domain observation. Component-level physical interpretation requires the original structural configuration, control layout, sensor placement, and member-level topology.

## 10.4 Edge current

The floor-state dynamic probes show stronger RMS edge-current concentration at `1F-2F` than at `2F-3F`. The edge-current ratio provides a phase-sensitive observation separate from the final path weights.

## 10.5 Path manifestation and displacement response

The dominant floor path and the maximum displacement-response floor occupy different observation layers:

| Observation layer | Meaning |
|---|---|
| QTE path manifestation | Where the evolving Power state concentrates or passes |
| Downstream displacement response | Where motion becomes geometrically visible |

The repository preserves both histories.

## 10.6 Evidence separation

The fixed-path and dynamic-path probes retain similar one-step absolute-envelope correlations. This assigns the one-step $a\cdot v$ alignment primarily to QSM state evolution.

The dynamic path weights and edge-current concentration provide the QTE evidence.

The current FATE evidence is the continuously updated `Aware_power` record. The control and re-evolution stages remain the next implementation step.

---

# 11. Current evidence and development horizon

The four-case release provides a common computational record for QSM state evolution, QTE floor-domain path observation, and FATE `Aware_power`. Its strongest evidence is the repeated one-step alignment in the direct-channel Kobe and Morgan Hill records, the separation between boundary-only and structure-coupled observation, and the recurring `1F-2F` floor-interface indication across all four cases.

| Layer | Evidence established in this release | Development horizon |
|---|---|---|
| **QSM** | Hamiltonian state evolution, target-state fidelity, and work-compatible target-hit reconstruction | Physical calibration of $\hat H$, $\hat H_p$, floor mass, absolute Power units, long-horizon autonomous evolution, and member-level target states |
| **QTE** | Three-floor topology, dynamic channel weights, Laplacian and zero-diagonal probes, edge current, and path history | BIM/IFC or as-built topology, $V_{\mathrm{bg}}$, complete field-driven Hamiltonian, $\Delta V_{\mathrm{resp}}$, $\Gamma$, $m$, $M$, and verified weak-plane localization |
| **FATE** | Incoming-wave, structure-coupled field, target-state, path, response, provenance, and ablation awareness | Fatal-topology criteria, governance thresholds, `Alert_control`, physical intervention, and `Alive_evolve` |
| **Life cycle** | Retrospective operation-stage observation from archived sensing records | Design-stage topology exploration, as-built material-field construction, and live operational feedback control |

The release preserves its current observation resolution. The repeated floor-interface result is a floor-domain manifestation; the physical member, joint, device, or boundary responsible for that manifestation requires the original experimental configuration or a finer as-built graph.

---

# 12. Repository structure

The public root keeps only the files needed to understand, cite, reproduce, verify, and version the research:

```text
QSM-QTE-FATE-Integrated-Seismic-Field-Observation/
├── .gitignore
├── README.md
├── CITATION.cff
├── CHANGELOG.md
├── QA_REGRESSION.md
├── SHA256SUMS.txt
├── requirements.txt
├── code/
│   └── qsm_qte_fate_nees_multicase_release_v11.py
├── scripts/
├── data/
│   └── README.md
├── cases/
│   ├── el_centro_050_uncontrolled/
│   ├── el_centro_050_passive_off/
│   ├── kobe_035_semi_active/
│   └── morgan_hill_100_passive_off/
├── cross_case/
└── release_logs/
```

Each case folder contains four evidence tables and histories, two generated reports, twelve figures, one execution log, and one provenance manifest. Across four cases, the release contains 80 case artifacts, 11 cross-case artifacts, and one root execution log: **92 generated files in total**.

---

# 13. Reproduction

## 13.1 Requirements

- Python 3.10 or later
- NumPy
- pandas
- Matplotlib

```powershell
python -m pip install -r requirements.txt
```

## 13.2 Direct execution

```powershell
python .\code\qsm_qte_fate_nees_multicase_release_v11.py `
    --root "D:\path\to\Data Source" `
    --out ".\outputs_qsm_qte_fate_nees_2011_1076_v11" `
    --stride 5 `
    --workers 8 `
    --prepare-workers 2 `
    --chunk-rows 200000
```

The formal run used temporary ASCII drive mappings for Windows paths containing Chinese characters. The corresponding script is preserved in `scripts/`.

---

# 14. Formal execution record

The V11 formal run used:

```text
24 logical processors
2 CSV preparation workers
8 parallel probe workers
20 probe tasks
```

| Phase | Time |
|---|---:|
| Data reading and case-field preparation | 3.2 s |
| Parallel QSM-QTE-FATE probes | 19.9 s |
| Case and cross-case artifact generation | 13.6 s |
| Internal V11 wall-clock time | 36.8 s |
| End-to-end PowerShell time | 39.17 s |

Regression checks against V10 produced floating-point-scale differences:

```text
Kobe:        4.18 × 10^-14
Morgan Hill: 1.53 × 10^-13
```

---

# 15. Citation

## 15.1 Theoretical works

- Kuo, Han-Jung (Alaric). *Quantum Structural Mechanics: From Stiffness Assets to Value Flow.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.27121.13928](https://doi.org/10.13140/RG.2.2.27121.13928)

- Kuo, Han-Jung (Alaric). *Quantum Topology Express Method.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.22329.12645](https://doi.org/10.13140/RG.2.2.22329.12645)

- Kuo, Han-Jung (Alaric). *Fractal Alive Topology Evolution.* ResearchGate preprint.  
  DOI: [10.13140/RG.2.2.27969.72806](https://doi.org/10.13140/RG.2.2.27969.72806)

## 15.2 Experimental dataset

Zhang, J., Wu, B., and Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot.  
DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

## 15.3 Software

The repository citation is provided in [`CITATION.cff`](CITATION.cff).

---

# 16. Research position

Under one unchanged computational configuration, V11 applies QSM Hamiltonian Power-state evolution, target-state fidelity, QTE floor-domain path observation, and FATE `Aware_power` to four archived seismic records. The direct-channel Kobe and Morgan Hill records reproduce strong one-step QSM alignment. All four structure-coupled cases indicate the `1F-2F` interface while preserving distinct event histories, and the El Centro cases show how signal provenance and coordinate semantics affect $a\cdot v$ coherence.

The release establishes a reproducible experimental bridge from **QSM Power-state evolution**, through **QTE topology-path manifestation**, to **FATE Power awareness**. Across the building life cycle, the same chain can begin with design-stage exploration of input Power and geometric topology, develop into an as-built field-driven Hamiltonian using verified material data, and enter operation as a sensing-corrected feedback and active-control system.

---

# 17. Rights and attribution

Copyright © 2026 A&J Management Consulting Limited. All rights reserved.

This repository is published for scientific inspection, citation, and reproducibility evaluation. The original NEES experimental data remain with the dataset provider and are subject to the original source terms.

**Theory developer and corresponding author:** Dr. Han-Jung (Alaric) Kuo  
**Organization:** A&J Management Consulting Limited  
**Location:** Taiwan

