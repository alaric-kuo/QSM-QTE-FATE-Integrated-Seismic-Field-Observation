# V12.2 Quality-Assurance and Regression Record

## 1. Syntax and package inspection

- `code/qsm_qte_fate_nees_multicase_release_v12_2.py` compiled successfully with Python `py_compile`.
- The public method order was inspected as:

  ```text
  QSM → QTE → FATE
  ```

- QSM uses `H = -W`, fixed path, boundary input, and no response feedback.
- QTE uses `H = L(W)`, dynamic path, boundary input, and no continuous floor-state assimilation.
- FATE uses the Laplacian dynamic path with continuous floor-state assimilation and response feedback.

## 2. Formal real-data execution

The formal V12.2 run completed all four NEES records:

```text
El Centro 0.50 — uncontrolled
El Centro 0.50 — passive-off
Kobe 0.35 — semi-active
Morgan Hill 1.00 — passive-off
```

Execution record:

```text
24 logical processors detected
2 CSV preparation workers
8 parallel method workers
12 method tasks completed
Phase 1 data preparation: 3.170 s
Phase 2 QSM/QTE/FATE execution: 20.507 s
Phase 3 artifact generation: 19.123 s
Total internal elapsed: 42.881 s
```

Generated formal artifacts:

```text
4 cases × 20 generated files = 80
10 cross-case generated files = 10
1 root release log = 1
Total = 91
```

Each case additionally has one maintained narrative README.

## 3. Output completeness

For every case, V12.2 generated:

- two canonical summary CSVs;
- one 149-column full-history CSV;
- one machine-generated case report;
- one release report;
- 13 figures numbered `06–18`;
- one run log;
- one JSON file manifest.

The full-history CSV is exported with at most 3,000 rows for inspection. It is not a redistribution of the original NEES source data.

## 4. V12.1 → V12.2 numerical regression

All four V12.1 and V12.2 `03_qsm_qte_fate_full_history.csv` files were compared column by column.

```text
Common columns compared per case: 149
Rows compared per case: 3,000
Maximum numerical difference across all four cases: 0
```

V12.2 therefore changes cross-case figure separation, README organization, and reporting—not the V12.1 numerical histories.

## 5. V11 principal result → V12.2 FATE continuity

The former V11 principal sensor-assimilated Laplacian history was mapped to the V12.2 FATE fields. The comparison included:

- evolved and measured `a·v` on all three floors;
- one-step residuals;
- target-hit and signed target-hit histories;
- measured displacement and signed work;
- normalized response envelopes and hidden-work proxies;
- `w12`, `w23`;
- state fidelity and residual norm.

```text
Maximum numerical difference across all mapped fields and four cases: 0
```

V11 display-only work-component histories used independent normalization for some curves. V12.2 preserves common-scale work decomposition and therefore does not treat those independently normalized display columns as direct regression fields.

## 6. Scope statement

This QA confirms:

- software execution;
- artifact completeness;
- V12.1/V12.2 numerical continuity;
- continuity between the retained V11 principal sensor-aware result and V12.2 FATE.

It does **not** by itself establish:

- universal structural validity;
- physical watts or joules;
- member-level damage localization;
- a complete as-built field-driven Hamiltonian;
- automated control validity.
