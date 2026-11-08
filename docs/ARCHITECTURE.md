# Architecture

Sentinel is a local, evidence-first case workflow prototype. It analyzes imported indexes and records workflow actions; it does not make an adjudication or independently validate source documents.

## Components

```text
XLSX snapshot ──> workbook ──> evidence analysis ──> SQLite service
                                             │          ├─ cases and revisions
CLI ─────────────────────────────────────────┘          ├─ audit and idempotency
Loopback HTTP API ──────────────────────────────────────┤
                                                        └─ notification obligations/outbox
```

- `src/sentinel/workbook.py` uses the standard-library ZIP support for XLSX containers and `defusedxml` for XML parsing; it returns row dictionaries, retains source row numbers, and computes a file SHA-256 digest.
- `src/sentinel/evidence.py` normalizes timestamps to UTC, selects tenant-scoped SOP index candidates by effective date, and returns candidate rows and blockers. Index rows are not authoritative evidence or a disposition.
- `src/sentinel/service.py` owns the SQLite-backed import, case workflow, command validation, audit trail, notifications, and export verification.
- `src/sentinel/http.py` provides a loopback-only JSON adapter over the service. Its bearer identities are a local prototype stub.
- `src/sentinel/__main__.py` exposes local CLI operations; `src/sentinel/demo.py` exercises a fictional end-to-end workflow.

## Import and time semantics

An import is a workbook snapshot. Its digest makes an identical re-import replayable; a different snapshot is rejected when one is already stored, rather than silently replacing it. The import records an observation timestamp in `tables['_observed_at']`. SOP lookup can accept `known_at`: when that requested knowledge time predates the imported snapshot's observation time, the snapshot cannot support that lookup. Effective-date selection and this observation-time check are distinct. The product index is a historical snapshot and does not provide bitemporal product validity.

## Case lifecycle and concurrency

```text
import → waiting for evidence → record evidence → review → sign
                                                    ↑       │
                                                    └ reopen┘
```

Evidence analysis begins with candidates and blockers, not a decision. A reviewer records evidence and resolves every blocker before review; the review also requires references across SOP, stability, telemetry, identity, batch, and contract categories. Signing requires an allowed disposition and an independent signer; the reviewer cannot sign their own packet. A signed case must be explicitly reopened before evidence changes. Every mutation uses an expected integer case version and an idempotency key: stale versions and conflicting key reuse are rejected, while an identical retry can return its prior result.

The optional dual-approval rule is currently a local heuristic: service code searches the tenant's `who_signs_a_disposition` text for the word `dual` using a case-insensitive regular expression. When matched, both `site_qa` and `corporate_qa` signatures are required. This text match is not a policy engine and is not suitable as a production authorization control.

## Notification and audit boundaries

The notification obligation is created from the original alert data independently of later case review or signature. Its deadline is derived from the alert time and configured reporting window. A recorded receipt is a separate human attestation; it is not created by reminder processing and is not independently verified. The `tick` command processes an internal reminder/outbox stub only. It does not send a regulatory filing or establish that an external recipient received anything.

Audit records are hash-chained and can be exported and checked for chain consistency. This is tamper-evidence within the local application, not WORM storage, a qualified electronic signature, or proof that recorded facts are true.

## Production boundary

The supported implementation is a local prototype: SQLite, static locally generated bearer identities, and loopback HTTP. It does not include production identity management, TLS termination, external notification or filing integrations, verified receipt ingestion, durable distributed storage, or validated document interpretation. Deploying it outside its intended local environment requires those controls to be designed and implemented separately; the prototype is not a substitute for them.
