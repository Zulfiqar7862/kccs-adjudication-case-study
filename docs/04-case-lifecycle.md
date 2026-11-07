# 4. Case lifecycle

## 2.4 Case lifecycle, timers and concurrency



| From → To | Guard / durable effect |
|---|---|
| RECEIVED → TRIAGE | Persist raw alert, create unresolved-reportability task and provisional earliest deadline in the **same transaction**, enqueue via outbox. |
| TRIAGE → CLOSED_NON_ACTIONABLE | Qualified rule, complete supporting evidence (e.g. signed no-occupancy interval), no unresolved reporting duty, tenant permits this closure class; preserve closure basis. A dock flag alone never qualifies. |
| TRIAGE → GATHERING | Allocate case/episode, capture dependencies and named case owner. |
| GATHERING → WAITING | Store wait type (lab, SOP steward, telemetry, carrier, signatory), requested item, owner, request time and wake condition. Do not consume a worker while asleep. |
| WAITING → GATHERING | Correlated evidence arrival, owner action or wait-expiry reminder. Check expected version; duplicate callbacks are harmless. |
| GATHERING → REVIEW_READY | All required fact checks satisfied, unresolved contradictions shown; compiler returns a versioned dossier. Missing evidence can instead be escalated to senior QA for an explicitly reasoned manual decision within tenant policy. |
| REVIEW_READY → SIGNING | QA selects disposition/pallet scope/rationale and freezes decision hash. |
| SIGNING → DISPOSED | Correct authorised signature(s), two distinct principals where dual QA required; any evidence change invalidates pending signatures and returns to GATHERING. |
| DISPOSED / CLOSED_NON_ACTIONABLE → REOPENED → GATHERING | Bulletin, complaint or new evidence creates a new episode; preserve original outcome, signatures, notification obligation and downstream effects. |

The notification submachine is parallel: `UNASSESSED → REQUIRED → DRAFTED → SUBMITTING → CONFIRMED`; failures remain required with retry/escalation. `NOT_REQUIRED` requires a versioned human/qualified policy basis. If policy is unknown, retain a provisional earliest possible duty and escalate to Regulatory Affairs immediately; do not invent the governing jurisdiction from tenant country alone. One case may have multiple jurisdictional obligations, including origin/destination/market rules; each must be satisfied. Reopening triggers an assessment of amendment/new-report duties without resetting the original obligation.

Timer facts live outside a FIFO review queue. A minute sweeper selects open duties by `due_at` with row leases (`FOR UPDATE SKIP LOCKED`), tenant concurrency limits and per-duty idempotent escalation markers. Proposed reminder policy: at creation, half-window, 12h/4h/1h remaining where applicable, and after breach; short next-business-day duties use appropriate earlier checkpoints. Page based on slack including channel latency, not simply elapsed percentage. Business-day rules require jurisdiction timezone, holidays, cutoff and definition of “next business day”; `reg_window_hours=24` is a historical surrogate and must not drive production US deadlines. India 15-day duties apply only to notifiable products; Brazil five **calendar** days must be legally mapped to an exact instant/cutoff, not assumed to mean local close of business. Fixed-hour replay in this prototype cannot qualify those legal meanings.

Case command transactions use expected aggregate version. Outbox `(tenant,event_id)` uniqueness prevents duplicate state changes; message consumers store inbox keys atomically with state. Ingestion keeps both `observed_at` and `received_at`; sensor backfill never moves `alert_received_at` later. Physical-event dedup requires corroborated shipment/logger/time-overlap, not “same shipment”. Incident correlation groups work for review; it never erases an individual consignment's occupancy risk. Batch exposure updates are locked/versioned; two concurrent events cannot both spend the same remaining allowance.



### Reopen six months later

A calibration notice identifies firmware/device/time-window dependencies. Search manifests and exposure edges, create review tasks for every impacted decision (including auto-closed cases), prioritise current stock and deadlines, and notify the case owner. Original bundle remains available; create episode N+1 with both old/new evidence and a structured difference. Ask Regulatory Affairs whether amendment is required and accounting whether a claim/invoice needs reversal. Those are compensating commands with their own approvals/idempotency keys; never delete an invoice or overwrite a signature. A reopened case is not proof that the old decision was wrong; impact assessment records unchanged as well as changed results.



## Executable scope

The in-memory workflow supports owned waits, expected-version guards, reviewed-basis guards, preserved prior decisions and appended reopen episodes. The original due instant is unchanged. These operations are tested on synthetic cases and optionally replayed over historical reopen flags. They do not integrate an identity provider, persist workflow aggregates or validate actual e-signatures. A hash argument in the demonstration is not a regulated signature. The workbook pipeline never calls its disposition transitions.

See [state diagram](../diagrams/case-lifecycle.md).
