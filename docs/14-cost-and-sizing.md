# Cost and sizing

All price and volume inputs are taken from tab 13 of the reference data pack (procurement price list dated 2026-09-01). Everything else is labelled **assumption** and is an estimate, not a measurement. Tenants are referred to by code only.

## 1. Inputs (verbatim from tab 13)

| Input | Value |
|---|---|
| Volumes | 128,000 consignments/month; 10M sensor readings/day; 11,400 alerts/month (82% non-actionable); 2,050 human-adjudicated cases/month |
| Largest burst | 1,912 alerts in 38 minutes (INC-2502) |
| Ceilings | USD 1.10 per case reaching a human reviewer; USD 0.06 per alert screened. "Covers inference and retrieval only; ingestion, storage, indexing, and seven-year retention are separate." |
| Provider A large | USD 3.00 in / 15.00 out per 1M tokens |
| Provider A small | USD 0.80 / 4.00 |
| Provider B large | USD 2.50 / 10.00, **US only**, no zero retention, 30-day notice |
| Provider C mid | USD 1.10 / 4.40, US and EU |
| Self-hosted | g5.12xlarge, USD 5.67 per instance-hour |
| Embeddings | USD 0.02 per 1M tokens |
| Reviewers | 23 (14 India, 6 EU, 3 US); median 96 active minutes per case; 7 systems opened per case; loaded rates India 18 / EU 61 / US 74 USD per hour; annual QA cost USD 1.51M |
| Condemned product | USD 19.4M across about 2,700 destroy decisions in FY25-26; audit estimates 32% was salvageable |

## 2. What the ceiling actually is (and a correction to doc 09)

The CFO's quote (brief section 4) states USD 3,000/month for model spend. The pack gives two per-unit ceilings instead:

- Per reviewed case: 1.10 x 2,050 = **USD 2,255**
- Per screened alert: 0.06 x 11,400 = **USD 684**
- Sum: 2,255 + 684 = **USD 2,939**

**Ambiguity:** the two ceilings could be additive (2,939) or could overlap with the 3,000 figure (e.g. screening spend is part of the same pool). **Position taken:** treat USD 2,939 as the binding monthly figure, because it is derived from the pack's unit ceilings and volumes, and treat USD 3,000 as the rounded envelope above it (USD 61 of unallocated margin). Both are shown in the final table. Any design that fits 2,939 fits 3,000.

**Reproduction check of doc 09 / doc 01 numbers:**

| Number in repo | Recomputed | Reproduces? | Note |
|---|---|---|---|
| USD 2,939/month | 2,255 + 684 = 2,939 | Yes | But it is the **sum of the ceilings**, not a modelled spend. Doc 09 now describes it as the sum of per-unit ceilings; an earlier draft had called it modelled spend. |
| USD 4,082.40 self-hosted | 5.67 x 720 h = 4,082.40 | Only with a 720-hour (30-day) month | At 730 h (average month, 8,760/12): 5.67 x 730 = **USD 4,139.10**. Difference USD 56.70. Doc 09 should state the hour basis; this doc uses 4,139.10. |

## 3. Routes

| Route | Description | Inference cost |
|---|---|---|
| **R0** | No-LLM evidence assembly. Deterministic resolution of product, facility, carrier, SOP, stability and telemetry evidence, with conflicts and missing inputs listed (what the prototype does). | **USD 0** |
| **R1** | Screening narrative for auto-closed alerts | Not adopted (see 3.1) |
| **R2** | Reviewer-aid narrative per human-reviewed case, rendered from the assessment JSON | Section 3.2 |

R0 is a supported, qualified route, not a fallback of last resort. The kernel's value is deterministic evidence resolution; it makes no disposition (the assessment's disposition is always `ABSTAIN`). T-VIRENT (India-only, no external APIs) and the six unlisted tenants that prohibit external APIs cannot use hosted models anyway, so R0 must be fully functional on its own. Nothing in the decision path depends on R1 or R2.

### 3.1 R1: screening narrative for auto-closed alerts

Not needed. Closure is rules-based and its audit evidence is the rule version plus inputs; a free-text narrative per benign alert adds no evidence, adds a non-deterministic artefact to retain for seven years, and adds a leak surface. Screening cost is therefore **embeddings only, or zero**.

- Optional embedding of alert text for grouping/precedent (**assumption**: 500 tokens/alert): 11,400 x 500 = 5.7M tokens x 0.02 = **USD 0.114/month** (USD 0.00001 per alert vs the 0.06 ceiling).
- For completeness, if R1 were wanted (**assumption**: 1,500 in / 300 out, x1.15 retries): Provider A large 0.0090 x 1.15 = 0.01035 per alert, x 11,400 = USD 118; A small USD 31.46. It would fit the ceiling, so the argument against R1 is value and risk, not price.

### 3.2 R2: reviewer-aid narrative, per case

**Assumptions:** input 6,000 tokens (assessment JSON plus selected evidence excerpts); output 800 tokens; retry factor 1.15; evaluation overhead = monthly replay of 10% of cases (205) + a full replay before each release (**assumption**: 2 releases/month x 500-case golden set = 1,000 runs).

Formulas:

- base per case = (6,000 x P_in + 800 x P_out) / 1,000,000
- with retries = base x 1.15
- monthly runs = (2,050 + 205 + 1,000) x 1.15 = 3,743.25 (1.826x the production case count)
- monthly cost = base x 3,743.25

| Provider | Base per case | With retries | Effective per case incl. evaluation (monthly / 2,050) | Monthly total (production + evaluation) | vs 1.10 per case |
|---|---|---|---|---|---|
| A large | 0.0300 | 0.0345 | 0.0548 | USD 112.30 | Fits (5%) |
| A small | 0.0080 | 0.0092 | 0.0146 | USD 29.95 | Fits (1.3%) |
| C mid | 0.01012 | 0.01164 | 0.0185 | USD 37.88 | Fits (1.7%) |
| B large | 0.0220 | | | | Excluded: US only, no zero retention; fails T-AURA and any EU-residency tenant |

Sensitivity: doubling case volume (e.g. also running R2 on the 22% of non-actionable alerts reviewers open, about 2,057/month) doubles these totals (A large USD 224.60) and still fits.

## 4. Retrieval cost

Tenant-scoped precedent retrieval uses per-tenant indexes. Cl.22 (T-MERIDIAN prohibits reuse of models or indexes built on its data) means T-MERIDIAN's index is never shared, queried from, or used to build anything for another tenant; this is a per-tenant index design, so there is no shared pool to optimise.

**Assumptions:** per human case, 1,000 query tokens + 6,000 tokens embedded when the disposition is stored as precedent = 7,000 tokens.

- 2,050 x 7,000 = 14.35M tokens/month x 0.02 = **USD 0.29/month**
- Screening embeddings (3.1): 5.7M tokens = USD 0.11/month
- One-time document embedding (**assumption**: stability PDFs 20,000 tokens, SOPs 8,000, contracts 15,000): 11,040 x 20,000 + 4,312 x 8,000 + 1,244 x 15,000 = 274M tokens x 0.02 = **USD 5.48** one-off. Indexing is outside the inference ceiling; its cost is storage and operations (section 7), not embedding fees.

Retrieval fees are rounding error. The cost of retrieval is the vector store, which is sized in section 7.

## 5. Quiet-Sunday cost: the shape of the bill

| Option | Idle cost | Monthly at current volume |
|---|---|---|
| R0 | 0 | 0 |
| Hosted APIs (A, C) | About 0 (per-token only) | Section 3 (about USD 30-112) |
| Self-hosted, 1 instance 24x7 | 5.67 x 24 = USD 136.08/day | 5.67 x 730 = **USD 4,139.10** (USD 4,082.40 at 720 h) |

One always-on instance costs USD 1,139.10 **more than the entire USD 3,000 envelope** (1.41x the 2,939 figure) before a single token is served. Hosted pricing gives the flat-on-a-quiet-Sunday shape the CFO asked for; self-hosting makes the floor the whole bill.

**Break-even vs hosted** (4,139.10 / cost per run): A large 138,000 runs/month (67x current case volume); C mid 409,000 (200x); A small 517,000 (252x). Self-hosting never pays on price at this volume.

**When self-hosting is justified:** only if tenants that prohibit external APIs *need* generated narratives, **and** the instance is shared across the India cell. For those 7 tenants (T-VIRENT + 6 unlisted), the instance costs USD 4,139.10 / 7 = about USD 591 per tenant per month, with unverified assumptions that g5.12xlarge capacity is available in the India region and that one instance sustains the load. **Alternative: R0 for prohibited tenants**, at zero cost, with the same evidence and decision path. Recommendation: ship R0 for them; revisit self-hosting only if a prohibited tenant's reviewers show a measured need for narrative.

## 6. Per-tenant residency routing

| Tenant | Rule | Route |
|---|---|---|
| T-AURA | EU residency in the DPA | EU-hosted endpoints only (Provider A EU or C EU); never B; otherwise R0 |
| T-NORDIA | US-hosted only for non-batch-identifiable data | US endpoint (A or C) with a pre-send filter that strips batch-identifying fields; otherwise R0 |
| T-VIRENT | India-only, no external APIs | R0 only |
| T-MERIDIAN | No reuse of models or indexes built on its data | Own isolated index; never a shared index or fine-tune |
| Unlisted tenants | Mixed | Default R0; model route enabled per tenant by explicit configuration, with a per-tenant kill switch |

Routing is data-driven per tenant, evaluated before any call leaves the cell. A routing miss (no permitted endpoint) resolves to R0, not to a default provider.

## 7. Separate sizing (not part of the ceiling)

**These are estimates from stated assumptions.** Retention horizon 7 years = 2,556.75 days = 84 months; volumes held flat.

| Item | Assumption (low / high) | Per month (low / high) | 7-year retained (low / high) |
|---|---|---|---|
| Telemetry, 10M readings/day | 40 B / 120 B per reading; compression 5:1 / 2:1 | Raw 12.2 / 36.5 GB; stored 2.4 / 18.3 GB | Raw 1.0 / 3.1 TB; stored **0.20 / 1.53 TB** |
| Consignments, 128,000/month | 2 KB / 10 KB per record incl. leg events | 0.26 / 1.28 GB | 0.02 / 0.11 TB |
| Alert evidence packages, 11,400/month | 100 KB / 500 KB (central 200 KB = 2.28 GB) plus referenced document digests (not copies) | 1.14 / 5.7 GB | 0.10 / 0.48 TB (central 0.19) |
| Stability PDFs, 11,040 | 3 MB / 12 MB average (about 18% are scan-of-scan) | One-off 33 / 132 GB | Same (corpus, plus new versions) |
| SOPs, 4,312 | 0.5 MB / 2 MB (1,180 are scans) | One-off 2.2 / 8.6 GB | Same |
| Contracts, 1,244 | 1 MB / 4 MB | One-off 1.2 / 5.0 GB | Same |
| Vector indexes (per tenant) | 1,024 dim / 1,536 dim float32; chunk 800 / 500 tokens; x1.5 index overhead; 274M tokens | One-off 2.1 / 5.0 GB total, partitioned per tenant | Same plus precedent growth (2,050 cases/month, negligible) |
| Audit log | 20 KB / 100 KB per alert | 0.23 / 1.14 GB | 0.02 / 0.10 TB |

Totals: documents about 37 / 146 GB; time-series dominates at 0.2-1.5 TB over 7 years; everything else below 1 TB combined. Storage is the smaller part of the capital line; the larger parts are WORM/immutability, backup copies (multiply by replicas, per cell), restore testing for the one-hour retrieval commitment, and operations. These are not priced here because the pack gives no storage price list; **no storage dollar figure is claimed**.

## 8. What not to conflate

- **Consignment value vs decision value.** The USD 84,000 average consignment value is not the value at stake in a destroy decision. A destroy condemns the affected pallets only. USD 19.4M / about 2,700 decisions = **about USD 7,200 per destroy decision**. The 32% salvageable is an audit estimate, unverified; it is not a saving Sentinel delivers (a salvage requires a human to decide differently on evidence that exists).
- **Capacity vs cash.** Adjudication hours: 2,050 x 96 min = 3,280 hours/month (39,360/year). At a headcount-weighted loaded rate (**assumption**) of (14x18 + 6x61 + 3x74)/23 = USD 36.5/hour, this is about USD 1.44M/year, consistent with the USD 1.51M QA cost, which suggests that adjudication is most of reviewer time. R0 and R2 assemble evidence; they do not make decisions, and the pack gives no measured time reduction. Released reviewer capacity is **capacity at risk and opportunity** (including 14 late notifications in two quarters), not guaranteed cash savings; no headcount reduction is assumed. Any claim of time saved needs the replay and pilot evidence from doc 08.

## 9. Monthly budget by route and provider

Total = production + evaluation (section 3.2) + case retrieval (0.29) + screening embeddings (0.11). USD, per month, at current volume.

| Route / provider | Total | vs 2,255 (cases) | vs 684 (screening) | vs 2,939 binding | vs 3,000 envelope |
|---|---|---|---|---|---|
| R0 only (all tenants) | 0 | Fits | Fits | Fits | Fits |
| R0 + embeddings (R1 not adopted) | 0.40 | Fits | Fits | Fits | Fits |
| R2 on Provider A large | 112.70 | Fits | Fits | Fits | Fits |
| R2 on Provider A small | 30.35 | Fits | Fits | Fits | Fits |
| R2 on Provider C mid | 38.28 | Fits | Fits | Fits | Fits |
| R2 on A large at 2x volume | about 225 | Fits | Fits | Fits | Fits |
| R1 narratives on A large (not adopted) | 118 screening | n/a | Fits | Fits | Fits |
| Self-hosted, 1 instance 24x7 | 4,139.10 | **Does not fit** | **Does not fit** | **Does not fit** | **Does not fit** |
| Provider B large (any) | n/a | Excluded by residency/zero-retention | | | |

Per-case unit ceiling check (cases): effective cost per case 0.0548 / 0.0146 / 0.0185 against USD 1.10. Fits with a factor of 20 or more.

The ceiling is not the constraint on this design; residency, determinism and reviewability are. The unconstrained risks are the separate capital line (section 7) and a self-hosted instance. This is why the cost position is "flat and bounded" rather than "USD 3,000".
