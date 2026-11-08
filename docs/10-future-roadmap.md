# Future roadmap and rollout

## Delivery and decision gates

- **Days 0–30 — define and prepare:** confirm the EU pilot boundary, approved source inventory and ownership, residency and access controls, SOP/study interpretation, signatories, notification policy and timezones, baseline denominators, retention/restore needs, and stop rules. Do not load live records until approval is documented.
- **Days 31–60 — shadow and reconcile:** compare synthetic or explicitly authorized pilot packets against independent human reconstructions. Measure source completeness, temporal selection, tenant isolation, audit export, missing-source handling, backlog, and clock calculations. Keep the tool advisory and non-dispositive.
- **Days 61–90 — go/no-go:** allow review-workspace use only after QA, security, data-governance, and operational acceptance of the prior gates. Otherwise extend shadow mode, narrow scope, or stop. Human disposition authority remains explicit.
- **Months 4–9 and beyond — conditional expansion:** evaluate each tenant and site independently for residency, data-use restrictions, provenance, tags, freshness, policy, signatories, recovery, and support. Do not infer that the first pilot authorizes a multi-tenant deployment.

## Phase intent

1. **Days 0–30 — define and approve:** establish the bounded pilot, data/source ownership, residency and access, approved policies/signatories, clock and retention semantics, baselines, operational owners, and stop criteria. Do not load live records before documented approval.
2. **Days 31–60 — shadow and reconcile:** compare authorized cases with independent human reconstructions; exercise source gaps, audit retrieval, isolation, backlog, and clock paths. Keep Sentinel advisory.
3. **Days 61–90 — go/no-go:** allow review-workspace use only if QA, security, governance, and operations accept the evidence. If gates fail, extend shadow mode, narrow scope, or stop. The milestone is a decision, not a production-readiness promise.
4. **Months 4–9+ — conditional expansion:** assess each additional tenant/site independently; no pilot approval automatically transfers.

This phased plan is contingent on implementation and qualification of the proposal in [versioning and deployment](06-versioning-and-deployment.md), and the open questions in [risks](09-risks-assumptions-and-open-questions.md).
