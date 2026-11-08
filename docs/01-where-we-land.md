# Where we land

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

## Deliberate non-goals

The first release does not make disposition decisions, retrieve cross-tenant precedent, or use a general-purpose model to decide cases. It does not guess identities, synthesize missing measurements, infer universal deadlines, or treat an index match as proof of a source document's validity. These exclusions preserve human authority and prevent incomplete or ambiguous evidence from appearing conclusive; related assumptions and board counterarguments are in [risks and open questions](09-risks-assumptions-and-open-questions.md).

The prototype's actual feature boundary and production gaps are summarized in the [executive summary](00-executive-summary.md).

## Critical working component and current implementation

**Chosen critical component: the transactional evidence/lifecycle/clock kernel.** Its hardest invariant is that incomplete or changed evidence must never silently become an approved disposition, while an independent regulatory deadline continues through waits, retries and reopening. A dashboard would not establish that invariant; durable transactions, independent actors, packet versions and failure-path tests do. External evidence and filing dependencies are explicitly stubbed rather than represented as successful integrations.

The current source implements workbook snapshot import, tenant-scoped candidate analysis and blockers, a SQLite case/revision workflow, evidence review, independent signatures, optimistic versioning, idempotency, hash-chained audit export/verification, notification obligations, and an internal reminder outbox. A manually recorded receipt is explicitly human-attested, not delivery-confirmed. `tick` is an internal stub and does not file with or notify a regulator. The evidence analyzer reports candidates and blockers; it does not adjudicate.

The current code does **not** implement production identity or TLS, external document/source retrieval, an external notification or filing integration, independently verified receipt ingestion, multi-snapshot reconciliation, WORM retention, or automated decision recommendations. Public examples and tests must remain synthetic. Private workbook checks are opt-in through an explicit `SENTINEL_WORKBOOK` path and must not emit or commit raw data or reports.
