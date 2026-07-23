# Experimental Data — V12.2

The original NEES source files used by this release are not redistributed in this repository.

## Source dataset

Zhang, J., Wu, B., and Dyke, S.  
*RTHS and Shake Table Comparison for Smart Structural Systems*  
NEES-2011-1076  
DOI: [10.7277/TPS7-V877](https://doi.org/10.7277/TPS7-V877)

## Expected local input files

```text
elcentro_0p50_07312012_unc_donghua_converted.csv
elcentro_0p50_07312012_poff_donghua_converted.csv
kobe_035_semi_active_avg_converted.csv
morgan_1_p_off_avg_converted.csv
```

Place these files in the local `Data Source` directory beside the repository when running the V12.2 scripts.

## Signal provenance

- Kobe and Morgan Hill use direct analytical displacement, velocity, and acceleration channels on all three floors.
- The El Centro records use mixed displacement-coordinate semantics; velocity is derived from displacement while acceleration is directly measured.
- These provenance differences are retained in the case-level and cross-case interpretation rather than silently harmonized.

The source files remain excluded from Git because of file size and data-redistribution considerations.
