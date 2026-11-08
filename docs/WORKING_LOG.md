# Working log

This log records engineering decisions and checks for the public-safe prototype. References below use brief sections and workbook sheet/row locations, not customer or case identifiers. No private workbook or source attachment is included in this repository.

## Scope and approach

- Addressed all four brief deliverables: A (recommendation and rationale), B (design requirements and boundaries), C (what currently runs), and D (this evidence-based work log).
- Chose evidence completeness for accountable human review over automated disposition. The proposed first pilot is named only as the EU pilot tenant, with its anonymized constraints referenced at `12_Tenant_Constraints`, row 2.
- Mapped the requirements to the brief and to relevant workbook sheets for reviewer questions/queue, excursion events, SOP and stability indexes, tenant constraints, system inventory, and aggregate volume/cost assumptions. No customer names, product names, case IDs, incident narratives, or source-document/study IDs are reproduced.
- Treated workbook metrics as supplied aggregates or modeling inputs, not verified population estimates, outcomes, or guarantees. No human work hours were estimated; time spent was not tracked.

## Design decisions and exclusions

- Keep the prototype local, evidence-first, and human-controlled. Analysis produces candidates and blockers, not a disposition.
- Preserve source row provenance, import snapshot/hash and observation time, case revision, expected version, idempotency, and hash-chained audit events. Rejecting a second distinct workbook snapshot is a deliberate bounded-prototype alternative to a multi-snapshot bitemporal ledger: it prevents silent replacement, but does not provide historical queries across successive source snapshots; a new database is required for another snapshot.
- Keep alert-derived notification obligations distinct from case decisions. A reminder/outbox attempt is not regulator delivery; a receipt is entered as a separate human attestation and is not independently verified.
- Leave external identity, TLS, filing/delivery integration, verified receipt ingestion, WORM retention, multi-source reconciliation, and decision automation outside the implemented local prototype.
- Do not treat the regular-expression match for `dual` in signatory policy text as a general policy engine; it is a local heuristic and production authorization needs a typed, approved policy.
- Replace unsafe XML parsing with the pinned `defusedxml==0.7.1` dependency after the scan identified the parser risk. ZIP container access remains standard-library `zipfile`; XML goes through `defusedxml`.

## Implementation observations

- An import SQL statement/schema column mismatch was identified and corrected; synthetic import and replay checks exercise the path.
- An earlier substring check for `dual` also matched `individual`, incorrectly classifying that policy as dual approval. The implementation now uses a case-insensitive whole-word match (`\bdual\b`), avoiding that false match. It remains a text heuristic, not a validated production policy engine.
- The HTTP adapter enforces a bounded request body and has a test for rejecting an oversized payload with HTTP 413. This is a local request-size control, not a general API security assessment.
- Synthetic tests use isolated temporary data and databases; generated workbook checks are deterministic. A second distinct workbook snapshot is explicitly rejected.
- Public tests are intended to use synthetic data. Private workbook integration is explicitly gated by `SENTINEL_WORKBOOK`. Private inputs and generated outputs stay local and are excluded from public CI.

## Verified locally on 2026-11-08

- `python scripts/check.py`: 23 tests discovered; 22 passed and the unconfigured private-workbook check explicitly skipped. Compilation and the running-HTTP lifecycle demo passed.
- With `SENTINEL_WORKBOOK` pointing to the authorized supplied workbook: all 23 tests passed. The private check imports all supplied events, rejects implicit dispositions, requires blockers, checks tenant isolation and temporal visibility, verifies audit exports, and confirms exact-file replay creates no new cases. No source-derived outputs are published.
- `ruff check src tests scripts` and `pip check` passed. Bandit found no medium/high-severity issues (two low-severity findings remain); `pip-audit` reported no known dependency vulnerabilities. The local project is not on PyPI and is reviewed as source, not covered by that dependency lookup.
- Early test failures exposed fixture mistakes: substring policy selection, an unescaped `+` in an ISO query parameter, UTC expectations, and assertions using the wrong response shape. Corrected tests preserve role enforcement and the API contract rather than weakening production checks.
- No live connector, clinical correctness, regulator delivery, production deployment, or seven-year retention proof is claimed. This is a JSON API/CLI, not a visual dashboard.

## AI assistance and review limits

AI assistance was used to inspect repository code and draft these documents. No external model API was used by the prototype during execution. The authorized case-study materials were consulted locally to create anonymized references; source files and identifying values were not copied into these public docs. No human review hours are claimed. The checks above validate workflow mechanics, not clinical decisions; production qualification and accountable human review remain required.
