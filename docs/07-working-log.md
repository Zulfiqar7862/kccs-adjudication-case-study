# Working log

## Scope and approach

- Addressed all four brief deliverables: A (recommendation and rationale), B (design requirements and boundaries), C (what currently runs), and D (this evidence-based work log).
- Chose evidence completeness for accountable human review over automated disposition. The proposed first pilot is named only as the EU pilot tenant, with its anonymized constraints referenced at `12_Tenant_Constraints`, row 2.
- Mapped the requirements to the brief and to relevant workbook sheets for reviewer questions/queue, excursion events, SOP and stability indexes, tenant constraints, system inventory, and aggregate volume/cost assumptions. No customer, person or product names, case IDs, or source-document/study IDs are reproduced; the brief's incidents are cited by month and figure only.
- Treated workbook metrics as supplied aggregates or modeling inputs, not verified population estimates, outcomes, or guarantees. No human work hours were estimated; time spent was not tracked.

## Design decisions and exclusions

- Keep the prototype local, evidence-first, and human-controlled. Analysis produces candidates and blockers, not a disposition.
- Preserve source row provenance, import snapshot/hash and observation time, case revision, expected version, idempotency, and hash-chained audit events. Rejecting a second distinct workbook snapshot is a deliberate bounded-prototype alternative to a multi-snapshot bitemporal ledger: it prevents silent replacement, but does not provide historical queries across successive source snapshots; a new database is required for another snapshot.
- Keep alert-derived notification obligations distinct from case decisions. A reminder/outbox attempt is not regulator delivery; a receipt is entered as a separate human attestation and is not independently verified.
- Leave external identity, TLS, filing/delivery integration, verified receipt ingestion, WORM retention, multi-source reconciliation, and decision automation outside the implemented local prototype.
- Do not treat the regular-expression match for `dual` in signatory policy text as a general policy engine; it is a local heuristic and production authorization needs a typed, approved policy.
- Replace unsafe XML parsing with the pinned `defusedxml==0.7.1` dependency after the scan identified the parser risk. ZIP container access remains standard-library `zipfile`; XML goes through `defusedxml`.

## Alternatives considered and discarded

The finished design hides most of the discarding. The table records the alternatives that were seriously considered, why they were dropped, and what replaced them.

| Alternative | Why it was discarded | What replaced it |
|---|---|---|
| Build the most visual part first: a reviewer dashboard over the workbook | The brief asks for the part that is hardest to be right about. A dashboard would not establish that incomplete evidence cannot silently become a signed disposition while the clock keeps running. | The transactional evidence/lifecycle/clock kernel with a JSON API; no UI. |
| Treat index matches (SOP, stability) as evidence | The workbook indexes are metadata. Treating a matching row as proof of applicability is the same failure as the January pilot citing studies that do not exist. | Candidates plus fail-closed blockers; every imported case starts in `WAITING_EVIDENCE`. |
| Multi-snapshot bitemporal ledger in the prototype | Correct for production, but it needs reconciliation rules, document-control agreement on end-date semantics, and far more time than the brief allows. Shipping a half-built version would look like the full thing. | One immutable snapshot per database; a different snapshot is rejected rather than merged; the full model is documented, not implemented. |
| Event sourcing for case state | Would make replay elegant but duplicates what the hash-chained audit table already provides for this scope, and makes the "current state" queries reviewers actually run harder. | Current-state rows with optimistic versions plus an append-only hash-chained audit log and immutable revisions. |
| PostgreSQL for the prototype | Adds a service dependency a reviewer must run; nothing in the demonstrated invariants depends on it. | SQLite with explicit transactions; PostgreSQL named for the regional production ledger. |
| Deriving the reporting window from the workbook alone | The pack does not carry per-jurisdiction windows or calendars; inferring a universal 72 hours would be wrong for Brazil and the US programme. | Policy-driven obligations; unknown policy raises urgent manual work rather than "not required". |
| Parsing signatory policy text into a rule engine | A regex for `dual` first matched `individual`; a policy engine built on free text would repeat the 2,400-rule explainability problem. | Whole-word heuristic for the prototype, labelled as such; typed, approved `policy_bundle` for production. |
| Standard-library XML parsing for XLSX | Security scan flagged the parser; a reviewer-supplied workbook is untrusted input. | `defusedxml` for XML; `zipfile` only for the container. |
| Including an LLM narrative step behind a feature flag | Cost ceiling leaves USD 61/month of headroom on the modeled spend and the November prompt-change incident shows the blast radius; nothing in the critical invariant needs it. | Optional, versioned augmentation in the production design; absent from the prototype. |

## Assumptions that turned out wrong

- **"The workbook will give the prototype something to adjudicate."** It does not. Every one of the 420 events imports with blockers: the product master is a point-in-time snapshot without validity dates, no full SOP, stability, firmware or calibration documents are supplied, and no batch exposure record exists. This was first read as an ingestion bug; it is the brief's point. The analyzer now reports the blocker counts rather than being tuned to let cases through.
- **"64% and 82% use different denominators."** An early draft treated the rules engine's 78% closure of non-actionable alerts and the 82% non-actionable share as incompatible. They multiply: 0.78 × 0.82 ≈ 0.64 of all alerts, which is the board paper's "about 64 per cent". The correction is recorded in [AI review and corrections](11-ai-review-corrections.md).
- **"The demo timeout on macOS is flakiness."** It was a reverse-DNS lookup during server bind costing about 35 seconds; binding the numeric loopback address fixed it, with a regression test.
- **"Commands that write a file need no stdout."** During the end-to-end review a reviewer-style run of `report --output` and `export` produced no output at all, which reads as failure. They now confirm the written path without echoing private contents.

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

The first hosted run passed Linux and Windows but exposed a macOS demo timeout. The first in-process HTTP server also took roughly 35 seconds to initialize; the standard HTTP server performs a reverse-DNS lookup during binding. The loopback-only adapter now binds the numeric loopback address without that unnecessary lookup, with a regression test that rejects any reverse-DNS call. The demo's timeout was not relaxed. Hosted macOS runs have passed since this change.

A separate scanner download received HTTP 504. Bounded HTTP retries now handle transient upstream failures without skipping the credential scan or weakening its result.

The AI-use disclosure and explicit review corrections are kept separately in [AI review and corrections](11-ai-review-corrections.md).

## Scope and traceability note

This log records engineering decisions and checks for the public-safe prototype. References below use brief sections and workbook sheet/row locations, not customer or case identifiers. No private workbook or source attachment is included in this repository.

## Reference-inspired layout revision

Moved the runnable package, tests and package metadata under `prototype/`, with ingestion, evidence, workflow, API and fictional-fixture boundaries. Kept transactionally coupled state and audit operations together instead of introducing empty domain or service layers. Split the written submission into numbered documents and moved Mermaid diagrams into `diagrams/`; the short redirect stubs left at the old document paths were removed in the final end-to-end review because nothing linked to them.

An initial test run caught a stale workbook import after the module move. Configuration tests and the CLI suite also caught a local variable shadowing the JSON-output function; both were corrected before publication. The new output default is `prototype/output`, with explicit `SENTINEL_OUTPUT` support. Existing local files are not deleted or migrated automatically.

Final local checks for this layout: 27 tests discovered, 26 public tests passed and the unconfigured private-workbook check skipped; all 27 passed with the supplied authorized workbook. The HTTP demo, clean non-editable package install, root requirements install, Ruff, dependency consistency/audit and Bandit's medium/high gate passed. Docker Compose and the Windows launcher have dedicated hosted CI jobs; their current-head results are the verification evidence for those paths. No private test output is published.

## Final submission review — 2026-11-08

Reviewed merged commit `3cebb9adbe3b91c740ca8df9d402f3cc1d5e7e4a` against the brief and all four requested sections. Fresh non-editable and root-requirements installs passed the public checks (27 tests discovered; 26 passed, one explicitly skipped). With the supplied workbook configured, all 27 tests passed. Direct private-workbook import/report commands completed, and SQLite integrity checking returned `ok`; source-derived outputs stayed local. The HTTP lifecycle demo, Ruff, dependency consistency, dependency audit and Bandit's medium/high gate passed. The fresh environment initially contained an outdated installer with advisory findings; upgrading that environment's pip resolved those toolchain findings without changing the project's pinned runtime dependency.

The merged revision's hosted CI passed all nine jobs (Linux, macOS and Windows on Python 3.11/3.13, lint, Docker Compose and PowerShell); its separate security job passed. Container and Windows-launcher verification here relies on those hosted results, not a local rerun. This remains prototype verification, not clinical or production qualification.

The review corrected an unsupported denominator claim, clarified retrospective disagreement reporting, and removed stale pre-merge and Docker wording. It also explicitly recorded that the authored working log does not fulfill the brief's request for complete original AI sessions. No missing session history was fabricated or published.

## Public evaluation workbook — 2026-11-08

At the submitter's explicit request, added a rebuilt anonymized derivative with the original sheet/row structure and 420 events. A default-redaction builder replaces identifiers consistently, maps dates to a synthetic sequence and substitutes numerical values; it copies no source package parts or unrestricted text. The first integration run caught an omitted timestamp field in the transform schema; the builder was corrected against the actual source columns rather than changing the import checks. Source/public value comparison found no unchanged values outside explicitly allowed constants/categories, and rebuilding produced identical bytes.

The expanded suite passed all 30 tests with the private original configured; the public-only run passed 29 tests with one expected private-input skip. Public artifact checks cover import/replay, fail-closed state, audit export and XLSX package restrictions. Direct public-workbook import/report passed. These checks establish structural workflow behavior, not answers to the twelve reviewer questions or clinical correctness. The derivative changes dates, durations and policies and must not be used as an outcome-equivalent substitute for the private original.

## End-to-end review before submission — 2026-11-08

Walked the repository the way the reviewer will: a fresh virtual environment from the README, `scripts/check.py`, the full suite with `SENTINEL_WORKBOOK` pointing at the supplied pack (30 of 30 passed), the public and private `import`/`report` commands (420 cases each, exact-file replay creating no cases), `credentials`, `serve` with the API example and an unauthenticated 401, `tick` with and without an injected transport failure, `export` and `verify`, Ruff, the Docker Compose demo, and the hosted CI history on `main`. Every runtime path passed. The review still found presentation defects that a passing suite does not catch: a duplicated section in the executive summary, a validation document that told the reader to run `demo` to generate a workbook, commands that wrote a file silently, a `tick` on an unknown tenant that reported success with no results, and five three-line redirect stubs under `docs/` that nothing linked to. The brief's regulatory windows, customer mix and incidents were quoted in the risks register but never tabulated against the design; that traceability is now in [where we land](01-where-we-land.md) and [degradation](05-degradation-and-regulatory-clock.md). The lesson recorded here is that a green suite verifies invariants, not whether a stranger can follow the artifact.

## Assessment kernel session — 2026-11-08

This section records the session in which the assessment kernel, the data investigation and the remaining written deliverables were produced. It was AI-assisted throughout (the coding agent wrote the code and drafts; the candidate's own review is still required — see the [review walkthrough](16-review-walkthrough.md)). Timestamps are the session date; hours were not tracked.

| Step | Question or hypothesis | Evidence examined | Kept / rejected and why | Mistake or uncertainty, and how it was caught |
|---|---|---|---|---|
| 1 | Is the central problem evidence assembly rather than disposition prediction? | Brief §1–§6; tab 10 (reviewer questions: 11 of 12 are look-ups, question 12 "can I reconstruct this in two years" answered "No"); tab 13 (median 96 active minutes, 7 systems per case, 23% override rate); 14_Incident_Log (AUD-2603). | Kept. Every quoted stakeholder asks for reasoning and reconstruction, not better verdicts; the January full-automation pilot failed on fabricated evidence. The hypothesis was tested, not assumed: if tab 10 had been dominated by "what should I decide" questions the conclusion would differ. | None at this stage. |
| 2 | What does the pack actually contain? | `scripts/inspect_workbook.py` over all 15 tabs: column profiles, overlap detection, exact tenant-scoped product resolution, stability coverage, firmware, timestamps. | Kept as a committed, reproducible script. The first draft classified `*_as_received` columns as timestamps because the heuristic matched "received" — caught by reading the output (420 "invalid timestamps" on a text column) and narrowed to `*_utc`. The carrier tab is `04_Carrier_Contracts`, not a carrier master; the script originally looked for the wrong name. | The first inspection run reported "0 carrier rows"; reading the sheet list exposed the naming assumption. |
| 3 | Which component is hardest to be right about? | The existing kernel already proved workflow invariants (versions, idempotency, audit chain). What it did not do was turn a real alert into an explicit statement of resolved/unresolved entities, selected/rejected evidence and knowledge-time semantics. | Chose the tenant-scoped, temporally correct evidence-resolution and replay kernel (`evidence/assessment.py`) over extending the API or adding a UI. Rejected rewriting the existing analyzer: it stays as the import-time blocker pass; the assessment is a separate, pure function over the stored snapshot so it can be replayed with different `known_at` and corrections. | — |
| 4 | How can knowledge time be modelled when the pack has no recorded-time history? | README tab (extract date 2026-09-14); `07_Alias_Observations.confirmed_on`; `14_Incident_Log.date`. | Kept: workbook rows are treated as known at the extract date; aliases, incidents and explicit correction overlays carry their own recorded time. Rejected: inventing per-row recorded times. This is the honest limit, stated in every assessment's `time_semantics`. | Uncertainty: the extract date is a date, not an instant; treated as 00:00 UTC and documented. |
| 5 | Does the presentation check catch the brief's "study for a different presentation" case? | T-AURA product row cites STB-8597 whose index text reads "… PFS (…) — vial". | The first implementation compared presentation terms across the whole study string, so "PFS" in the product name masked "vial" after the dash and the T-AURA case was **not** flagged. Caught by looking for that specific row after the first `assess-all` run. Fixed by reading the presentation from the part after the em dash, which is the index's naming convention; the conflict count rose from 8 to 23. | A real wrong assumption, detected by checking a known case rather than trusting the aggregate. |
| 6 | Should historical outcome columns be inputs? | README row 45 (`rules_engine_recommendation` holds the assistant draft), row 36 (auto-closed population never audited). | Rejected as inputs. They are listed in `inputs.historical_fields_excluded` and read only by the `assess-all --compare-history` evaluation layer, which reports "review candidates", not errors. A unit test changes `final_disposition` and asserts the assessment hash does not change. | — |
| 7 | Which real cases demonstrate the failure modes? | `scripts/select_demo_cases.py` picks the first event per mode in workbook order. | Kept programmatic selection over hand-picked IDs. Two modes (carrier parent/subsidiary ambiguity, SOP boundary day) do not occur in the pack and are covered only by fictional unit tests; this is stated rather than fabricated. | — |
| 8 | Is the notification window an outcome or a policy input? | README row 46; tab 13 windows; `reg_window_hours` present on 28 rows. | Kept as a *provisional* policy input (it is the window, not the outcome), labelled as such in the assessment and in the LLD; `hours_to_notification` and `reported_within_window` remain excluded. Production takes the window from an approved policy bundle. | Judgement call, recorded in the contradictions register. |
| 9 | Does the regulatory clock survive the case lifecycle? | `test_regulatory_clock_is_unchanged_by_review_signature_and_reopen` (new). | Kept. The first version of the test supplied one evidence kind and failed on the service's own guard requiring all six — the guard is correct; the test was fixed. | A test-authoring mistake caught by the service's fail-closed rule. |
| 10 | Do the cost figures in the risks register reproduce from tab 13? | Tab 13 ceilings: USD 1.10 × 2,050 + USD 0.06 × 11,400 = USD 2,939; self-hosted USD 5.67/h. | USD 2,939 reproduces. "USD 4,082.40" equals 720 hours, not a 730-hour month (USD 4,139.10); corrected in [cost and sizing](14-cost-and-sizing.md). | A rounding assumption found by recomputation. |

Verification for this session: `python scripts/check.py` 53 tests (2 skipped without the pack); with `SENTINEL_WORKBOOK` all 53 pass; Ruff clean; `assess-all` over 420 events in about 2 s. The AI session transcript itself is not in the repository; the brief asks the candidate to keep and submit it separately.
