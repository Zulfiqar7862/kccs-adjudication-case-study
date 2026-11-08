# Validation and test strategy

## Standard checks

Install the prototype in editable mode as described in [Contributing](CONTRIBUTING.md), then run the repository check from the root:

```sh
python scripts/check.py
```

To generate a fictional workbook for local manual checks:

```sh
python -m sentinel demo
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
