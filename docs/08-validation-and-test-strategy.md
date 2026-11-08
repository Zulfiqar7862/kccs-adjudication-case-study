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


## Assessment kernel validation

The required validation cases for the chosen component map to tests as follows. "Unit" tests run on small, clearly fictional tables in `prototype/tests/unit/test_assessment.py`; "public" tests run on the anonymized workbook (`prototype/tests/integration/test_assessment_workbook.py`); "pack" tests in the same file run only when `SENTINEL_WORKBOOK` points at the supplied pack. Cases marked *design-level* are outside the prototype and are acceptance tests for the proposed production system in the [LLD](13-detailed-design-lld.md).

| Validation case | Test | Scope |
|---|---|---|
| Same identifier under multiple tenants | `test_same_identifier_under_two_tenants_resolves_only_within_tenant` | unit |
| Unauthorized cross-tenant access | `test_cross_tenant_access_is_indistinguishable_from_missing`; `test_every_public_event_abstains_and_hashes_deterministically`; CLI `assess` with the wrong tenant in `test_cli_assess_all_and_package_verification` | unit, public |
| Misleading stability file path | `test_misleading_file_path_does_not_transfer_ownership` | unit |
| Wrong product presentation | `test_wrong_presentation_is_a_conflict_not_a_match`; the pack test asserts the mode occurs in the supplied data | unit, pack |
| Missing and unreadable stability evidence | `test_missing_and_unreadable_stability_evidence` | unit |
| Overlapping SOP revision windows | `test_overlapping_sop_revisions_are_a_conflict`; the public test asserts overlaps are detected in the anonymized pack | unit, public, pack |
| Policy interval boundaries | `test_policy_interval_boundaries_are_half_open_and_flagged` | unit (the pack has no boundary-day case) |
| Ambiguous site scope | `test_site_specific_scope_requires_annexure` | unit |
| Missing product reference | `test_missing_product_reference` | unit |
| Untrusted alias mapping | `test_alias_observations_are_surfaced_but_never_resolve` (includes an alias confirmed after `known_at`) | unit, pack |
| Historical replay without future knowledge | `test_historical_replay_hides_facts_recorded_after_known_at`; the pack test replays every bulletin-affected event at `known_at` 2026-01-01 | unit, pack |
| Repeated execution / idempotency | `test_repeated_execution_is_deterministic`; public hash equality | unit, public |
| Source correction with immutable old assessment | `test_correction_yields_new_assessment_and_leaves_original_intact`; replayed on the pack by `scripts/select_demo_cases.py` | unit, pack (script) |
| Affected firmware with uncertain correction | `test_affected_firmware_is_flagged_without_a_fixed_correction` | unit, pack |
| Conflicting inputs fail safely | `test_conflicting_facility_records_fail_safely`; `test_parent_and_subsidiary_contracts_are_ambiguous`; `test_untagged_bms_source_is_quarantined_for_attribution` | unit |
| Separation of historical outcome and prototype input | `test_historical_outcomes_are_listed_but_never_read`; the pack test asserts `final_disposition` is never among the fields read | unit, public, pack |
| Notification clock starts at alert receipt | `test_notification_clock_starts_at_alert_receipt` | unit |
| Evidence waits do not pause the clock | workflow tests: the obligation deadline is unchanged through review and reopen (`test_workflow.py`) | integration |
| Next-business-day needs explicit calendar and timezone | not implemented; the assessment states `calendar_semantics` as a requirement | design-level |
| Failed delivery is not marked successful | `tick --fail` path in `test_cli.py` and `test_workflow.py` | integration |
| Storm traffic cannot discard obligations | not implemented (single-process prototype) | design-level: [LLD §6](13-detailed-design-lld.md) |
| Package tampering detected | `test_package_verification_detects_tampering`; CLI `verify-assessment` on a tampered file | unit, public |

## Verification record

Results from the end-to-end pass taken immediately before submission (2026-11-08, second pass after adding the assessment kernel). Private outputs stayed local; only aggregates are recorded.

| Check | Command | Result |
|---|---|---|
| Fresh install from the README | `python3 -m venv .venv && python -m pip install -r requirements.txt` | Installs `sentinel-adjudication` and `defusedxml==0.7.1` only |
| Compile, public tests, HTTP lifecycle demo | `python scripts/check.py` | 53 tests, 2 skipped (private pack not configured); demo lifecycle PASS |
| Full suite against the supplied workbook | `SENTINEL_WORKBOOK=<pack> python scripts/check.py` | 53 tests, all passed |
| Workbook inspection | `python scripts/inspect_workbook.py <pack> --output-dir artifacts/private` | 15 sheets, 420 events; findings in `workbook-inspection.json` |
| Supplied workbook import and report | `python -m sentinel --db … import <pack>` then `report --output …` | 420 cases created, all `WAITING_EVIDENCE` with blockers; exact-file replay created 0 |
| Demo case selection and replays | `python scripts/select_demo_cases.py --db … --output-dir artifacts/private` | 9 of 11 failure modes found in the pack; knowledge-cutoff replay and correction replay produced distinct hashes; the original package still verifies |
| Coverage summary | `python -m sentinel --db … assess-all --compare-history --output …` | 420 ABSTAIN; 234 BLOCKED_BY_CONFLICTS, 186 INCOMPLETE_EVIDENCE; 118 review candidates; about 2 s |
| Public anonymized workbook | same commands on `data/anonymized-evaluation.xlsx` → `artifacts/public/` | 420 ABSTAIN; 78 BLOCKED_BY_CONFLICTS, 342 INCOMPLETE_EVIDENCE (firmware, readability and constraints are redacted there) |
| API | `serve`, `scripts/api_example.py`, unauthenticated request | 200 with bearer, 401 without |
| Reminder stub, export and verify | `tick --tenant …`, `tick --fail`, `export`, `verify` | Reminders delivered / retried; exported bundle `valid: true` |
| Lint and container | `ruff check …`, `docker compose run --build --rm prototype` | Passed |
| Hosted CI | GitHub Actions on the pull-request head | The earlier head passed all 20 jobs; re-check the PR after the final push |

Re-run this table before any later submission; it is the acceptance check for "does it still work", not a clinical or production qualification.
