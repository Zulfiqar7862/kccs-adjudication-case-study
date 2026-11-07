# 5. Degradation and the regulatory clock

## 2.5 Failure, degradation and the regulatory clock

| Failure | Product/case behaviour | Regulatory behaviour |
|---|---|---|
| Model / embedding API unavailable or forbidden | Deterministic dossier + approved templates, lexical lookup and manual QA. No unqualified alternate model. | Continues independently; an LLM is not in this lane. |
| SOP/stability source unavailable | Use already captured approved bytes only when required version/freshness is defensible; otherwise WAITING/manual escalation, not current-document substitution. | Deadline continues; file initial deviation with known facts and permitted follow-up, under Regulatory Affairs policy. |
| Telemetry source gap | Mark incomplete; bounded retries/watermark; BMS permanent gaps require alternate evidence/manual assessment. Never fabricate samples. | Alert-based clock unchanged; outage is not an extension. |
| TMS/occupancy unavailable | No BMS auto-close; hold affected evidence compilation. Isolate tenant work queues. | Unresolved-reportability escalation continues. |
| Broker/workflow worker down | PostgreSQL outbox survives; retry/backoff with jitter; leases expire. Independent sweeper reconstructs missed timer work. | DB ledger is authoritative; independent health alarm on oldest unresolved deadline/sweeper heartbeat. |
| Case database unavailable | API cannot acknowledge durable intake or accept signatures. Adapters buffer encrypted raw envelopes/cursors; operational outage route captures alert receipt independently where supported. | Page immediately; RA uses last replicated ledger and approved emergency register/filing process; reconcile receipts on recovery. Do not claim zero loss if both intake and emergency capture fail. |
| Regulator endpoint/email unavailable | Filing stays SUBMITTING/FAILED, not CONFIRMED; attach failed attempt evidence. | Retry by idempotency key, page RA before slack expires; approved alternate filing channel, human receipt verification. Clock never pauses. |
| Region outage | Fail within allowed geography only. EU data never fails over to US for convenience. | Execute regional recovery + emergency RA runbook, preserve original due instants, disclose any missed duty. |
| WORM store unavailable | Do not commit a signed final decision without its durable frozen bundle. Raw landing buffer retries. | Notification may proceed through emergency channel without a final disposition; record and later reconcile its receipt. |

Backpressure reserves notification capacity and per-tenant worker quotas. A tenant's storm cannot consume every worker, model budget or signer queue. Dead-letter queues have an owner, oldest age alarm and replay tool; they are not a place where an obligation silently expires. “Notification attempted”, “received by regulator” and “signed disposition” are different metrics.



## What the local clock proves

`temporal/clock.py` is a pure arithmetic replay of historical flags. It never determines jurisdiction or reportability independently. Missing reportability is UNKNOWN_REPORTABILITY; missing windows are UNKNOWN_WINDOW. Every result has calendar qualification false. A pending notification remains pending regardless of case waits or disposition time. No notification is sent.

See [degradation modes](../diagrams/degradation-modes.md).
