# System architecture

This document separates the **implemented local prototype** from the **proposed production design**. Production topology is not implemented or deployment-qualified.

## Implemented prototype components

### Component overview

```text
XLSX snapshot ──> workbook ──> evidence analysis ──> SQLite service
                                             │          ├─ cases and revisions
CLI ─────────────────────────────────────────┘          ├─ audit and idempotency
Loopback HTTP API ──────────────────────────────────────┤
                                                        └─ notification obligations/outbox
```

- `prototype/src/sentinel/ingestion/workbook.py` uses the standard-library ZIP support for XLSX containers and `defusedxml` for XML parsing; it returns row dictionaries, retains source row numbers, and computes a file SHA-256 digest.
- `prototype/src/sentinel/evidence/analysis.py` normalizes timestamps to UTC, selects tenant-scoped SOP index candidates by effective date, and returns candidate rows and blockers. Index rows are not authoritative evidence or a disposition.
- `prototype/src/sentinel/workflow/service.py` owns the SQLite-backed import, case workflow, command validation, audit trail, notifications, and export verification.
- `prototype/src/sentinel/api/http.py` provides a loopback-only JSON adapter over the service. Its bearer identities are a local prototype stub.
- `prototype/src/sentinel/cli.py` and `prototype/src/sentinel/demo.py` provide the root CLI and fictional end-to-end workflow.

## Scope of the production proposal

The implemented prototype is described above; the following sections specify the wider system proposed for a gated rollout, not implemented functionality. Policy values are proposed engineering defaults unless identified as workbook facts; QA/legal must approve regulatory semantics.

## Deployment and component boundaries

Deploy a regional cell for each authorized residency boundary, initially an EU pilot cell. Keep tenant keys, queues, blobs, indexes, backups, logs and processing inside the required region. A shared control plane may distribute code/package hashes and non-sensitive health totals only, never evidence, embeddings, prompts or case identifiers. The tenant requiring exclusive derived artifacts gets a tenant-exclusive data/derived-artifact boundary. India-only and EU-only are enforced by egress/network/storage policy, not a request flag.

[Production architecture diagram](../diagrams/01-production-architecture.md).

Start with a modular service and separately deployed ingestion and deadline workers, not a microservice per table. A relational transaction covers case version, approval event, batch reservation and outbox intent; distribute only at real trust, scaling or fault boundaries. The deadline worker has its own connection pool, reserved workers and queue so evidence extraction, a model outage or alert storms cannot starve notification work. Source object storage is separate because retention and large immutable bytes differ from transactional queries. Signature and filing integrations remain separately qualified authorities.

## Source adapters, identity and ordering

Tab `11_Systems_Inventory` defines the initial adapter contracts:

| Source | Integration and required behavior |
|---|---|
| Telemetry provider A SYS-01 | REST poll below the 300 req/min hard limit; tenant/cursor checkpoints, overlapping fetch window and dedupe; up to four hours of reconnect backfill. Persist source bytes before acknowledging ingestion. |
| Gateway provider B SYS-02 | MQTT at-least-once push; dedupe by source event ID, retain out-of-order samples up to the documented 90 minutes and accept later corrections as new evidence, not overwritten samples. |
| Building monitoring SYS-03 | OPC-UA → Kafka; gaps have no backfill. Persist gap evidence. Missing tenant tags go to a restricted quarantine with human assignment; never route by a fuzzy facility-name guess. |
| Transport management SYS-04 | Debezium CDC; transaction/order cursor, shipment/leg associations and correction events. |
| Tenant ERP SYS-05 | SFTP batches with per-file digest, manifest and atomic publication; late files occur 3–6 times/month. Keep event-time and receipt-time distinct. |
| Stability SYS-06 | No API in the inventory. Controlled, tenant-approved document export with manifest and QA ownership attestation; no invented SharePoint API access. OCR is an extraction proposal, not evidence approval. |
| SOP SYS-07 | Controlled document library REST below 60 req/min; fetch exact revision and annexes, not just latest; retain original and rendition with hashes. |
| Contracts SYS-08 | Controlled Box/shared-drive export plus legal-entity, amendment and temporal review; names of a parent/subsidiary cannot substitute for contractual counterparty. |
| Carrier SYS-09 | Source-specific REST/EDI adapters and controlled CSV/email/fax manual intake; preserve sender, attachment and translation provenance. Unsupported formats create human work, not a silent success. |

Canonical envelope: `tenant_id, source_system, source_event_id, source_revision, event_time_utc, observed_at_utc, ingested_at_utc, schema_version, source_uri, source_sha256, correlation_id, payload`. Unique inbox key is `(tenant, source, event_id, source_revision)`; a same-key/different-hash conflict is quarantined. Store cursor and inbox commit atomically. Producer retry is normal. Never use hash equality of temperature/duration alone to conclude that two physical excursions are duplicates.

Maintain governed `entity_alias(tenant, entity_kind, alias, canonical_id, valid interval, recorded interval, confirmer, evidence_id)`. Exact alias resolution can return zero, one or many candidates. Zero/many require review. Facility identity, site timezone, product presentation and carrier legal entity are distinct domains; do not collapse them into a global name map. The ad hoc alias workbook is a source of proposals, not authority. Route incidents to parent groups for operational triage, but retain each child's case, product context and regulatory obligation.

## Prototype integration contract

The local API contract, route and role behavior, and workbook shape are documented in [API and data contract](API.md). Security boundaries and local-only limitations are in [Security](SECURITY.md); deployment and development commands are in [Contributing](CONTRIBUTING.md).
