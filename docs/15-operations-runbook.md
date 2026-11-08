# Operations runbook: how we know at 3 a.m., six months from now

Scope: how the platform shows that it has stopped working or has started working differently, and what the on-call person does. **Status key:** items marked *(implemented)* exist in the prototype; everything else is **proposed** and untested. Thresholds are proposed starting points to be tuned against a measured 7-day baseline.

## 1. Structured logs

One JSON line per assessment or state change. Example:

```json
{
  "ts": "2027-05-14T03:07:41.212Z",
  "tenant_id": "T-EXAMPLE",
  "region": "eu-cell",
  "event_id": "EVT-000123",
  "case_id": "CASE-000045",
  "assessment_revision": 3,
  "assessment_sha256": "9f2c...e1",
  "manifest": {"code_version": "0.4.0", "schema_version": "7", "rules_version": "R-2027.04", "policy_version": "P-12", "mapping_version": "M-31", "model_version": "none"},
  "known_at": "2027-05-14T03:07:40Z",
  "as_at": "2027-05-14T03:07:40Z",
  "source_versions": {"SYS-01": "cursor-8841", "SYS-05": "file-2027-05-14", "SYS-07": "rev-C"},
  "readiness": "INCOMPLETE_EVIDENCE",
  "conflict_count": 0,
  "missing_count": 4,
  "duration_ms": 182,
  "principal": "svc-assess",
  "idempotency_key": "b1c2...",
  "outcome": "ok"
}
```

Field notes: `assessment_sha256`, `readiness`, and the manifest's code/policy/model values are produced by the prototype today *(implemented)*; `model_version` is `none` on route R0 (doc 14). `known_at` is when the system knew the facts; `as_at` is the effective time being reasoned about. The remaining fields (region, revision, principal, idempotency key, schema/rules/mapping versions) are **proposed**.

**Never log:** document contents or excerpts; free-text reasons, notes or reviewer comments; cross-tenant identifiers (a log line carries exactly one `tenant_id`; no references to other tenants' IDs, names, or document digests); tokens, keys, credentials or session identifiers; batch numbers or patient/product-identifying payloads for tenants with residency restrictions. Log counts and hashes, not text. The prototype's `assess-all` output follows the same rule (aggregates and event IDs only).

## 2. Metrics and alerts

| Metric | Why | Proposed threshold | Page / ticket | First runbook step |
|---|---|---|---|---|
| **Tenant-leak canary**: synthetic cross-tenant probe every 5 min expecting 404 | Isolation is the property that cannot fail silently | Any 200 (or any non-404): page immediately. Also an index-content assertion: no T-MERIDIAN document digest appears in any other tenant's index or cache. Any hit pages. | Page | Runbook 3a |
| Conflict rate and abstention rate per tenant vs 7-day baseline | A spike means source drift or a mapping regression | > 2x baseline over 1 h, or > 3 sigma | Ticket (page if > 5x, or if a spike appears in all tenants) | Runbook 3b step 1: check manifest and mapping changes, then source freshness |
| Source freshness per system: SYS-05 ERP nightly, SYS-01 15-min poll, SYS-06/08 manual | Stale input silently degrades evidence | SYS-01 > 45 min; SYS-05 > 26 h; SYS-06/08 > 30 days since last confirmed export. Beyond threshold, assessments carry a freshness warning and readiness is downgraded | Ticket; page for SYS-01 if any obligation window is under 25% | Runbook 3d |
| **Replay drift**: nightly re-assess a pinned golden set of cases with pinned `known_at` | The detector for "it stopped working silently" | Any `assessment_sha256` change without a manifest change: page | Page | Runbook 3b |
| Evidence package integrity: daily verify of a sample of stored packages | Seven-year retention must stay verifiable | Any verify failure: page | Page | Runbook 3g |
| Dependency failures: circuit-breaker state per source and model provider | Detects outages and sunset | Breaker open > 10 min; for model providers, any open breaker: ticket (decision path unaffected) | Page for a source with an open obligation; ticket for models | Runbook 3d / 3e |
| Deadline risk: obligations with < 25% of window left and not `FILED_PENDING_ACK`; any `OVERDUE`; outbox lag; reminder delivery failures | Regulatory windows are 72 h / 5 d / next business day / 15 d; 14 were missed in two quarters | Any `OVERDUE`: page. < 25% left and unfiled: page the regulatory ops role. Outbox lag > 2 min; any reminder failure: ticket, page if repeated | Page | Runbook 3c |
| Queue age and per-tenant backlog; alerts/10 min per facility | Storm detection (INC-2502 was 1,912 alerts in 38 min) | > N alerts / 10 min from one facility, N = 5x baseline (proposed 50); oldest queue item > 15 min | Ticket; page if oldest > 60 min | Runbook 3f. The obligation count must equal the genuine-event count even when grouping is engaged |
| Schema/version skew between cells | A cell on a different manifest produces different hashes | Any cell whose deployed manifest differs from the release record for > 1 h | Ticket | Runbook 3h step on version check; redeploy the intended manifest |

## 3. Runbooks

### 3a. Tenant-leak canary fired
1. Page security and platform on-call. Treat it as a confirmed incident until disproved.
2. Freeze: disable the offending route or the tenant's read access via the kill switch; do not delete anything.
3. Capture evidence: the probe request, response, principal, tenant IDs, trace; store as a hashed record, not in chat.
4. Determine scope: query access logs (counts and tenant IDs only) for the same route and window; for the index assertion, list which index or cache held the foreign digest.
5. For a T-MERIDIAN digest in another tenant's index, quarantine that index; rebuild it from source for the affected tenant only. Cl.22 forbids reuse.
6. Fix, then run the full replay and the cross-tenant test suite (section 4) before re-enabling.
7. Notify affected tenants through regulatory ops and QA duty officer as the DPA and contracts require; record the notification time.
8. Post-incident: add the missing probe/test; record the timeline.

### 3b. Replay drift detected
1. Confirm the alert: is the manifest (code/schema/rules/policy/mapping/model) identical in both runs? If it changed, this is a version event, not drift; record it and rebase the golden set deliberately.
2. If the manifest is identical, freeze deploys to the cell.
3. Diff the two assessments field by field (hash, sources, conflicts, missing inputs). Common causes: a source row changed in place (a mutated source version), an unpinned dependency (time, locale, ordering), a mapping edited in place.
4. Check `source_versions` used in each run; a changed source version without a new version ID is a source-integrity defect.
5. Roll back (section 4) to the last manifest whose golden replay was clean.
6. Run the full replay on the fix and show QA the decision differences (the quality sponsor's condition applies to the fix as well).
7. Identify live assessments produced during the drift window; re-assess them as new revisions (never mutate); notify the case owners.

### 3c. Obligation approaching its window with no filing
1. Identify the obligation, jurisdiction, window end, and current state (the alert ID, not the document).
2. Page the regulatory ops role; confirm the human owner and delegate.
3. Confirm the reminder was delivered (outbox and delivery records). If delivery failed, escalate by phone, not by the system that failed.
4. Check whether evidence is blocking (`BLOCKED_BY_CONFLICTS` or `INCOMPLETE_EVIDENCE`). A filing may proceed on available evidence; the platform never decides or files by itself.
5. Record the human's filing and the acknowledgement. State stays `FILED_PENDING_ACK` until the acknowledgement is received.
6. If the window passes, mark `OVERDUE`; start the incident procedure and notify the VP Quality & Regulatory.
7. Post-incident: why was the reminder not acted on; adjust thresholds.

### 3d. Source stale or ERP file late
1. Identify the system (SYS-05 nightly, SYS-01 poll) and last good version/cursor.
2. For SYS-05, check the tenant's SFTP drop and manifest/digest. Late files are expected 3-6 times a month; if the file is partial or the digest mismatches, quarantine it. Never apply a partial file.
3. Verify that affected assessments show the freshness warning and downgraded readiness; if not, treat as a defect.
4. Contact the tenant's integration contact (or use SYS-01 vendor support for polling).
5. When the file arrives, ingest it as a new source version; re-assess open cases as new revisions.
6. For SYS-06/08 (manual exports), ask the QA owner for a fresh controlled export with the attestation.
7. If the stale source affects an open obligation, follow 3c.

### 3e. Model provider down or sunset notice
1. Confirm via the circuit breaker which provider and which tenants route to it.
2. Switch the affected tenants (or all tenants) to **R0, the no-LLM route**, with the per-tenant kill switch. Nothing in the decision path depends on a model; reviewers lose only the narrative.
3. Verify the log shows `model_version: none` for new assessments and that conflict/missing counts are unchanged.
4. For a sunset notice (Provider B has 30-day notice): inventory tenants and prompts using it, and pick a replacement with the same residency (never B for EU tenants).
5. Replace the model only as a new manifest version; run the full replay and show QA the diffs before enabling (the quality sponsor's condition).
6. Re-enable per tenant, starting with one.
7. Record cost impact (doc 14 table).

### 3f. Alert storm
1. Confirm the facility and tenant; check whether the burst is a genuine event or a sensor/gateway fault (compare against SYS-01/02 health).
2. Verify grouping is engaged. Check that **obligation count equals genuine-event count** (one obligation per genuine event, not one per alert, and none dropped).
3. Watch queue age and backlog; if oldest item exceeds 60 min, add reviewers from the next regional pool.
4. Confirm the other tenants' queue age and processing are unaffected (per-tenant backpressure).
5. Check that the outbox and reminders still deliver.
6. After the storm: reconcile grouped alerts to the obligations and the audit trail; record the burst as a regression case (INC-2502 shape).

### 3g. Package integrity failure
1. Identify the package, tenant, region, and storage location. Do not edit the package.
2. Re-run the verification (the prototype's `verify-assessment` for packages; `verify` for audit bundles) to rule out a tool error.
3. Verify which layer failed: assessment hash, a section hash, or the package hash.
4. Compare with the replica/backup copy of the same package; restore from the intact copy if one is available.
5. If no copy is intact, re-derive by re-assessing with the pinned `known_at` and source versions; if the hash differs, the original is irrecoverable; record it, notify QA and the VP Quality & Regulatory.
6. Scan a wider sample (same day, same storage) to bound the problem.
7. Investigate cause (storage corruption, an unauthorised write, a bug in serialisation) and treat any unauthorised write as 3a-class.

### 3h. Regional cell unavailable
1. Confirm which cell and which tenants (residency pins tenants to a cell); other cells continue unaffected.
2. Do **not** fail over across a residency boundary; tenant data stays in the region.
3. Regulatory ops: list obligations with windows closing during the outage; start manual filing from the tenants' own records where needed. Windows keep running while the cell is down.
4. Within the region, fail over to the standby (if provisioned) using the last released manifest.
5. After recovery, check version skew (manifest equals release record), outbox drain, and no duplicate obligations (idempotency keys).
6. Re-run the replay canary and the leak canary before declaring recovery.
7. Reconcile any manual filings back into the case record.

## 4. Ownership, escalation, rollback

| Role | Owns |
|---|---|
| Platform on-call | Infrastructure, deploys, canaries, drift, cells, dependency alerts |
| QA duty officer | Evidence quality, package integrity, replay diffs, tenant communication on quality |
| Regulatory ops | Obligation windows, filings, acknowledgements, regulator contact |

**Escalation ladder (all times proposed):** page acknowledged within 10 min, otherwise secondary on-call at 10 min; engineering lead at 30 min; VP Quality & Regulatory at 60 min for any leak, any `OVERDUE`, or any unverifiable package. Leak canary and `OVERDUE` skip the ladder and notify the lead and the VP immediately.

**Rollback mechanics:**
- Deploy the previous manifest (code, schema, rules, policy, mapping, model together); never a partial rollback.
- Mappings and policies roll back as **new versions** whose content equals the old one; they are never deleted or edited in place.
- Assessments are never mutated. Anything produced under a bad version is superseded by a new revision, with the earlier revision retained and linked.
- Schema migrations are expand/contract so that rollback does not need a data restore.

**Post-incident replay requirement:** after any fix, run the full replay over the known-outcome case set and show QA where decisions differ from the previous manifest and why, before re-enabling. This is the quality sponsor's condition, applied to the fix as to any change.

## 5. What the prototype already provides

| Capability | Where | Status |
|---|---|---|
| Deterministic `assessment_sha256` (canonical JSON, sorted keys, SHA-256) and a manifest (code version, assessment version, policy version, workbook hash, Python version, corrections hash). Replay drift is testable today: same snapshot and same `known_at` produce the same hash, covered by `test_repeated_execution_is_deterministic` in `prototype/tests/unit/test_assessment.py` | `prototype/src/sentinel/evidence/assessment.py` | Implemented |
| `verify-assessment` (assessment, section and package hashes) and `verify` (audit bundle integrity) | `prototype/src/sentinel/cli.py`, `evidence/assessment.py`, `workflow/service.py` | Implemented |
| Cross-tenant access returns 404 (route not found), not 403 | `prototype/src/sentinel/api/http.py` | Implemented |
| `tick` delivers reminders at least once and records failure rather than swallowing it; it never marks a filing complete | `prototype/src/sentinel/workflow/service.py` | Implemented |
| `assess-all` summary: totals, readiness counts, disposition counts (all `ABSTAIN`), conflict kinds, product resolution, events with conflicts; usable as the abstention and conflict baseline | `prototype/src/sentinel/cli.py` | Implemented (batch; not a live metric) |
| Readiness values `BLOCKED_BY_CONFLICTS`, `INCOMPLETE_EVIDENCE`, `EVIDENCE_ASSEMBLED`, `missing_inputs`, `conflicts` | assessment output | Implemented |

**Everything else in this document is proposed:** the structured log emitter and its extra fields, the metrics pipeline, the canaries, freshness tracking and readiness downgrade, circuit breakers and per-tenant kill switch, storm grouping, paging integration, cell failover, and the nightly golden-set job. The prototype shows that the hash-based detector is feasible; it does not run one.
