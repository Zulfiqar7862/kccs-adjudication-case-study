# Submission checklist

Maps each evaluator expectation to where it is met. Status values: **Done** (exists and was run or read), **Partial** (some of it exists), **Design-only** (specified, not built), **Candidate action** (Zulfiqar must do it), **Verify before sending** (not confirmed when this file was written). Docs 12–15 were written in parallel with this file; confirm each cited section exists.

## 1. Expectations → evidence

| # | Evaluator expectation | Where satisfied | Status | Note |
|---|---|---|---|---|
| 1.1 | Requirements mapped to the brief and the pack | `docs/01-where-we-land.md` "Requirements mapped to evidence"; incident mapping table in the same file; `docs/09-risks-assumptions-and-open-questions.md` (board commitments) | Done | Mapping cites brief sections and pack sheets. |
| 1.2 | What is deliberately not built, and why | `docs/01-where-we-land.md` "Deliberate non-goals"; `docs/09` "Explicit exclusions"; `docs/16-review-walkthrough.md` §1 (17–19 min) | Done | No live connectors, OCR, model call, regulator delivery, identity, legal calendars, WORM. |
| 1.3 | Phased rollout, first customer, timeline reasoning | `docs/01` "Why this tenant first"; `docs/10-future-roadmap.md` (gates, expansion waves, nine-month target) | Done | Day 90 is a gate, not a promise. Re-read the tenant choice reasoning once more before the call. |
| 1.4 | Silent or contradictory areas and positions taken | `docs/09` "Silent or contradictory areas and positions taken"; `docs/12-data-findings-and-assumptions.md` | Done / Verify before sending (doc 12) | Doc 12 is being written separately; check it covers the pack's own contradictions. |
| 1.5 | Board items believed incorrect, with counterargument | `docs/09` (six commitments); `docs/16` §3 Q2 (70% closure) | Done | 70% as a go-live number, nine months for 34 tenants, absolute "no late filings". |
| 2.1 | Complete architecture | `docs/02-system-architecture.md`; `docs/13-detailed-design-lld.md` | Done / Verify before sending (doc 13) | |
| 2.2 | Components and boundary reasoning | `docs/02` "Deployment and component boundaries", "Source adapters, identity and ordering" | Done | |
| 2.3 | Data modelling including "as at a date" | `docs/03-data-model.md` (two time axes, inspector worked example); `assessment.py` (`as_at`, `known_at`); tests `test_historical_replay_hides_facts_recorded_after_known_at`, `test_policy_interval_boundaries_are_half_open_and_flagged` | Partial | Production model is bitemporal (design); prototype has one snapshot, so replay is real only for alias, incident and correction rows. |
| 2.4 | Lifecycle: transitions, waiting, manual steps, reopened months later | `docs/04-case-lifecycle.md`; `prototype/tests/integration/test_workflow.py`; `python -m sentinel demo` | Done (mechanics) | Delayed-correction and reopening are tested on fictional data only. |
| 2.5 | Degradation and regulatory clock | `docs/05-degradation-and-regulatory-clock.md`; test `test_notification_clock_starts_at_alert_receipt`; `docs/15-operations-runbook.md` | Partial | Clock is a stub with a provisional policy (`notification-policy-stub-v1`); no calendars, no receipts. |
| 2.6 | Versioning and deployment pipelines | `docs/06-versioning-and-deployment.md`; `docs/16` §4a | Design-only | Prototype stamps `ASSESSMENT_VERSION`, `POLICY_VERSION` in packages. No pipeline built. |
| 2.7 | Diagrams | Mermaid in `docs/02`, `03`, `04`, `05`, `06`, `10` | Verify before sending | Confirm each renders on GitHub (preview the files). |
| 3.1 | The single most critical and difficult component | `docs/01` "Critical working component"; `docs/16` §1 (6–9 min); `prototype/src/sentinel/evidence/assessment.py` | Done | Temporal, tenant-scoped evidence assessment that abstains on missing or conflicting evidence. |
| 3.2 | Execution against the provided workbook, with stubs | `python -m sentinel --db prototype/output/private.db import <pack>` then `assess-all`; `prototype/tests/integration/test_assessment_workbook.py`; `artifacts/private/assessment-summary.json` | Done (local run) | 420 events: ABSTAIN 420, BLOCKED_BY_CONFLICTS 234, INCOMPLETE_EVIDENCE 186. Private outputs are not committed. Re-run with the real pack before sending. |
| 3.3 | Demonstrable cases | `artifacts/private/demo-cases.json` (from `scripts/select_demo_cases.py`); `docs/16` §1.1 | Done | EXC-110336, EXC-112135 and six others, selected by program, not by hand. |
| 3.4 | Validation approach now | `docs/08-validation-and-test-strategy.md`; `scripts/check.py`; unit and integration tests | Done | 54 tests pass; 2 skip without the pack. |
| 3.5 | Validation approach long-term (monitoring at 3 a.m., six months on) | `docs/08` "Long-term reliability approach"; `docs/15-operations-runbook.md` | Partial | Retrospective evaluation against known outcomes is specified, not run: the pack has no ground truth and the historical outcomes are never read by the kernel. |
| 4.1 | Discarded ideas, alternatives, lessons | `docs/07-working-log.md` "Alternatives considered and discarded" | Done | |
| 4.2 | Wrong assumptions and how they were identified | `docs/07` "Assumptions that turned out wrong"; `docs/11-ai-review-corrections.md` | Done | Candidate must confirm the entries match what actually happened. |
| 4.3 | Abandoned approaches | `docs/07` (alternatives, hosted verification feedback, layout revision) | Done | |
| 4.4 | Original AI sessions kept (brief §8 D) | Not in repo | Candidate action | Export and deliver the transcripts; the authored log does not replace them. |
| 5.1 | Covering note: how long you spent | `docs/16` §5 | Candidate action | Hours left blank deliberately. |
| 5.2 | 20-minute presentation and conversation prep | `docs/16` §1–4 | Done | Rehearse; deep-dive topics named in §2. |
| 5.3 | Submission to the brief's §10 address | `docs/16` §5 | Candidate action | |

## 2. Final quality gate

| Gate | Evidence | Status | Note |
|---|---|---|---|
| Re-read evaluator expectations | Table 1 above | Candidate action | Re-read against the email once more before sending. |
| Consistent names and semantics across design and implementation | `docs/13` terms vs `assessment.py` (`as_at`, `known_at`, `recorded_at`, package, abstain) | Verify before sending | Grep that `known_at`, `as_at`, `recorded_at`, `policy_bundle` mean the same in docs 02–06, 13 and code. |
| Imports and dependencies verified | `python -m pip check`; `ruff check .` | Verify before sending | Run both in a clean venv. |
| Clean install, test, demo | `python scripts/check.py`; `python -m sentinel demo` | Verify before sending | Last recorded: 54 tests pass (2 skipped without the pack; 53 with `SENTINEL_WORKBOOK` set). Repeat on a fresh clone. |
| No expected result hardcoded from historical outcomes | `test_historical_outcomes_are_listed_but_never_read`; `ALLOWED_EVENT_FIELDS` in `assessment.py` | Done | The 118 "review candidates" are re-review prompts, not errors. |
| Missing evidence is not treated as favourable | Readiness states INCOMPLETE_EVIDENCE and ABSTAIN; `test_missing_and_unreadable_stability_evidence`, `test_missing_product_reference`, `test_alias_observations_are_surfaced_but_never_resolve` | Done | |
| Tenant isolation | `test_same_identifier_under_two_tenants_resolves_only_within_tenant`, `test_cross_tenant_access_is_indistinguishable_from_missing`, `test_misleading_file_path_does_not_transfer_ownership`; HTTP 404 in `test_http.py` | Done (application level) | Single SQLite file; production needs per-tenant keys and storage (Cl.22 for T-MERIDIAN; doc 14 §4). |
| Temporal replay | `test_historical_replay_hides_facts_recorded_after_known_at`, `test_correction_yields_new_assessment_and_leaves_original_intact`, `test_repeated_execution_is_deterministic`, `test_package_verification_detects_tampering` | Done (limited) | Vacuous for rows without a recorded time (docs/16 §2 i). |
| Generated files exist | `artifacts/private/`: `assessment-summary.json`, `demo-cases.json`, `demo-correction.json`, `workbook-inspection.{json,md}`, `cases/`; `artifacts/public/` from the anonymized workbook | Done (local) | `artifacts/private/` is gitignored; `artifacts/public/` is tracked. Confirm nothing from `private/` is staged. |
| Passing tests vs unexecuted checks | `docs/08` verification record; `docs/16` §1.2 | Partial | Not executed: any clinical correctness check, regulator delivery, load or alert-storm test, WORM retention, retrospective evaluation, real connectors. |
| Residual risks recorded | `docs/09-risks-assumptions-and-open-questions.md` | Done | |
| Unnecessary infrastructure removed | Repository tree; `requirements.txt` | Verify before sending | Look for unused scripts, stale generated files, and unused dependencies. |
| Privacy: no personal names; workbook and private outputs not committed | `.gitignore` (`*.xlsx`, `artifacts/private`), `data/`, docs | Verify before sending | Tenant codes are used; decide the stance (docs/16 §6). Search the tree for names from the brief and pack. |
