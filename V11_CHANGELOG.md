# V11 Changelog

## Formal method-chain presentation

- Renamed the release to **QSM–QTE–FATE Integrated Seismic Field Observation**.
- Added QSM–QTE–FATE to every case and cross-case figure title.
- Added the integrated method chain to generated CSV tables.
- Renamed the four case CSV files to include `qsm_qte_fate`.

## Interpretation wording

- Replaced categorical figure annotations with observational wording.
- Reported QTE as a floor-domain path indication at the available experimental resolution.
- Reported FATE as `Aware_power` only.
- Retained displacement as downstream response evidence.
- Changed near-zero path dominance to `near-equal / no clear final path indication`.

## Timing provenance

- Added data-preparation timing to every case log.
- Added elapsed time for each probe worker.
- Added sum and maximum probe-worker elapsed time.
- Added case artifact-generation/finalization timing.
- Added a root release log with all three phase times and total wall-clock time.
- Added execution timing to each case JSON manifest.

## Numerical engine

- Retained the V10 multi-core process engine.
- Retained chunked C-engine CSV parsing.
- Retained memory-mapped case feature sharing.
- Retained the O(n) running work maximum.
- No case-specific parameter fitting was introduced.
