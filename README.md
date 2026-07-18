# QSM–QTE–FATE Integrated Seismic Field Observation

## NEES-2011-1076 Formal Release V11

V11 is the formal four-case release of the integrated QSM–QTE–FATE observation package.

The method chain reported by this release is:

```text
QSM one-step power-state evolution
→ QTE floor-domain topology-path indication
→ FATE Aware_power observation
```

The present scope is deliberately limited:

- **QSM:** one-step structure-coupled `a*v` field evolution.
- **QTE:** floor-domain path indication using the three-floor experimental mapping.
- **FATE:** `Aware_power` only.
- **Not included yet:** component-level BIM/IFC topology, `Alert_control`, or `Alive_evolve`.

## Formal V11 changes

V11 keeps the V10 numerical evolution settings and multi-core engine. It does not introduce case-specific parameter fitting.

The formal-release changes are:

1. Every generated figure title contains **QSM–QTE–FATE**.
2. Figure and report annotations use observational wording such as “indicator,” “comparison,” and “proxy.”
3. Every generated CSV begins with a `00_method_chain` or `method_chain` field containing `QSM-QTE-FATE`.
4. Per-case logs record:
   - data-preparation time;
   - elapsed time of each of the five probe workers;
   - sum and maximum probe-worker time;
   - artifact-generation/finalization time;
   - accounted case task time.
5. The output root contains `00_RELEASE_RUN_LOG.txt` with phase and total wall-clock time.
6. Near-zero final path dominance is reported as:
   `near-equal / no clear final path indication`
   rather than being assigned to an interface by sign alone.
7. Case CSV filenames now include `qsm_qte_fate`.

## Configured cases

```text
el_centro_050_uncontrolled
el_centro_050_passive_off
kobe_035_semi_active
morgan_hill_100_passive_off
```

Expected data files:

```text
elcentro_0p50_07312012_unc_donghua_converted.csv
elcentro_0p50_07312012_poff_donghua_converted.csv
kobe_035_semi_active_avg_converted.csv
morgan_1_p_off_avg_converted.csv
```

## Recommended Windows folder

```text
D:\OneDrive\文件\Quantum Topology Express\
QSM-QTE Seismic Field Evolution - NEES-2011-1076
```

Copy the V11 package files into that folder beside the four converted CSV files.

## Run the complete four-case release

Open PowerShell in the project folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_all_cases_v11_ascii_path.ps1
```

The launcher maps the project folder temporarily to `Q:\` so that Conda receives an ASCII-only path.

Default execution settings:

```text
stride = 5
parallel probe workers = 8
CSV preparation workers = 2
chunk rows = 200,000
```

Output folder:

```text
outputs_qsm_qte_fate_nees_2011_1076_v11
```

## Quick smoke test

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_smoke_test_morgan_v11_ascii_path.ps1
```

This runs only the Morgan Hill case using a coarser stride.

## Case outputs

Each completed case contains 20 files:

```text
01_qsm_qte_fate_mode_comparison.csv
02_qsm_qte_fate_manifestation_summary.csv
03_qsm_qte_fate_floor_target_summary.csv
04_qsm_qte_fate_core_history.csv
05_CASE_REPORT.md
06_release_report.txt
07_energy_path_manifestation_consensus.png
08_floor_assimilated_path_evolution.png
09_boundary_input_only_path_evolution.png
10_edge_current_concentration.png
11_1f_evolved_av_next_vs_measured_av.png
12_2f_evolved_av_next_vs_measured_av.png
13_3f_evolved_av_next_vs_measured_av.png
14_boundary_vs_assimilated_av_alignment.png
15_boundary_vs_assimilated_path_dominance.png
16_work_capacity_summary_by_floor.png
17_force_displacement_work_loop_proxy.png
18_response_manifestation_by_floor.png
19_release_run_log.txt
20_release_file_manifest.json
```

The release also generates 11 cross-case files and one root execution log.

## Timing interpretation

Per-case probe timings are worker-process elapsed times. Their sum is useful as a computational-load indicator, but it is not the same as wall-clock time because probes run in parallel.

The root log reports true phase and total wall-clock timing.

## Numerical regression

V11 was run on the Kobe and Morgan Hill records and compared with V10.

Maximum differences in the numeric mode-comparison fields were:

```text
Kobe:       4.18 × 10^-14
Morgan Hill: 1.53 × 10^-13
```

These differences are floating-point scale. The V11 changes are presentation, provenance, timing, and cautious path labeling; the QSM–QTE numerical evolution settings were not retuned.

## Data citation

Zhang, J., Wu, B., and Dyke, S.  
*RTHS and Shake Table Comparison for Smart Structural Systems (NEES-2011-1076)* [Data set].  
DOI: `10.7277/TPS7-V877`.
