# 2. System architecture — HLD

## 2.1 HLD: a regional evidence plane, an independent clock lane

The architecture below is a **production proposal**, not a claim that these services have been deployed. The implemented surface is the local evidence kernel described in chapter 3.



Each residency cell contains ingestion, tenant-scoped evidence, case state, timers, retrieval and audit storage. The global control plane contains only deployment identities, policy versions, health counters and regional routing; no case payload, batch key, embedding or prompt crosses cells. Region is part of every storage, queue and encryption-key choice. EU means processing, logs, backups and model endpoints in the EU; India-only uses India endpoints only if the tenant allows them. APAC is not proof of India residency. the API-prohibited Indian tenant receives deterministic retrieval/templates and manual QA without an external model; self-hosting is a separately approved later option.

Use Python services with typed contracts; FastAPI for production HTTP, PostgreSQL 16+ for transactional/temporal data and pgvector only when needed; object storage with versioning/Object Lock; an at-least-once broker and durable workflow worker. Temporal can host long waits, but deadline facts stay in PostgreSQL and are independently swept. A six-person team should start with a modular case/evidence application and separate connector/clock workers, not a microservice per table. The clock lane is a real deployment/resource boundary because the February queue incident proves shared fate is dangerous. An optional LLM adapter is another separate, permissioned boundary because it is unavailable or prohibited for some tenants.

### Components, ownership and crossings

| Boundary | Owns | Interface and why separate |
|---|---|---|
| Source adapters | Vendor cursors, rate limits, raw envelopes, source sequence/arrival time, schema errors | Emits immutable evidence envelopes. Adapters absorb nine incompatible systems without leaking source quirks into adjudication. |
| Identity and reference registry | Tenant product/presentation versions; site/room/equipment mappings; legal entities; alias proposals and approvals; controlled rule facts | Returns candidates plus provenance for `(tenant, ref, valid_at, known_at)`. Human stewardship, not retrieval score, settles conflicting identity. |
| Evidence compiler / kernel | Dependency graph, evidence completeness, typed arithmetic, verified citations and manifest | Produces a dossier with facts, uncertainty and blockers. Pure evaluation is replayable; no network or filing side effects. |
| Case workflow / reviewer workbench | Case episodes, wait reasons, assignments, manual tasks, signatory matrix and decision snapshots | Commands require expected case version and idempotency key. Coordinates work; cannot edit source truth or stop the clock. |
| Notification obligations worker | Reportability-review task, jurisdiction policy, due instant, escalation schedule, filing attempts and confirmed receipt | Durable deadline-first queue independent of disposition or model. Regulatory Affairs owns unresolved obligations. |
| Retrieval and optional language service | Tenant-specific evidence/precedent search, approved translations, constrained drafting | Receives only eligible source excerpts; returns claim-to-citation mapping. Cannot set state or write a disposition. |
| Audit/export | WORM snapshots, signature binding, export jobs, retention/legal holds and verification | Exports byte-identical signed basis without a live source system or re-calling a model. |
| Commercial investigation | Carrier causation, contract/amendment review, claims deadlines and accounting compensations | References clinical decision but cannot decide product fitness. Separate failure and approval domain. |

### Source-specific ingestion

* SYS-01 REST: poll within 300 requests/min, incremental cursor, cache unchanged results; retain 5-minute buckets as buckets, never label them raw. Acquire available raw before 30 days; the seven-year basis cannot depend on the vendor's retention. Four-hour reconnect backfill generates a new evidence version.
* SYS-02 MQTT: at least once, 90-minute disorder; transport dedup key includes tenant, device, vendor message identity and payload hash. A reused ID with changed payload is a conflict, not a duplicate to drop. Event-time windows carry watermark/completeness. A late reading can invalidate a recommendation or reopen a signed episode.
* SYS-03 BMS: permanent gaps, no tenant tag, availability 97.8% (`11!G4:I4`). Land restricted raw room events in a cell-local quarantine domain. Resolve time-bounded room occupancy from TMS before fan-out into tenant evidence. Never broadcast a shared room's tenant list. Unmapped is a manual task, not “no product loaded”.
* SYS-04 TMS CDC: capture LSN/version, deletes and leg/equipment changes; join occupancy at event time rather than current location. ERP SFTP: checksum, source date, complete-file marker, late-file alerts and schema validation; stale feeds never silently become current.
* SharePoint/Box/manual/fax: controlled manual intake, malware scan, OCR as an untrusted transcription, document hash and page bounding boxes, two-person QA approval of numeric rules and handwritten exceptions. There is no SharePoint API assumed by the pack. the controlled-SOP repository REST obeys 60 req/min; prefetch governed revisions, do not perform seven systems' lookups synchronously while a reviewer waits.

No external text can instruct the compiler to change policy or invoke a tool. An LLM sees inert quoted evidence and has no execution credentials. Numerical limits and citations are checked against approved structured facts, not the draft prose.

## 2.2 Capacity, availability and economics

At 10M readings/day, average ingestion is ~116 readings/s. Case volume is only 11,400 alerts/month, ~380/day, and ~2,050 adjudications/month (`13!B3:B8`). These are different scaling domains. Store telemetry in time-partitioned object files plus searchable metadata; do not put every reading into a graph database. Use a 10× sustained telemetry sizing assumption initially and load-test it, then measure actual peak rate: the supplied BMS burst is an alert burst, not a raw-reading throughput measurement. The 1,912/38-minute burst is ~0.84 alerts/s; the failure was queue fairness, not inherently extraordinary compute load.

Proposed SLOs: durable accepted-alert recording p99 <60s; timer sweep every minute; deadline escalation page within 5 minutes; cell-local case API 99.9%; audit export p95 <10 min and every validated request <1 h. Targets require operational validation. PostgreSQL synchronous multi-AZ protects accepted obligations (target RPO 0 within that failure domain); region disaster RPO ≤5 min/RTO ≤1 h is a planning target, not achieved evidence. Backups/DR remain within contractual geography. A low-RPO outbox stream and a separate obligation ledger backup support manual notification during regional recovery.

**Retention sizing assumptions**, deliberately not presented as measured compression: 80 bytes/reading × 10M × 365 × 7 = 2.044 TB logical; three copies ≈6.13 TB. JSON overhead, index sizes, encryption metadata, leap days and compression are excluded; benchmark Parquet compression and vendor raw payloads before procurement. A 20MB evidence bundle × 2,050 × 12 × 7 ≈3.44TB; three copies ≈10.33TB. Documents ~16,596 indexed repository PDFs (11,040 stability + 4,312 SOP + 1,244 contracts); at an assumed 2MB each, ~33GB before versions/OCR. Retain the **complete relied-on series and source bytes** for seven years, with legal holds and immutability; general telemetry retention beyond that subset needs a separate agreed policy. These are sizing scenarios, not a mandate to retain all unrelated telemetry seven years.

**Budget arithmetic** (`13!B25:B28`, prices `B33:C38`):

| Gate | Monthly maximum / scenario |
|---|---|
| Per screened alert | $0.06 × 11,400 = $684 |
| Per human case | $1.10 × 2,050 = $2,255 |
| Sum of both maxima | $2,939; this fits CFO's $3,000, leaving $61, but only if the two ceilings are additive. Seek explicit finance confirmation. |
| Proposed baseline screening | No model; retrieval allowance assumed $0.002/alert = $22.80 |
| Two small-model drafts per case | Each 18k input + 2k output tokens: $0.0144 + $0.008 = $0.0224/call; two × 2,050 = $91.84 |
| Human-case retrieval allowance | Assumed $0.02/case = $41 |
| Large-model fallback for 20% | One 40k/4k call costs $0.18; 410 calls = $73.80 |
| Total scenario | $229.44/month, ~7.65% of the $3,000 cap; not a measured provider invoice. All cases are costed as API-eligible, so prohibitions can only reduce calls. |

Enforce counters before each call, input/output token limits, at most two baseline drafts plus one escalation call per case, tenant daily and platform monthly budgets, and no unbounded agent loops. Retrieval is separately metered; cap hard cases at $1.10 including retrieval, not just on average. Larger context or repeated human regeneration consumes a token reservation and can fall back to deterministic templates. Provider A small is the starting procurement option where permitted: regional endpoints, zero retention and 12-month notice; exact India location/processor terms still need confirmation. Provider B's lower price does not compensate for US-only/no zero-retention/30-day sunset. No embedding endpoint is used for prohibited tenants; SQL/lexical retrieval works without one.

One always-on listed GPU: $5.67 × 730 = $4,139.10/month; two regions $8,278.20, before retrieval and idle redundancy. Sunday costs persist. Scheduled GPU inference may later be batch-qualified, but is not a free always-ready alternative. Storage, ingestion and indexing are a separate capital line (`13!B27`); provision and price them explicitly rather than burying them in the cheap model figure.



See [architecture](../diagrams/architecture.md) and [data flow](../diagrams/data-flow.md).

The implementation remains a modular local application. Every requested Python boundary has real behavior; deployment boundaries described here are proposed, not operational infrastructure.
