# Local-only inputs

No source workbook, source PDF or source-derived report is included in this public repository.

For a generated fictional workbook, run `python -m sentinel sample`. It writes
`prototype/output/sample.xlsx`, which is ignored by Git. For authorized private data, keep the
workbook outside the repository (recommended), or place it here. All `.xlsx` and `.pdf`
files are ignored. Never force-add them.

Run the private integration checks with `SENTINEL_WORKBOOK` set to an absolute path.
When the variable is unset, private integration tests report an explicit skip. When set
to an invalid path or invalid workbook, they fail. Public CI uses only fictional fixtures.
