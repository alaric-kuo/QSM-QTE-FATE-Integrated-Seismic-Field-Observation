# V11 Quality-Assurance Record

## Syntax

`qsm_qte_fate_nees_multicase_release_v11.py` was compiled with Python `py_compile`.

## Real-data execution

V11 was executed using the uploaded public-record conversions for:

```text
Kobe 0.35 — semi-active
Morgan Hill 1.00 — passive-off
```

The two-case test completed all three phases and produced 20 files for each case, 11 cross-case files, and a root execution log.

## V10 numerical comparison

After excluding the new `00_method_chain` column and the revised textual path label, the maximum numeric differences in the case mode-comparison tables were:

```text
Kobe:        4.1744385725905886e-14
Morgan Hill: 1.5276668818842154e-13
```

The values are consistent with floating-point execution differences.

## Scope statement

This QA confirms software execution and V10/V11 numerical continuity for the tested records. It does not by itself establish universal structural validity.
