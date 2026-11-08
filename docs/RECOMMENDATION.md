# Recommendation: make evidence complete, not autonomous

## Decision

Proceed with a bounded, human-controlled evidence workflow and a gated, single-site EU pilot. Do not authorize automated dispositions, cross-tenant precedent retrieval, or a general-purpose model in the initial release. The product should make a human decision supportable and reconstructable; it must not turn incomplete indexes into a recommendation or a favorable assumption.

The proposed first pilot is referenced only as **the EU pilot tenant** (`12_Tenant_Constraints`, row 2). Its residency position, signatory roles, auditability needs, source ownership, and permitted processing define a narrow pilot boundary—not permission to onboard other tenants or reuse their data. The brief’s four deliverables are addressed below: **A. Where you land, and why; B. The design; C. Something running; D. Your working log.**

## A. Where you land, and why

The operational problem is evidence assembly and accountable timing, not a lack of automated verdicts. The reference pack reports 11,400 monthly alerts and 2,050 human-adjudicated cases; these are source-pack aggregates, not independently validated forecasts. The dataset is stratified and cannot establish population rates or prove a pilot outcome. Historical recommendations, dispositions, and notification records are not correctness labels for new cases.

The system should preserve source/version lineage, timestamps, reviewer rationale, and audit events; show ambiguity and missing sources; keep the notification clock separate from disposition; and retain a named human as the final decision authority. Require an explicit go/no-go before the prototype is used as an operational review workspace.

### Requirements mapped to evidence

| Requirement | Source mapping | Design response and limit |
|---|---|---|
| Reconstruct why a human reached a disposition | Brief A/B; `10_Reviewer_Questions`; `08_Reviewer_Queue_Log` | Preserve source and version references, row provenance, recorded evidence, reviewer rationale, revisions, and verifiable audit exports. Agree retention, restore, and response-time controls before promising an on-demand service level. A hash chain is not immutable retention. |
| Select the applicable procedure and supporting study | Brief B; `05_SOP_Index`; `06_Stability_Index` | Return tenant-scoped candidates with effective-date context and provenance. Missing, unreadable, overlapping, or conflicting required records block readiness. An index match is not proof that the underlying source is valid or applicable. |
| Preserve measurement context and uncertainty | Brief B; `01_Excursion_Events`; `11_Systems_Inventory` | Retain original readings and times; distinguish alert time from excursion time; surface gaps, duplicates, ordering, interpolation, and source freshness. Never synthesize readings or silently correct measurements. |
| Keep customer data and policy boundaries isolated | Brief A/B; `12_Tenant_Constraints`, row 2 for the anonymized EU pilot constraint; `03_Facility_Registry` | Scope every lookup, write, index, export, and notification item by tenant. Verify residency, source tags, signatories, language, and SOP ownership for the pilot. A pilot approval does not transfer to another tenant; no shared precedent search. |
| Protect reporting clocks through review, reopen, and outage | Brief A/B; `01_Excursion_Events`; `13_Volume_And_Cost` for modeled capacity assumptions | Derive the obligation from the original alert time under an explicit, versioned policy. Keep notification separate from disposition; reopening must not restart the clock. Persist and expose backlog and missing-policy states. A local reminder is not external delivery or a regulator receipt. |
| Preserve human authority and independent approval | Brief A/B; `12_Tenant_Constraints`, row 2 | Record who reviewed and signed. Enforce the approved pilot signatory policy and reviewer/signatory separation. The prototype’s local dual-signature text heuristic is not a production authorization policy or qualified electronic signature. |
| Deliver a working and honestly evaluated artifact | Brief C/D; synthetic tests and source tree | Demonstrate implemented local behavior publicly with synthetic data and privately against the supplied workbook. Report failed checks and integration gaps; do not represent prototype behavior as validated performance or production readiness. |

## B. The design

1. **Ingest one authorized snapshot at a time.** Keep workbook digest, source sheet/row, and import observation time. Exact replay is idempotent; a different snapshot is rejected rather than silently merged. Reconciliation and multi-source refresh need an explicit design.
2. **Analyze for evidence readiness, not disposition.** Resolve candidates within tenant and time context. Missing or ambiguous required evidence blocks review. Keep source indexes non-authoritative; reviewer attestations must refer to recorded evidence.
3. **Keep clocks and decisions separate.** Create the reporting obligation from alert data and an approved tenant/jurisdiction policy. Do not infer a universal deadline, reset the clock on case reopen, or equate a reminder attempt with successful external notification. Human-attested receipt remains unverified until an appropriate integration and evidence process exist.
4. **Make workflow changes attributable and concurrency-safe.** Require expected case versions, idempotency keys, role checks, and an append-only event history. Preserve prior revisions on reopen. Hash-chain verification detects some alteration but does not provide WORM retention, legal non-repudiation, or factual validation.
5. **Treat the current implementation as local-only.** The repository currently provides a Python/SQLite service, a loopback HTTP adapter, CLI, workbook reader, and synthetic demo. Static bearer credentials, SQLite durability, notification processing, and policy parsing are prototype boundaries. Production identity, TLS, managed durable storage, verified integrations, recovery procedures, and validated retention remain separate work.

## C. Something running

**Chosen critical component: the transactional evidence/lifecycle/clock kernel.** Its hardest invariant is that incomplete or changed evidence must never silently become an approved disposition, while an independent regulatory deadline continues through waits, retries and reopening. A dashboard would not establish that invariant; durable transactions, independent actors, packet versions and failure-path tests do. External evidence and filing dependencies are explicitly stubbed rather than represented as successful integrations.

The current source implements workbook snapshot import, tenant-scoped candidate analysis and blockers, a SQLite case/revision workflow, evidence review, independent signatures, optimistic versioning, idempotency, hash-chained audit export/verification, notification obligations, and an internal reminder outbox. A manually recorded receipt is explicitly human-attested, not delivery-confirmed. `tick` is an internal stub and does not file with or notify a regulator. The evidence analyzer reports candidates and blockers; it does not adjudicate.

The current code does **not** implement production identity or TLS, external document/source retrieval, an external notification or filing integration, independently verified receipt ingestion, multi-snapshot reconciliation, WORM retention, or automated decision recommendations. Public examples and tests must remain synthetic. Private workbook checks are opt-in through an explicit `SENTINEL_WORKBOOK` path and must not emit or commit raw data or reports.

### Six board commitments: qualify before accepting as guarantees

| Commitment in the brief | Recommendation |
|---|---|
| Median alert-to-signed-disposition under 24 hours by the end of the first full quarter after go-live | Treat as a monitored target, not a promise. Define eligible-case population, pause rules, baseline, and safety guardrails; the source-pack median is 6.2 days. Do not rush decisions or waive evidence to meet a clock. |
| At least 70% of alerts closed without human review | Do not optimize this quota before validating the denominator, false closures, and source quality. The pack reports about 64% current rules-engine closures while also describing an approximately 82% non-actionable alert share; those are not interchangeable, validated rates. No automated disposition is in scope. |
| Full decision basis produced within one hour for seven years | A useful requirement, but it needs tested retrieval, backup/restore, access control, and an approved retention regime. The local hash chain is not WORM storage, and the prototype does not establish either the one-hour service level or seven-year retention. |
| Stay within the cost ceiling | The modeled inference/retrieval allowance is **$2,939/month** against a **$3,000/month** ceiling, leaving **$61/month** before omitted ingestion, storage, indexing, retention, and operations. One always-on self-hosted instance is modeled at **$4,082.40/month**, above that ceiling before other costs. These scopes are not equivalent to a complete production budget. |
| No notifiable deviation reported outside its applicable window | Zero late notifications is an outcome to measure and govern, not a software guarantee. First approve policy and clock inputs, then test backlog, outage, escalation, delivery evidence, and manual fallback. The reminder stub does not deliver a filing. |
| First customer live within 90 days; all 34 within nine months | Use day 90 as a go/no-go for one bounded EU pilot, not a promise of production readiness. The 34-tenant target requires individual residency, data-use, source, signatory, and operating-control review. Broader onboarding in months 4–9 or later remains conditional. |

All six commitments should have named owners, definitions, and stop criteria before they become acceptance gates. A target is not evidence that it can be met safely.

## Delivery and decision gates

- **Days 0–30 — define and prepare:** confirm the EU pilot boundary, approved source inventory and ownership, residency and access controls, SOP/study interpretation, signatories, notification policy and timezones, baseline denominators, retention/restore needs, and stop rules. Do not load live records until approval is documented.
- **Days 31–60 — shadow and reconcile:** compare synthetic or explicitly authorized pilot packets against independent human reconstructions. Measure source completeness, temporal selection, tenant isolation, audit export, missing-source handling, backlog, and clock calculations. Keep the tool advisory and non-dispositive.
- **Days 61–90 — go/no-go:** allow review-workspace use only after QA, security, data-governance, and operational acceptance of the prior gates. Otherwise extend shadow mode, narrow scope, or stop. Human disposition authority remains explicit.
- **Months 4–9 and beyond — conditional expansion:** evaluate each tenant and site independently for residency, data-use restrictions, provenance, tags, freshness, policy, signatories, recovery, and support. Do not infer that the first pilot authorizes a multi-tenant deployment.

## Explicit exclusions

- **Automated release/destroy or other dispositions:** rejected because the evidence is incomplete and historical labels are not ground truth; accountable human authority remains required.
- **A general-purpose or cross-tenant model/precedent service:** rejected for the initial scope because it adds data-use, residency, leakage, change-control, and validation risks without being needed for evidence assembly.
- **Fuzzy identity resolution, guessed SOP limits, fabricated telemetry, or silent correction:** excluded because uncertain matches and missing records must remain visible blockers, not confident-looking facts.
- **A universal deadline or clock reset on reopen:** excluded because policies vary and reopening does not change when the original alert occurred.
- **Claims of salvage, savings, compliance, accuracy, or guaranteed service levels:** excluded until prospectively measured against agreed baselines and complete costs. The stratified workbook sample is not a population estimate.

## Silent or contradictory areas and positions taken

| Gap or tension | Position pending accountable confirmation |
|---|---|
| A universal automated-closure target versus tenant-specific signatories and incomplete SOP/stability indexes (`05_SOP_Index`, `06_Stability_Index`, `12_Tenant_Constraints`) | No automated disposition. Index candidates cannot establish the underlying document's applicability or clinical limits. QA must validate the actual source evidence and authorized policy. |
| “As at” could mean applicable then or known then (brief B) | Model both valid time and recorded time in production. The prototype only has one snapshot's observation time plus SOP effective dates; it does not pretend to reconstruct unavailable historical knowledge. |
| Reportability, calendars, detection semantics and legally sufficient receipt are not fully specified (`01_Excursion_Events`, `12_Tenant_Constraints`) | Preserve original alert timestamps; use supplied windows only as provisional inputs. Unknown windows require urgent manual review, not exemption. A stored human receipt is not independently verified delivery. |
| Current closure and non-actionable percentages use different denominators (`13_Volume_And_Cost`) | Do not infer automated accuracy or savings from their difference. Establish prospective definitions and independent false-safe-closure evaluation. |
| Seven-year auditability without a specified retention start, legal-hold or deletion policy (brief board requirements) | Archive immutable source/version evidence in the production design; QA/legal must approve retention semantics. Local hashes are not sufficient. |
| A fixed onboarding schedule without validated connector readiness or full operating costs (brief; `11_Systems_Inventory`, `13_Volume_And_Cost`) | Treat dates as conditional gates. Confirm source access, total cost and recovery staffing before widening the pilot. |
