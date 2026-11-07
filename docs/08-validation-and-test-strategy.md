# Validation and test strategy

## Public-data contract

All committed fixtures are hand-made: four synthetic events and three synthetic product rows. They share field names with the workbook but do not copy customer rows, names, values or outcomes. Their expected output is a manually stated aggregate contract. Synthetic tests cover tenant isolation, aliases, study hazards, half-open time ranges, two-axis corrections, clocks, lifecycle waits/reopen, output guardrails and audit tamper detection.

Workbook integration modules use `pytest.mark.skipif` and skip cleanly when `data/KCCS_Sentinel_Reference_Data_Pack.xlsx` is absent. Normal CI runs the entire suite without that file and a separate unit-only coverage gate. Real-workbook dossiers and detailed logs stay in gitignored local folders. No CI artifact upload contains private output.

## Layers

- Unit tests check missing/ambiguous identity, tenant scoping, invalid numeric/time inputs, wrong presentation, unreadability and guardrails.
- A synthetic golden checks the expected aggregate report; it is not clinical ground truth.
- Hypothesis properties check that an under-reading interval never lowers the observed bound and that disposition waits cannot move notification results.
- Two-axis tests preserve prior knowledge after correction, retain overlaps and enforce tenant/interval boundaries.
- Workflow tests preserve original due instants and prior episodes across waits and reopening; audit tests verify persistence and detect a modified event.
- Fixture CLI end-to-end checks all five expected files, then compares every file byte-for-byte across two runs.
- Optional real-workbook tests read all 15 sheets, verify aggregate results/tenant isolation and replay every historical reopen flag without changing the original duty. That replay is a simulation, not validation of past signed decisions.

## Sanitized measured evidence

Final local and fresh-clone results are recorded below after execution. The evidence contains only aggregate counts; detailed logs and per-case output are not published.

| Executed check | Result |
|---|---|
| Full local Python 3.13.5 suite, workbook present | 49 passed; 99.19% combined statement/branch coverage |
| Entire suite, workbook physically removed | 45 passed, 4 skipped; 95.30% combined coverage |
| Actual workbook | All 15 sheets and 420 events; original bytes unchanged |
| Product references | 297 exact source; 72 unverified alias; 51 missing |
| Notification fixed-hour replay | 14 late; 14 within window; 392 historical not-reportable flags |
| Eligibility | 420 NEEDS_EVIDENCE; zero signed dispositions or proposed closures |
| Repeated CLI outputs | All five files byte-identical across runs |
| Ruff | Check and format gates passed |
| Bandit | No findings in prototype source |
| Runtime dependency audit | No known vulnerabilities reported |
| Public staged payload | Gitleaks found no leaks; tracked-file/PII review performed |
| Docker | Not installed on this box; build/run not executed |

Detailed execution logs and coverage JSON remain under ignored `.local-evidence/`. Hosted CI and fresh-clone verification are checked after publication; local evidence alone is not a claim of hosted success.

## Long-term controls

A changed rule, reference, retrieval index, prompt, model or translation requires reproducible differential evaluation, QA review of clinically material disagreements, sampled unchanged cases, a qualification manifest and a rollback/fallback rehearsal. Historical outcome labels must never become eligibility input features. Extend the regression corpus with independently reviewed incident cases; do not regenerate expected values from the changed implementation.

Production release also needs actual controlled documents, jurisdiction calendars/reportability, signature authority, concurrent batch exposure updates, outbox recovery, tenant-isolation fuzzing and regulator receipt integration tests. These are design gates, not tested features of the local prototype.

At 03:00 Europe/Berlin, alert on missing timer heartbeat, unresolved low-slack obligations, filing failures, stale source watermarks, foreign-tenant retrieval, invalid evidence hashes and budget exhaustion. A deterministic fixture passing nightly does not establish current source correctness. Run independent sampling, source contracts and restore/failover drills.
