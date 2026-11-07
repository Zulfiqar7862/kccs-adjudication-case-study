# Executive summary

**Zulfiqar Ali Ahmed — Workcats take-home**

The central problem is substantiating a regulated human decision, not producing a more confident prediction. Build a tenant-scoped evidence service, an independent regulatory-obligation lane and a signed, immutable historical basis. The design deliberately leaves pharmaceutical disposition with authorised people.

The hardest implemented component is the deterministic **evidence-eligibility and temporal-reference kernel**. It runs against the actual local workbook but refuses to treat indexes, ambiguous aliases or an overlapping SOP revision as permission to release product. The reference store can answer both “valid at the event” and “known at the decision”. Small executable workflow and hash-chain boundaries make waiting and reopening semantics testable without pretending to deploy the entire platform.

The local run processes 15 sheets and 420 events. Product resolution yields 297 exact-source matches, 72 unverified alias candidates and 51 missing. Fixed-hour historical replay identifies 14 late notification examples. All 420 cases still lack evidence needed for a defensible clinical disposition: zero automated product decisions or proposed closures are generated. These are stratified-pack counts, not population statistics.

Start with one Indian site/lane for the customer whose SOPs the operator manages (`12_Tenant_Constraints`, operator-managed row). Its controlled sources give the team a narrower first qualification. Make the renewal-sensitive EU customer the next cohort after an EU cell and audit retrieval are qualified. The first 90 days are for source readiness, QA shadow evaluation and on-call/manual fallback, not a quota of model-based closures.

Board goals for unconditional automation, universally fast signed outcomes and zero late notifications need safety conditions. Lab waits do not extend reporting deadlines; model outages must not stop the clock; a new model is not automatically an acceptable rollback. Every behavioral change requires reviewed differential replay.

This public repository is a fresh derivative: no source attachment, private workbook, contact details, compensation information, original history or real-case output is tracked. Tests use explicitly hand-made synthetic CSVs. Workbook-dependent tests skip without the user's own local copy. The private report is generated outside the repository. See the validation document for current measured evidence and honest limits.
