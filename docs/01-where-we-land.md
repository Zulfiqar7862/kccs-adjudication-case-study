# 1. Where we land

**Zulfiqar Ali Ahmed · Workcats take-home · 7 November 2026**

## The product is the right to sign

I would build an evidence service with a case workflow, not another disposition predictor. the senior reviewer found the likely answer in ten minutes; the next hundred minutes established that she could sign it (brief §2, pp.2–3). The inspector then exposed the absence of a retained argument, not the absence of a prediction (§3, p.3). The critical boundary is therefore between **assertions we can substantiate** and **facts we still need**. A named, authorised person remains responsible for a disposition.

The prototype makes that boundary executable. It resolves tenant-specific product references, retains every candidate SOP revision valid on the excursion date, detects several stability-index hazards, and emits a reproducible evidence-gap dossier. It also replays the separate notification clock. It does not pretend that an index is the underlying controlled document. All 420 records need additional evidence; that is a useful result, not a failed attempt to meet an automation quota.

## Requirements and attributes, with their source

| ID | Requirement / measurable acceptance | Why it exists |
|---|---|---|
| R1 | Tenant-scoped product/presentation, physical-site and legal-carrier identity; unresolved and disputed matches require steward approval. No global fuzzy merge. | §2 p.2 product and carrier examples; §7 pp.6–7; `07_Alias_Observations!B205:I208` explicitly distinguishes subsidiaries, CRT presentation and adjacent sites. |
| R2 | Resolve both origin and destination SOP, annexures and approved exceptions at excursion valid time and at a chosen recorded-time snapshot. More than one governing revision blocks automated closure. | §2 p.2; `10_Reviewer_Questions!B2:C2`; `05_SOP_Index!A202:L204` overlap. |
| R3 | Evidence includes correct presentation, bounded thermal exposure, prior batch exposure and measured/interpolated provenance. Unknown is not safe. | `10!B3:C3,B6:C9`; `00_README!B33:B37,B42:B44`; §3 April incident. |
| R4 | Preserve a signed argument: source bytes/hash, source page/cell, transformations, identity links, calculations, versions, dissent and approvers. Retrieve a historical bundle within one hour for seven years. Target p95 retrieval <10 minutes, quarterly restore drill. | §6 commitment 3 and §3 inspector; `10!B13:C13`. The p95 target and drill are proposed SLOs, not supplied facts. |
| R5 | Independent durable notification obligations from alert receipt. Waiting for lab, missing carrier CSV, model outage and reopening never pause/reset the original deadline. | §2 p.2; `00!B43,B46`; `13_Volume_And_Cost!B22:B23`; `09!E23` confuses the clocks. |
| R6 | Fair per-tenant queues, deadline-first regulatory lane, correlated incident view without bulk closure. Storm replay must leave every unrelated timer serviceable. | INC-2502 (`14!A3:F3`), 1,912 alerts / 38 minutes, four other tenants late. |
| R7 | Qualified automated non-actionable closure only; signed product dispositions remain human. Dual signatures and regional language policy are tenant configuration. | §6 the quality lead; `12_Tenant_Constraints!F2:K9` including the API-prohibited Indian tenant dual QA, its US competitor two-factor e-sign, the Portuguese-output tenant Portuguese. |
| R8 | Isolation covers source files, indexes, embeddings, prompts, cache, evaluation corpora, exports, logs and backups. EU/India data and processor routing obey tenant policy. | §4 p.5 Clause 22; INC-2512; `12!F2:G6,K6,F10:G10`. A tenant WHERE clause on a shared retrieval result is insufficient. |
| R9 | Every rules/reference/prompt/model change gets tenant-specific replay, discrepancy review, QA approval, immutable release manifest, canary and rollback. | §6 the quality lead; INC-2411 and INC-2509; `13!F33:F38` notice periods. |
| R10 | Recalibration performs dependency-driven impact search; append a new adjudication episode and compensate downstream claims, never rewrite the old signature. | `14!E4:F4`: 214 affected, 61 changed, nine withdrawn invoices. |
| R11 | Capture vendor evidence promptly; bounded retries, watermark/late-data handling, dead-letter repair, explicit missingness and source freshness. | `11_Systems_Inventory!D2:I10`: 30-day raw retention, 90-minute disorder, four-hour backfill, permanent BMS gaps, manual/fax dependencies. |
| R12 | Inference/retrieval stays below all three ceilings, including idle days; size storage/indexing separately. Every dashboard denominator states population and sampling. | CFO §4 p.4; `13!B25:B28,B37`; stratification `00!B28`. |

Short sheet numbers refer to the corresponding numbered workbook tab. All source sheets were reviewed; the public inventory is in the risks document. Proposed SLOs require sign-off; this submission has not demonstrated production compliance.

## Deliberate exclusions

No autonomous release, destruction, shortened-expiry calculation or claims invoice. No global precedent index or training on another tenant's history. No wholesale replacement of nine systems or telemetry transport in the first release. No LLM inference for the initial evidence kernel, no knowledge graph database, and no new visual case-management application: a reviewer workbench can be a thin view on existing Sentinel. PostgreSQL edges and an immutable object store are enough at this case volume. Do not migrate all 2,400 rules by translating them into a prompt; preserve the existing engine behind a feature flag while its closures are audited.

The prototype intentionally does **not** derive MKT, gap overlap, occupancy or cumulative exposure from aggregate temperatures and flags. The pack lacks raw series, batch IDs, per-pallet contents, room load intervals, equipment IDs, actual SOPs and documents. A convincing but unsupported answer would repeat the January pilot (§5 p.5).

## Rollout with six engineers

**First customer: the operator-managed-SOP tenant, one Indian site and a small signed-off product set.** Its SOPs are KCCS-managed (`12_Tenant_Constraints!J7`), Site QA signs (`H7`), and it has no residency clause in this extract (`F7`). That reduces the number of parties needed to correct source references. Hindi/Marathi and shared-terminal privacy remain release conditions, not details to postpone. Select the actual site only after source/occupancy audit; the pack does not justify picking one. the API-prohibited Indian tenant is a poor first customer: largest volume, India-only/no external APIs, dual signatures and four untagged BMS sites (`12!F3:K3`). the renewal-sensitive EU tenant is the second controlled cohort, in an EU-only cell: renewal risk is high, but it is not a reason to use its audit as our first production qualification.

| Relative time from design sign-off | Delivery and exit gate |
|---|---|
| Days 0–14 | Two engineers on source contracts/identity, two on case/clock, one on evidence/replay, one on test/security/release; QA, legal and tenant stewards are required partners, not assumed extra engineers. Agree calendar/reportability policy, source rights, first cohort, two-axis history and signatory matrix. Back up/curate the spreadsheet owner's spreadsheet with consent before January (§5). |
| Days 15–42 | Read-only ingestion, evidence snapshots, deadline dashboard and manual filing runbook. Shadow current closures and review a random, tenant-stratified auto-close population as well as the incident pack. Resolve cohort aliases/doc conflicts. |
| Days 43–70 | Replay disputed outcomes with QA; fault injection, tenant isolation and restore drills. Reviewer-assisted evidence bundles, translated outputs checked by local QA, real signature integration in non-production. |
| Days 71–90 | One-site the operator-managed-SOP tenant assisted live cohort; no new automatic product decisions. On-call, owner-approved notification channel and rollback exercised. Only independently evidenced non-actionable closures can graduate. |
| Months 4–6 | the renewal-sensitive EU tenant EU cell and a second Indian cohort after fresh qualification. Grow closure classes incrementally, not tenant forks. |
| Months 7–9 | Add remaining tenants in policy cohorts only after inventorying the 26 unlisted contracts; Brazil translation/pharmacist and US calendar/e-signature gates. Nine months is an aspiration conditional on evidence readiness. |

The 90 days are needed for source and QA qualification, not coding a form. Missing signed-off acceptance data, unknown jurisdiction or a failed isolation drill stops expansion. The board minute preferring one certain customer over thirty uncertain ones takes precedence over a date-only all-34 rollout.

## Where I push back on the board

1. **Under-24-hour signed disposition is not a universal safety target.** Median 6.2 days mixes queue delay with lab/third-party waits. `09!E23` says lab turnaround is nine days; notification can still occur on time. Keep the median as an observed business metric, but commit first to time-to-triage, evidence-ready-to-sign time, oldest-risk age and zero unowned notification obligations. Never release merely to improve a median.
2. **70% without a human is a conditional coverage goal, not a release gate.** Current approximate 82% × 78% = 63.96% reconciles the brief's 64%. Reaching 70% requires safe closure of 85.37% of non-actionable alerts, a 7.37-point gain in that conditional coverage; the unaudited closure population cannot establish safety (`00!B36`). Require a QA-agreed false-closure risk bound and an ongoing random audit. The 420 stratified records cannot certify that target.
3. **Zero late notification needs operational ownership and a fallback, not a promise of zero outages.** We can design no silent loss, persistent clocks and early escalation. A regulator endpoint can still fail. Track receipt-confirmed compliance separately from attempted submissions, and document external failures; do not mark a queued message notified.
4. **All 34 in nine months conflicts with the board's own certainty condition when contracts/data are unknown.** Only eight are individually described. Make cohort release conditional and keep the business date as a forecast.
5. **The budget is workable without always-on GPUs, but not with an idle GPU in every residency region.** One listed instance costs $5.67 × 730 ≈ $4,139.10/month before retrieval (`13!B37`). Start deterministic; constrained customers get no-model service. Detailed arithmetic is in the design. Do not silently treat the $3,000 model budget as storage/retention funding.

## Contradictions and positions taken

* **The flagship case is not a golden release.** §2 says a six-hour below-15°C allowance, then says cumulative shelf-life exposure. `02!K57` points at the cited study, which `06!B108:D108` describes as a vial accelerated study; `06!A105:H106` has pen-specific studies, one unreadable. The master says 72 hours cumulative (`02!J57`). Reject automatic adoption of the narrative outcome; obtain the approved pen study and governing annexure.
* **Alert receipt and excursion onset differ.** The narrative and extract do not provide the same chronology or reviewer identity. Apply `00_README!B43`: notification starts at receipt; reference validity uses excursion time. Preserve competing source assertions, not a fabricated reconciliation.
* **An unreadable study still has a limit-looking field.** `00!B42` warns there is no usable extracted outcome; `06!G8:H8` contains an illegibility note next to a six-hour allowance. Readability controls eligibility, not the presence of numbers.
* **Some human rationales are unsafe policy.** `09!E23` equates lab waiting with missing notification; `E21` uses inability to claim as a reason to destroy. Separate reporting, product fitness and liability. `E17` is a hypothesis about a cold excursion, not a validated calibration correction: the observed maximum is already inside the upper limit, while a lower-bound problem remains. Preserve dissent and ask for device-specific evidence.
* **Queue reconciliation is not universally valid.** Independent arithmetic finds two end-versus-disposition discrepancies exceeding a minute. Preserve both fields and exclude those records from unqualified timing analytics.


Date boundaries for controlled documents, legal calendar details, reportability criteria, actual signature authority and source correction dates are not provided. The demonstration uses half-open date intervals and UTC midnight for date-only metadata, explicitly provisional. Production requires QA/legal-approved site-local effective instants, business calendars, authorities and retention/hold policy before automation.
