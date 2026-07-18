# El Centro 0.50 — uncontrolled

## QSM–QTE–FATE Integrated Seismic Field Observation · NEES-2011-1076 V11

- Source file: `elcentro_0p50_07312012_unc_donghua_converted.csv`
- Earthquake input: **El Centro**
- Input scale: **0.50**
- Control state: **uncontrolled**
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
- Main final path dominance index: **0.140**
- Main edge-current ratio 1F-2F / 2F-3F: **3.763**

## Boundary-input-only versus floor-state assimilation

| Floor | Boundary signed corr | Boundary abs corr | Assimilated signed corr | Assimilated abs corr |
|---|---:|---:|---:|---:|
| 1F | -0.058 | 0.792 | 0.778 | 0.900 |
| 2F | 0.003 | 0.770 | 0.093 | 0.477 |
| 3F | -0.060 | 0.733 | 0.097 | 0.469 |

## Work-compatible proxy summary

- Work-capacity scale: **12.231**
- Mean manifested work ratio: **0.507**
- Mean unmanifested work margin: **0.493**
- Largest downstream displacement response: **3F**

## Signal provenance

| Floor | Displacement u | Velocity v | Acceleration a |
|---|---|---|---|
| 1F | `direct:First Floor Relative Displacement Sensor` | `derived:d(displacement)/dt` | `direct:First Floor Acceleration Sensor` |
| 2F | `direct:Second Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Second Floor Acceleration Sensor` |
| 3F | `direct:Third Floor Absolute Displacement Sensor` | `derived:d(displacement)/dt` | `direct:Third Floor Acceleration Sensor` |

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.
