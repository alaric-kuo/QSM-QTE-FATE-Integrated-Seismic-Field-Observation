# Morgan Hill 1.00 — passive-off

## QSM–QTE–FATE Integrated Seismic Field Observation · NEES-2011-1076 V11

- Source file: `morgan_1_p_off_avg_converted.csv`
- Earthquake input: **Morgan Hill**
- Input scale: **1.00 (encoded as morgan_1)**
- Control state: **passive-off**
- Acquisition context: **averaged converted record**

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
- Main final path dominance index: **0.079**
- Main edge-current ratio 1F-2F / 2F-3F: **1.368**

## Boundary-input-only versus floor-state assimilation

| Floor | Boundary signed corr | Boundary abs corr | Assimilated signed corr | Assimilated abs corr |
|---|---:|---:|---:|---:|
| 1F | 0.154 | 0.782 | 0.733 | 0.907 |
| 2F | 0.040 | 0.788 | 0.785 | 0.974 |
| 3F | -0.054 | 0.527 | 0.740 | 0.974 |

## Work-compatible proxy summary

- Work-capacity scale: **1.833**
- Mean manifested work ratio: **0.552**
- Mean unmanifested work margin: **0.448**
- Largest downstream displacement response: **2F**

## Signal provenance

| Floor | Displacement u | Velocity v | Acceleration a |
|---|---|---|---|
| 1F | `direct:First Floor Displacement - Analytical` | `direct:First Floor Velocity Sensor - Analytical` | `direct:First Floor Acceleration - Analytical` |
| 2F | `direct:Second Floor Displacement - Analytical` | `direct:Second Floor Velocity Sensor - Analytical` | `direct:Second Floor Acceleration - Analytical` |
| 3F | `direct:Third Floor Displacement - Analytical` | `direct:Third Floor Velocity Sensor - Analytical` | `direct:Third Floor Acceleration - Analytical` |

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.
