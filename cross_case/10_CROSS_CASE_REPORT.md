# QSM–QTE–FATE Integrated Seismic Field Observation

## NEES-2011-1076 four-case comparison · Release V11

This package compares four records from the same three-story steel-frame project. It is reported as a partial cross-wave and cross-control observation matrix rather than as a balanced factorial experiment.

## Cases

| Case | Event | Scale | Control mode | Source file |
|---|---|---:|---|---|
| El Centro 0.50 — uncontrolled | El Centro | 0.50 | uncontrolled | `elcentro_0p50_07312012_unc_donghua_converted.csv` |
| El Centro 0.50 — passive-off | El Centro | 0.50 | passive-off | `elcentro_0p50_07312012_poff_donghua_converted.csv` |
| Kobe 0.35 — semi-active | Kobe | 0.35 | semi-active | `kobe_035_semi_active_avg_converted.csv` |
| Morgan Hill 1.00 — passive-off | Morgan Hill | 1.00 (encoded as morgan_1) | passive-off | `morgan_1_p_off_avg_converted.csv` |

## Main comparison

| Case | Boundary abs corr | Assimilated abs corr | Gain | Boundary dominance | Assimilated dominance | Manifested path |
|---|---:|---:|---:|---:|---:|---|
| El Centro 0.50 — uncontrolled | 0.765 | 0.615 | -0.150 | -0.000 | 0.140 | 1F-2F lower-interface indication |
| El Centro 0.50 — passive-off | 0.737 | 0.589 | -0.148 | -0.003 | 0.150 | 1F-2F lower-interface indication |
| Kobe 0.35 — semi-active | 0.677 | 0.918 | 0.242 | -0.007 | 0.543 | 1F-2F lower-interface indication |
| Morgan Hill 1.00 — passive-off | 0.699 | 0.952 | 0.253 | -0.004 | 0.079 | 1F-2F lower-interface indication |

## Interpretation boundary

The four cases can test whether the distinction between incoming boundary information and the structure-coupled power-state field repeats across different records and control states. Only the El Centro uncontrolled / passive-off pair holds the earthquake input and scale approximately fixed; the full four-case set should therefore be interpreted as a robustness comparison rather than a complete causal control experiment.

## Data citation

Zhang, J., Wu, B., & Dyke, S. *RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set]. NEES / DesignSafe Data Depot. DOI: 10.7277/TPS7-V877.
