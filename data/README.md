# Local private data

Place your authorised `KCCS_Sentinel_Reference_Data_Pack.xlsx` in this directory, retaining that exact filename. It is intentionally **not** included in the public repository and is ignored by git. The source brief PDF and private report must not be added here or anywhere in public history.

Without the workbook, `make test` runs synthetic tests and skips workbook integration modules. After copying it, run `make test` and `make run`. All fifteen sheets are read locally, and the workbook is never rewritten. Detailed generated dossiers stay in ignored `prototype/output/`; local test/coverage logs stay in `.local-evidence/`.

MIT licensing covers the authored code/documentation, not rights to the supplied private data. Do not upload your data in issues, pull requests, screenshots or CI artifacts.
