# Risks, assumptions, and open questions

## Six board commitments: qualify before accepting as guarantees

| Commitment in the brief | Recommendation |
|---|---|
| Median alert-to-signed-disposition under 24 hours by the end of the first full quarter after go-live | Treat as a monitored target, not a promise. Define eligible-case population, pause rules, baseline, and safety guardrails; the source-pack median is 6.2 days. Do not rush decisions or waive evidence to meet a clock. |
| At least 70% of alerts closed without human review | Do not optimize this quota before validating the denominator, false closures, and source quality. The pack reports about 64% current rules-engine closures while also describing an approximately 82% non-actionable alert share; those are not interchangeable, validated rates. No automated disposition is in scope. |
| Full decision basis produced within one hour for seven years | A useful requirement, but it needs tested retrieval, backup/restore, access control, and an approved retention regime. The local hash chain is not WORM storage, and the prototype does not establish either the one-hour service level or seven-year retention. |
| Stay within the cost ceiling | The modeled inference/retrieval allowance is **$2,939/month** against a **$3,000/month** ceiling, leaving **$61/month** before omitted ingestion, storage, indexing, retention, and operations. One always-on self-hosted instance is modeled at **$4,082.40/month**, above that ceiling before other costs. These scopes are not equivalent to a complete production budget. |
| No notifiable deviation reported outside its applicable window | Zero late notifications is an outcome to measure and govern, not a software guarantee. First approve policy and clock inputs, then test backlog, outage, escalation, delivery evidence, and manual fallback. The reminder stub does not deliver a filing. |
| First customer live within 90 days; all 34 within nine months | Use day 90 as a go/no-go for one bounded EU pilot, not a promise of production readiness. The 34-tenant target requires individual residency, data-use, source, signatory, and operating-control review. Broader onboarding in months 4–9 or later remains conditional. |

All six commitments should have named owners, definitions, and stop criteria before they become acceptance gates. A target is not evidence that it can be met safely.

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
| Closure coverage versus non-actionable prevalence (brief sections 5–6; `13_Volume_And_Cost`) | The brief describes closure of about 78% of non-actionable alerts, with non-actionable alerts about 82% of all alerts: 0.78 × 0.82 ≈ 64% of all alerts. The 64% closure share and 82% prevalence share therefore use the same overall population, not different denominators. These aggregates do not establish false-safe-closure accuracy or savings; validate outcomes independently. |
| Seven-year auditability without a specified retention start, legal-hold or deletion policy (brief board requirements) | Archive immutable source/version evidence in the production design; QA/legal must approve retention semantics. Local hashes are not sufficient. |
| A fixed onboarding schedule without validated connector readiness or full operating costs (brief; `11_Systems_Inventory`, `13_Volume_And_Cost`) | Treat dates as conditional gates. Confirm source access, total cost and recovery staffing before widening the pilot. |

## Material prototype/production boundary

The prototype accepts one immutable snapshot per database, uses one snapshot observation time plus limited SOP effective-date selection rather than full bitemporal history, and relies on local identity/signature stubs. Production readiness additionally depends on source-owner agreements, qualified signatories, retention/legal-hold policy, recovery objectives and tested restore, total operating costs, and legally approved clock/receipt semantics. See [data model](03-data-model.md), [degradation](05-degradation-and-regulatory-clock.md), and [deployment](06-versioning-and-deployment.md).
