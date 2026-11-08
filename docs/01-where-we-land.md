# Where we land

## Decision

Proceed with a bounded, human-controlled evidence workflow and a gated, single-site EU pilot. Do not authorize automated dispositions, cross-tenant precedent retrieval, or a general-purpose model in the initial release. The product should make a human decision supportable and reconstructable; it must not turn incomplete indexes into a recommendation or a favorable assumption.

The proposed first pilot is referenced only as **the EU pilot tenant** (`12_Tenant_Constraints`, row 2). Its residency position, signatory roles, auditability needs, source ownership, and permitted processing define a narrow pilot boundary—not permission to onboard other tenants or reuse their data. The brief’s four deliverables are addressed below: **A. Where you land, and why; B. The design; C. Something running; D. Your working log.**

### Why this tenant first

| Reason | Where it comes from |
|---|---|
| Its renewal is already conditional on exactly the capability this design is built around: producing, for a dated disposition, the SOP revision in force, the stability data relied on, the temperature series, and the approver. | Brief §3 (March inspection), customer quote in §4, board commitment 3 |
| Its data-processing agreement fixes residency in Europe, so the pilot forces the regional-cell and tenant-scoping design to be real from day one rather than retrofitted. | Brief §4 (customer quote); `12_Tenant_Constraints`, row 2 |
| It asks to be told which version produced a recommendation and when that changes—the same requirement Dr Rao's pre-change replay condition imposes. | Brief §4, §6 (Dr Rao's condition) |
| One tenant, one site, one jurisdiction keeps the first clock policy, signatory roster and source inventory small enough to reconcile by hand in shadow mode. | Board minute: "ship this to one customer and be certain" |
| It has no cross-tenant precedent dependency, so the pilot cannot repeat the August leakage path. | Brief §3 (August), §4 (counsel quote) |

Customer and person names are deliberately not reproduced in this public repository; the brief is confidential. The selection is identifiable to the reviewer from the row reference and the quoted constraints.

### Brief incidents and quotes mapped to design controls

| Brief detail | Requirement derived | Design control (document) |
|---|---|---|
| November: one customer's prompt change moved recommendations for 31 of 34 customers; destroy share rose from 11% to 19%; nine days to detect; USD 310k of product incinerated. | Any policy, rule or model change must be versioned, tenant-scoped and replayed against known cases before release. | Versioned policy bundles, per-tenant release manifests, Dr Rao's replay gate before every change ([versioning](06-versioning-and-deployment.md)). No model in the disposition path in the first release. |
| February: 1,912 alerts in 38 minutes left the queue unusable for 31 hours; four genuine cases from other customers missed their 72-hour window. | The regulatory clock must not depend on queue health, and one tenant's storm must not starve another's deadline. | Obligations created from alert time independently of the case; reserved regulatory workers; per-tenant fairness and incident grouping ([degradation](05-degradation-and-regulatory-clock.md)). |
| March: an inspector asked for the SOP in force, stability data, temperature series and approver for a disposition on a given date; only the outcome and approver existed. | Every signed disposition must pin the exact evidence versions it relied on and be retrievable for seven years. | Bitemporal evidence facts, frozen signed packets, hash-chained audit export; worked example in the [data model](03-data-model.md). |
| April: a firmware build under-reported by up to 1.8 °C; 214 closed cases affected, 61 re-adjudicated differently, nine carrier invoices withdrawn. | Telemetry provenance (device, firmware, calibration) must be evidence, and corrections must open new revisions, not rewrite history. | Firmware/calibration blockers in evidence analysis; reopen creates a new revision and preserves the prior one; compensating business actions via outbox ([lifecycle](04-case-lifecycle.md)). |
| June: a 30-day model sunset forced three weeks on an unqualified replacement. | No silent provider or version substitution; degraded mode must be explicit. | Model omitted rather than swapped when unqualified; version pinned per case revision ([degradation](05-degradation-and-regulatory-clock.md)). |
| August: a similar-case lookup put one customer's case into a direct competitor's draft; contract clause forbids derived artefacts crossing tenants. | No index, model or derived artefact built on one tenant's data may serve another. | `tenant_id` leads every key, index and export; cross-tenant precedent retrieval is a deliberate non-goal (below). |
| Regulatory windows: 72 hours in two markets, five days in Brazil, next business day for one US state programme; 14 late filings in two quarters, each stuck behind a flat-battery sensor. | Windows are per jurisdiction and programme, calendar-aware, and start at alert time. | Policy-driven obligation table and worked clock example ([degradation](05-degradation-and-regulatory-clock.md)). |
| CFO: USD 3,000/month model ceiling, 23 reviewers at about USD 1.5M/year, and the bill must be flat "on a quiet Sunday". | Cost must be predictable and bounded per tenant and per case, not usage-spiky. | Cost position and counterargument in [risks](09-risks-assumptions-and-open-questions.md). |
| Reviewer: "I spend my day looking things up"; 1,100-row private spreadsheet with no schema, backup or second owner. | Capture the reasoning, not just the outcome code; bring the spreadsheet's content under a schema inside tenant boundaries. | Structured review argument (rule, fact, citation, uncertainty, rationale) on every case ([lifecycle](04-case-lifecycle.md)). |

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

## Deliberate non-goals

The first release does not make disposition decisions, retrieve cross-tenant precedent, or use a general-purpose model to decide cases. It does not guess identities, synthesize missing measurements, infer universal deadlines, or treat an index match as proof of a source document's validity. These exclusions preserve human authority and prevent incomplete or ambiguous evidence from appearing conclusive; related assumptions and board counterarguments are in [risks and open questions](09-risks-assumptions-and-open-questions.md).

The prototype's actual feature boundary and production gaps are summarized in the [executive summary](00-executive-summary.md).

## Critical working component and current implementation

**Chosen critical component: the transactional evidence/lifecycle/clock kernel.** Its hardest invariant is that incomplete or changed evidence must never silently become an approved disposition, while an independent regulatory deadline continues through waits, retries and reopening. A dashboard would not establish that invariant; durable transactions, independent actors, packet versions and failure-path tests do. External evidence and filing dependencies are explicitly stubbed rather than represented as successful integrations.

The current source implements workbook snapshot import, tenant-scoped candidate analysis and blockers, a SQLite case/revision workflow, evidence review, independent signatures, optimistic versioning, idempotency, hash-chained audit export/verification, notification obligations, and an internal reminder outbox. A manually recorded receipt is explicitly human-attested, not delivery-confirmed. `tick` is an internal stub and does not file with or notify a regulator. The evidence analyzer reports candidates and blockers; it does not adjudicate.

The current code does **not** implement production identity or TLS, external document/source retrieval, an external notification or filing integration, independently verified receipt ingestion, multi-snapshot reconciliation, WORM retention, or automated decision recommendations. Public examples and tests must remain synthetic. Private workbook checks are opt-in through an explicit `SENTINEL_WORKBOOK` path and must not emit or commit raw data or reports.
