# Synthetic fixtures

These CSVs were manually invented for the public test suite. All entity labels use SYN/Example, timestamps are fictional, identifiers and temperatures are artificial, and no source workbook row was copied. They reproduce only column shapes and deliberately chosen boundary conditions.

Four events cover tenant-scoped SKU equality, missing identity, a synthetic firmware/BMS hazard, a late fixed-hour notification, a pending duty and exact-window equality. Three product records include a shared SKU across two synthetic tenants. Other source tables are absent by design; unit tests add hand-made alias/study/SOP assertions in memory.

`expected_outputs/sample_adjudication_report.json` is a manually stated aggregate subset checked against the deterministic report. It is evidence eligibility, not a clinical golden set. No source workbook is needed.
