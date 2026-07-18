# Kobe 0.35 — semi-active

## QSM–QTE–FATE Integrated Seismic Field Observation · NEES-2011-1076 V11

- Source file: `kobe_035_semi_active_avg_converted.csv`
- Earthquake input: **Kobe**
- Input scale: **0.35**
- Control state: **semi-active**
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
- Main final path dominance index: **0.543**
- Main edge-current ratio 1F-2F / 2F-3F: **4.392**

## Boundary-input-only versus floor-state assimilation

| Floor | Boundary signed corr | Boundary abs corr | Assimilated signed corr | Assimilated abs corr |
|---|---:|---:|---:|---:|
| 1F | 0.087 | 0.757 | 0.567 | 0.851 |
| 2F | 0.012 | 0.725 | 0.709 | 0.949 |
| 3F | -0.147 | 0.548 | 0.693 | 0.955 |

## Work-compatible proxy summary

- Work-capacity scale: **1.654**
- Mean manifested work ratio: **0.611**
- Mean unmanifested work margin: **0.389**
- Largest downstream displacement response: **3F**

## Signal provenance

| Floor | Displacement u | Velocity v | Acceleration a |
|---|---|---|---|
| 1F | `direct:First Floor Displacement - Analytical` | `direct:First Floor Velocity Sensor - Analytical` | `direct:First Floor Acceleration - Analytical` |
| 2F | `direct:Second Floor Displacement - Analytical` | `direct:Second Floor Velocity Sensor - Analytical` | `direct:Second Floor Acceleration - Analytical` |
| 3F | `direct:Third Floor Displacement - Analytical` | `direct:Third Floor Velocity Sensor - Analytical` | `direct:Third Floor Acceleration - Analytical` |

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.
