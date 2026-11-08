# Validation and test strategy

## Standard checks

Install the prototype in editable mode as described in [Contributing](CONTRIBUTING.md), then run the repository check from the root:

```sh
python scripts/check.py
```

To generate a fictional workbook for local manual checks (`demo` does not write one; it uses a temporary database):

```sh
python -m sentinel sample --output prototype/output/sample.xlsx
```

Generated files are local artifacts and must not be staged or published. Use temporary SQLite databases and temporary output paths in tests so test runs do not rely on or overwrite a developer's local data.

## Private workbook checks

Any integration check that reads an authorized private workbook must be explicitly opt-in through `SENTINEL_WORKBOOK`, set to an absolute local path. When unset, the private check should report an explicit skip; when set to an unreadable or invalid workbook, it should fail rather than silently fall back to a fixture. Never print workbook contents, include them in test output, or commit the input or resulting reports. Public CI uses synthetic fixtures and the reviewed anonymized workbook independently of this variable.

## Behaviors worth covering

- Workbook parsing, row preservation, timestamp normalization, SOP effective dates, and `known_at` visibility relative to the import's `tables['_observed_at']` timestamp.
- Candidate analysis and fail-closed blockers, including the fact that indexes do not establish an adjudication.
- Snapshot import replay and rejection of a different snapshot; expected-version conflicts and idempotent retries.
- Evidence/review/signature prerequisites, independent approvers, reopening before signed-case changes, and the local-only dual-signature text heuristic.
- Original-alert notification obligations, internal reminder processing, and the separation of reminder delivery from a manually attested receipt.
- Audit-chain export and verification without treating a valid hash chain as WORM retention or proof of factual correctness.

## Long-term reliability approach

Production qualification should add repeatable tests for tenant isolation, concurrency, source gaps and corrections, deadline behavior during outages/backlogs, restore and retention, audit export, false-safe closure, and independently verified delivery. Pin code, policy, source mappings, and any optional model version per release/case; gate promotion on reconciled shadow results and accountable QA/security/operations approval. These are proposed qualification gates, not tests already passed by the local prototype.

## Public-test constraints

The public test suite uses synthetic fixtures and the separately reviewed anonymized evaluation workbook, never the private original records. Tests should check domain outcomes and workflow boundaries without asserting that the prototype validates the meaning of source documents.

## Verification record — 2026-11-08

Results from the end-to-end pass taken immediately before submission. Private outputs stayed local; only aggregates are recorded.

| Check | Command | Result |
|---|---|---|
| Fresh install from the README | `python3 -m venv .venv && python -m pip install -r requirements.txt` | Installs `sentinel-adjudication` and `defusedxml==0.7.1` only |
| Compile, public tests, HTTP lifecycle demo | `python scripts/check.py` | Passed; private check explicitly skipped |
| Full suite against the supplied workbook | `SENTINEL_WORKBOOK=<pack> python -m unittest discover -s prototype/tests` | 30 tests, all passed |
| Supplied workbook import and report | `python -m sentinel --db … import <pack>` then `report --output …` | 420 cases created, all `WAITING_EVIDENCE` with blockers; exact-file replay created 0 |
| Public anonymized workbook | same commands on `data/anonymized-evaluation.xlsx` | 420 cases, same structural outcome |
| API | `serve`, `scripts/api_example.py`, unauthenticated request | 200 with bearer, 401 without |
| Reminder stub, export and verify | `tick --tenant …`, `tick --fail`, `export`, `verify` | Reminders delivered / retried; exported bundle `valid: true` |
| Lint and container | `ruff check …`, `docker compose run --build --rm prototype` | Passed |
| Hosted CI on `main` | GitHub Actions | CI (9 jobs) and Security workflows green on the current head |

Re-run this table before any later submission; it is the acceptance check for "does it still work", not a clinical or production qualification.
