# Working log

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

## Initial prototype verification on 2026-11-08

- `python scripts/check.py`: 24 tests discovered; 23 passed and the unconfigured private-workbook check explicitly skipped. Compilation and the running-HTTP lifecycle demo passed.
- With `SENTINEL_WORKBOOK` pointing to the authorized supplied workbook: all 24 tests passed. The private check imports all supplied events, rejects implicit dispositions, requires blockers, checks tenant isolation and temporal visibility, verifies audit exports, and confirms exact-file replay creates no new cases. No source-derived outputs are published.
- `ruff check --config prototype/pyproject.toml prototype/src prototype/tests scripts` and `pip check` passed. Bandit found no medium/high-severity issues (two low-severity findings remain); `pip-audit` reported no known dependency vulnerabilities. The local project is not on PyPI and is reviewed as source, not covered by that dependency lookup.
- Early test failures exposed fixture mistakes: substring policy selection, an unescaped `+` in an ISO query parameter, UTC expectations, and assertions using the wrong response shape. Corrected tests preserve role enforcement and the API contract rather than weakening production checks.
- No live connector, clinical correctness, regulator delivery, production deployment, or seven-year retention proof is claimed. This is a JSON API/CLI, not a visual dashboard.

## Hosted verification feedback

The first hosted run passed Linux and Windows but exposed a macOS demo timeout. The first in-process HTTP server also took roughly 35 seconds to initialize; the standard HTTP server performs a reverse-DNS lookup during binding. The loopback-only adapter now binds the numeric loopback address without that unnecessary lookup, with a regression test that rejects any reverse-DNS call. The demo's timeout was not relaxed. Hosted macOS results are the acceptance check for this change.

A separate scanner download received HTTP 504. Bounded HTTP retries now handle transient upstream failures without skipping the credential scan or weakening its result.

The AI-use disclosure and explicit review corrections are kept separately in [AI review and corrections](11-ai-review-corrections.md).

## Scope and traceability note

This log records engineering decisions and checks for the public-safe prototype. References below use brief sections and workbook sheet/row locations, not customer or case identifiers. No private workbook or source attachment is included in this repository.

## Reference-inspired layout revision

Moved the runnable package, tests and package metadata under `prototype/`, with ingestion, evidence, workflow, API and fictional-fixture boundaries. Kept transactionally coupled state and audit operations together instead of introducing empty domain or service layers. Split the written submission into numbered documents and moved Mermaid diagrams into `diagrams/`; old document paths remain short navigation redirects.

An initial test run caught a stale workbook import after the module move. Configuration tests and the CLI suite also caught a local variable shadowing the JSON-output function; both were corrected before publication. The new output default is `prototype/output`, with explicit `SENTINEL_OUTPUT` support. Existing local files are not deleted or migrated automatically.

Final local checks for this layout: 27 tests discovered, 26 public tests passed and the unconfigured private-workbook check skipped; all 27 passed with the supplied authorized workbook. The HTTP demo, clean non-editable package install, root requirements install, Ruff, dependency consistency/audit and Bandit's medium/high gate passed. Docker Compose and the Windows launcher have dedicated hosted CI jobs; their current-head results are the verification evidence for those paths. No private test output is published.

## Final submission review — 2026-11-08

Reviewed merged commit `3cebb9adbe3b91c740ca8df9d402f3cc1d5e7e4a` against the brief and all four requested sections. Fresh non-editable and root-requirements installs passed the public checks (27 tests discovered; 26 passed, one explicitly skipped). With the supplied workbook configured, all 27 tests passed. Direct private-workbook import/report commands completed, and SQLite integrity checking returned `ok`; source-derived outputs stayed local. The HTTP lifecycle demo, Ruff, dependency consistency, dependency audit and Bandit's medium/high gate passed. The fresh environment initially contained an outdated installer with advisory findings; upgrading that environment's pip resolved those toolchain findings without changing the project's pinned runtime dependency.

The merged revision's hosted CI passed all nine jobs (Linux, macOS and Windows on Python 3.11/3.13, lint, Docker Compose and PowerShell); its separate security job passed. Container and Windows-launcher verification here relies on those hosted results, not a local rerun. This remains prototype verification, not clinical or production qualification.

The review corrected an unsupported denominator claim, clarified retrospective disagreement reporting, and removed stale pre-merge and Docker wording. It also explicitly recorded that the authored working log does not fulfill the brief's request for complete original AI sessions. No missing session history was fabricated or published.
