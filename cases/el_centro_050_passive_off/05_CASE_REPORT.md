# El Centro 0.50 — passive-off

## QSM–QTE–FATE Integrated Seismic Field Observation · NEES-2011-1076 V11

- Source file: `elcentro_0p50_07312012_poff_donghua_converted.csv`
- Earthquake input: **El Centro**
- Input scale: **0.50**
- Control state: **passive-off**
- Acquisition context: **Dong-Hua shake-table record**

## Method position

This case reports an evolutionary-field observation at the available floor-domain resolution. QSM is used for one-step structure-coupled power-state evolution; QTE is used for floor-domain path indication; FATE is represented at the Aware_power observation layer. The boundary-input-only mode is retained as a diagnostic reference.

The one-step check is:

```text
measurements through k
-> evolve field to k+1|k
-> compare evolved a*v with measured a*v at k+1
-> assimilate the new measurement
```

## Case-level path indication

- Floor-state final path indication: **1F-2F lower-interface indication**
- Supporting floor-state dynamic probes: **3 / 3**
- Main final path dominance index: **0.150**
- Main edge-current ratio 1F-2F / 2F-3F: **2.010**

## Boundary-input-only versus floor-state assimilation

| Floor | Boundary signed corr | Boundary abs corr | Assimilated signed corr | Assimilated abs corr |
|---|---:|---:|---:|---:|
| 1F | -0.054 | 0.857 | 0.680 | 0.799 |
| 2F | 0.016 | 0.667 | 0.053 | 0.501 |
| 3F | 0.150 | 0.687 | 0.040 | 0.468 |

## Work-compatible proxy summary

- Work-capacity scale: **9.715**
- Mean manifested work ratio: **0.555**
- Mean unmanifested work margin: **0.445**
- Largest downstream displacement response: **1F**

## Signal provenance

| Floor | Displacement u | Velocity v | Acceleration a |
|---|---|---|---|
| 1F | `direct:First Floor Relative Displacement Sensor` | `derived:d(displacement)/dt` | `direct:First Floor Acceleration Sensor` |
| 2F | `direct:Second Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Second Floor Acceleration Sensor` |
| 3F | `direct:Third Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Third Floor Acceleration Sensor` |

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.
