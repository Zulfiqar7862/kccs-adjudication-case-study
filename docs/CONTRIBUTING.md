# Contributing

Contributions should preserve the evidence-first behavior: candidate indexes and software-generated checks are inputs for human review, not an automated adjudication. Keep changes focused, add synthetic tests for changed behavior, and do not include source workbooks, reports, or other private inputs in commits.

## Development setup

Use Python 3.11 or newer. From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The package has one pinned runtime dependency, `defusedxml==0.7.1`, for safe XML parsing. Installing in editable mode installs it and exposes the `sentinel` command. Generate the fictional workbook with `python -m sentinel sample`; generated artifacts are local and ignored by Git.

## Code map

- `src/sentinel/workbook.py`: XLSX parsing and input digest.
- `src/sentinel/evidence.py`: timestamp parsing, SOP candidate lookup, and blocker analysis.
- `src/sentinel/service.py`: SQLite transactions, case lifecycle, optimistic versioning, idempotency, audit, signatures, notifications, and export verification.
- `src/sentinel/http.py`: authenticated loopback API adapter.
- `src/sentinel/__main__.py`: CLI command dispatch.
- `src/sentinel/demo.py`: fictional local workflow demonstration.
- `tests/`: add synthetic unit and integration checks here; do not add private source material as fixtures.

Keep adapters thin and put workflow invariants in the service/domain implementation. Preserve tenant scoping, expected-version checks, idempotent retry behavior, independent review/signature rules, and explicit boundaries around notification receipts. Changes to these behaviors should include tests for both the expected path and relevant rejection path.

## Checks and change hygiene

Run the standard-library test suite with:

```sh
python -m unittest discover -s tests -v
```

Run tests against fictional data only. Private integration checks are opt-in through an explicit `SENTINEL_WORKBOOK` path; see [Testing](TESTING.md). Never put raw inputs, generated reports, credentials, local databases, or private test output in a public commit. Review `git status` and the staged diff before committing, and do not force-add ignored input files.
