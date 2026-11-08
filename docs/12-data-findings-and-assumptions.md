# Data findings and assumptions

This document records what the reference pack (`KCCS_Sentinel_Reference_Data_Pack.xlsx`, extract date 2026-09-14) does and does not establish, where it contradicts the brief or itself, and which position the design and prototype take. It complements [where we land](01-where-we-land.md), [risks](09-risks-assumptions-and-open-questions.md) and the [roadmap](10-future-roadmap.md); it does not repeat them.

Conventions: "brief §N" is a section of the case brief. Tenants are the pack's pseudonymous codes (`T-AURA`, `T-VIRENT`, …). Rows are Excel rows. Free text (override reasons, notes, comments) is deliberately not quoted. Status labels: **implemented** (in `prototype/src/sentinel/evidence/`), **proposed** (design only), **unavailable** (not in the pack).

## 1. How the inspection is reproduced

```bash
python scripts/inspect_workbook.py <pack.xlsx> --output-dir artifacts/private
```

The script writes `workbook-inspection.json` (per-column profiles with Excel row ranges, plus computed findings) and the SHA-256 of the input. `artifacts/private/` is gitignored; real-data outputs are never committed. Counts below come from that inspection, from the analyzer (`assess()` over all 420 events, `known_at` defaulting to the extract date) and from targeted lookups of the private pack.

| Aspect | Private pack (source of the numbers here) | Public anonymized copy (`scripts/build_anonymized_workbook.py`) |
|---|---|---|
| Sheet/column structure, row counts | Original | Preserved |
| SOP overlaps, product resolution, shared identifiers | Original | Preserved (structural results reproduce) |
| Firmware builds, bulletin text | Original | Redacted: firmware and bulletin findings do not reproduce publicly |
| Stability readability | Original | Redacted |
| Tenant constraints, incidents | Original | Redacted |
| Free text, names | Present | Not copied |

Consequence: the structural claims (§3 F-06 to F-09, F-17 to F-21) can be re-run on the public copy; firmware, readability, window and incident claims can only be re-run on the private pack.

Two corrections to the inspection tooling found while writing this document (neither fixed here): (a) `stability_path_does_not_mention_owner_tenant` in `scripts/inspect_workbook.py` compares the string `"t"` (the part of the tenant code before the first `-`) with the path, so its count of 0 is vacuous; F-07 uses a direct check instead. (b) The demo-case selector reports `sop_boundary_day` and carrier ambiguity as unmatched, while the pack contains two boundary-day events and two parent/subsidiary carrier pairs (F-09, F-21).

## 2. Sheet inventory

| Sheet | Rows | Excel rows | Key columns | What it is / is not (README's own description) |
|---|---|---|---|---|
| `00_README` | 40 | 2–46 | — | Extract notes and the known-problems list. Not exhaustive ("certainly not listed all"). |
| `01_Excursion_Events` | 420 | 2–421 | `event_id`, `alert_ts_utc`, `tenant_code`, `source_system`, `logger_fw`, `product_ref_as_received`, `reg_window_hours` | Alerts as the sources present them, uncleaned. Stratified, not random. Outcome columns (`triage_outcome`, `final_disposition`, …) are history, not labels. |
| `02_Product_Master` | 59 | 2–60 | `tenant_code`, `internal_sku`, `gtin`, `stability_study_ref` | Product master as received from tenant ERPs (4 ERP kinds); identifiers populated inconsistently; storage spec is free text. |
| `03_Facility_Registry` | 70 | 2–71 | `source_system`, `code_in_source`, `timezone_in_source`, `cold_rooms` | 14 sites × 5 systems; the same site appears more than once; timezone wrong for two sites (not identified). |
| `04_Carrier_Contracts` | 14 | 2–15 | `contract_id`, `names_seen_on_documents`, `parent_of`, `effective_to`, `claim_window_days` | Legal's contract index. Parent/subsidiary pairs with different claim windows. Not the contracts or amendments. |
| `05_SOP_Index` | 203 | 2–204 | `doc_id`, `revision`, `effective_from/to`, `supersedes_text` | Docuvault export (metadata only). Supersession is free text; the SOPs and annexures are not included. |
| `06_Stability_Index` | 107 | 2–108 | `study_ref`, `tenant_code`, `readable`, `permitted_excursion_text` | Hand-built by an intern in 2025, unmaintained, ~60% of the repository. Not authoritative on ownership via `file_path_text`. |
| `07_Alias_Observations` | 207 | 2–208 | `entity_kind`, `string_a/b`, `confirmed_by`, `confirmed_on` | Reviewer-confirmed same-thing pairs; ad hoc, not exhaustive, not authoritative. Sighting counts are platform-wide, not within the 420. |
| `08_Reviewer_Queue_Log` | 200 | 2–201 | `case_ref`, `reviewer_utc_offset`, `local_start/end`, `active_minutes` | One row per human-opened case in 01; local time to the reviewer. |
| `09_Override_Reasons` | 24 | 2–25 | `case_ref`, `engine_said`, `reviewer_decided` | The 24 cases with a typed reason; other overrides carry none. Free text, not used by the prototype. |
| `10_Reviewer_Questions` | 12 | 2–13 | `#`, `where_the_answer_lives_today`, `typical_minutes` | Workshop transcription (2026-07-30). |
| `11_Systems_Inventory` | 9 | 2–10 | `system_id`, `access_method`, `ordering_and_backfill` | The nine systems and their defects. |
| `12_Tenant_Constraints` | 9 | 2–10 | `tenant_code`, `data_residency_position`, `third_party_model_apis`, `who_signs_a_disposition` | 8 of 34 tenants chosen to span variation, plus one row "26 others" (91,600 shipments/month; 14 with a residency clause, 6 prohibiting third-party model APIs, 4 requiring non-English regulator output). |
| `13_Volume_And_Cost` | 31 | 3–38 | label/value pairs | Population-level volumes, costs, windows, ceilings, procurement price list (2026-09-01). |
| `14_Incident_Log` | 6 | 2–7 | `ref`, `date` | INC-2411, INC-2502, INC-2506, INC-2509, AUD-2603, INC-2512. |

Event counts by tenant (01): T-VIRENT 164, T-SAHYADRI 83, T-KAVERI 44, T-AURA 33, T-NORDIA 28, T-CAMPOS 26, T-PINNACLE 26, T-MERIDIAN 16. Source systems: SYS-01 228, SYS-02 96, SYS-03 96. Alerts span 2025-12-16 to 2026-09-09.

## 3. Data-quality findings

| # | Finding | Evidence | Consequence for design | Prototype treatment |
|---|---|---|---|---|
| F-01 | **Stratified, not representative.** | README row 28: strata add to 420 = 61 re-adjudicated under TT-CB-114 + 24 written overrides + 13 late-notification + 57 INC-2502 storm + 1 reproduced case + 264 random (README: 14 late and 58 storm records in all, one of each among the 24). In-tab 01: 275 of 420 triaged non-actionable (65%) vs 82% in `13` row 6; 200 of 420 opened by a human vs 2,050/11,400 (18%); `08` median active minutes 73.5 vs 96 (`13` row 11). | No rate, accuracy or savings claim from the 420. | **Implemented**: assessment output is structural coverage only; summary states it is not a population estimate. |
| F-02 | **Outcome ratios are not population estimates.** | 14 of 28 reportable events late (50%) by construction; no late event in the 360 h markets; 36 reviewer overrides among 200 opened cases (18%) vs 23% population (`13` row 15). | Targets must be measured prospectively on the live population (see [where we land](01-where-we-land.md#assessment-of-the-board-targets)). | **Implemented**: outcome fields listed in `HISTORICAL_OUTCOME_FIELDS`, never read. |
| F-03 | **Alias observations are not a master.** | `07`: 207 rows (product 79, facility 77, carrier 51); `confirmed_by` and `confirmed_on` populated on all rows (23 distinct confirmers, 2025-06-01 to 2026-09-03); 4 rows marked `N` (rows 205–208). No status column; sighting counts are platform-wide. | A confirmation is an assertion by a person, dated; it cannot be a join table. The four `N` rows show some assertions are wrong. | **Implemented**: surfaced as `unverified_alias_candidates` only when `same_real_world_thing` is true and `confirmed_on` ≤ `known_at`; never resolves an entity (EXC-111064). |
| F-04 | **Stability index is incomplete.** | `06`: 107 rows; readable Y 87 / "N — scan of scan" 7 / "Partial — scan quality" 13; `permitted_excursion_text` blank on 41 (long-term, accelerated and photostability studies do not set excursion limits). Product→study: 47 refs found under the same tenant, 5 absent from the index, 7 of 59 product rows with no ref. `11` row 7: 11,040 PDFs, ~18% scans of scans. | Index presence is not evidence of coverage; readable ≠ applicable. | **Implemented**: unreadable or limit-less studies are unusable candidates plus a missing input; full reports are always listed as absent. |
| F-05 | **Absent study ≠ no study.** | 5 product refs absent from `06` (e.g. EXC-111519). README: index ≈60% of repository. | A blocker with a named lookup action, never "no study exists". | **Implemented**: rejected with reason "absence is not evidence that no study exists"; human action to locate it in SYS-06. |
| F-06 | **Wrong presentation.** | `02` row 2 (T-AURA, SKU-INS-0442) cites STB-8597; `06` row 3 describes it as a vial study for a prefilled-syringe product. `02` row 60 (T-KAVERI) cites STB-7388; `06` row 104 is a vial study (EXC-112135). Assessment: 23 events carry this conflict (T-VIRENT 8, T-AURA 6, others 9). | A matched reference can still be the wrong evidence. | **Implemented**: presentation tokens compared; mismatch is a conflict and the study unusable. Limit: only detects when both sides state a presentation. |
| F-07 | **Stability ownership vs path.** | `06` rows 9 (owner T-AURA, path under T-VIRENT), 47 (owner T-PINNACLE, path under T-MERIDIAN), 64 (owner T-MERIDIAN, path under T-PINNACLE); rows 4, 6, 19, 57, 72 under a shared "Misc" folder. | Rows 47 and 64 are the Cl.22 competitor pair: trusting the path would attribute each study to the other. | **Implemented**: ownership comes only from `tenant_code`; unit test `test_misleading_file_path_does_not_transfer_ownership`. |
| F-08 | **SOP revisions overlap** (table below). | 27 overlapping revision pairs across 10 `doc_id`s. Events with an open SOP conflict: sop-vir-9115 35, sop-kav-5329 16, sop-kav-9392 13, sop-cam-7820 6, sop-aur-6613 6, sop-mer-5228 4 (the two boundary-day events are counted under their documents). `supersedes_text` is free text typed by the issuer. | Overlap is a conflict for document control to settle, not a tie-break rule. | **Implemented**: overlapping revisions in force at excursion start → conflict + required human action; no revision is chosen. |
| F-09 | **Date-only SOP dates; boundary day; site scope.** | All 203 `effective_from` are `YYYY-MM-DD`; 64 open-ended (blank `effective_to`); 114 site-specific; formats: native PDF 114, scanned 50, scanned with handwriting 17, DOCX 22. Two events fall on a same-tenant boundary date: EXC-110098 (`05` row 16, sop-aur-6613 Rev 03 ends 2026-03-22) and EXC-112093 (`05` row 200, sop-kav-5329 Rev 03 ends 2026-03-06). | Whether the last day is inclusive, and in which timezone, is undefined in the index. | **Implemented**: intervals are half-open at 00:00 UTC. A same-tenant revision whose date-only `effective_to` equals the excursion date is not dropped silently: it is listed under `evidence.sop.rejected` with the reason, and a conflict plus a document-control action are raised (observed by running `assess` on EXC-110098, which now reports sop-aur-6613 Rev 03 as a boundary-day rejection alongside Rev 04). The first version of the kernel did drop it silently; this review found it, and the fix is recorded in the working log. |
| F-10 | **Timestamps: UTC by assumption.** | All three `*_utc` columns parse on 420/420 rows, none with a timezone marker, minute resolution. `alert_ts_utc − excursion_start_utc` by source: SYS-01 5–25 min (median 15, consistent with the 15-minute poll), SYS-02 1–86 (median 7), SYS-03 0–4 (median 2). | The regulatory clock starts at alert (README row 43); excursion start is detection-latency-blind. | **Implemented**: clock from `alert_ts_utc`; SOP/stability "as at" uses `excursion_start_utc`. UTC is an assumption, stated in `time_semantics`. |
| F-11 | **`rules_engine_recommendation` is a misnomer.** | README row 45: since 2024 the column holds the assistant's draft. Values: AUTO_CLOSE 275; disposition drafts 145. `case_opened = N` is 220, so 55 AUTO_CLOSE rows were opened by a human anyway. | Rule-engine accuracy cannot be derived from this column; assistant drafts are not rule outputs. | **Implemented**: excluded from the assessment. |
| F-12 | **Prior outcomes are not ground truth.** | 61 events `reopened_later = Y`, all on TT-2.14.3 (61 of 91): a historical disposition was itself overturned. 36 overrides vs 24 written reasons. 220 auto-closed alerts never audited (README row 36). | Backtests compare against history as a *discussion list*, not a score. | **Implemented**: assessment ignores outcomes. 118 events have a historical disposition alongside an open conflict; these are candidates for human re-review, not evidence anyone was wrong. |
| F-13 | **Leakage of later-known facts.** | Bulletin TT-CB-114 recorded 2026-04-11 (`14` row 4). TT-2.14.3 alerts run 2026-01-18 to 2026-09-08: 63 in the three weeks before the bulletin, 19 after it. Product master has current values only (`last_updated` ≤ 2026-03-24); alias `confirmed_on` runs to 2026-09-03. | A replay on today's data silently uses knowledge the original reviewer lacked. | **Implemented**: `known_at` hides bulletins and aliases recorded later (EXC-110336: at 2026-01-01 no firmware conflict, at 2026-04-11 it appears). **Unavailable**: recorded-time history for SOP, stability and master rows; the extract date 2026-09-14 is the only global knowledge time. |
| F-14 | **Aggregates, not raw series.** | `duration_min` median 31 (max 1,345); `readings_in_window` 1–268, median 7, ≤2 on 73 events; `gateway_gap_min` > 0 on 99; `interpolated` = Y on 76. `11` row 2: SYS-01 delivers five-minute averages, raw kept 30 days. | Cumulative exposure, measured vs interpolated split and calibration re-computation cannot be done. | **Implemented**: "raw series not supplied" is a standing missing input; gap, interpolation and low-count flags. No series is synthesized. |
| F-15 | **No batch identity or lifetime exposure.** | No batch column in `01`; README: batch references pseudonymised; `10` question 8 answered "Nowhere". | Cumulative allowances (e.g. `02` row 2's cumulative-hours text) cannot be checked. | **Implemented**: standing missing input. |
| F-16 | **Facilities duplicated across five systems; wrong timezones.** | `03`: 70 rows = 14 sites × 5 systems. BLR-CS-02 (rows 2–6): five different names, `code_in_source` shared by three, `cold_rooms` 2/1/6/9/6. `gmp_licence_ref` blank on 26 rows. Every timezone equals its country default (IN, US, NL, BR, DK, DE), so the two wrong entries are undetectable in-pack. Lookups over 420 events: 634 resolved, 153 multiple-source, 53 unresolved. | Site identity needs a curated crosswalk; timezone needs site confirmation. | **Implemented**: multi-record matches kept as-is; conflicts fail safe; registry timezone flagged UNTRUSTED. |
| F-17 | **BMS records carry no tenant tag.** | SYS-03: 96 events (T-VIRENT 49, T-SAHYADRI 26, T-KAVERI 10, five others 11). `12` row 3: "4 of 9 sites feed BMS without tenant tags". The 58 INC-2502 records (2026-02-19 09:12–09:51) are SYS-03 and attributed to T-VIRENT 30, T-SAHYADRI 22, T-KAVERI 6 for one facility's alarms. | Tenant attribution is inferred from the TMS (not in the pack); a tenant-scoped design must not trust it. | **Implemented**: conflict "attribution inferred, not recorded at source" on all 96; quarantine (EXC-111008). |
| F-18 | **Identifiers shared across tenants.** | 14 internal SKUs, 11 GTINs and 14 brand labels appear under ≥2 tenants; SKU-INS-0442 under 5, GTIN 08901234500035 under 4 (including EXC-107133's tenant). | Any non-tenant-scoped join leaks (brief §3, August). | **Implemented**: exact tenant-scoped lookup; cross-tenant access is indistinguishable from missing (unit tests). |
| F-19 | **`product_ref_as_received` is a mix.** | 420 events: brand/other string 245, SKU 72, GTIN 61, blank 42. Exact tenant-scoped match: 237 resolved, 141 unresolved, 42 missing. | Resolution must be explicit about its basis. | **Implemented**: exact normalized match on brand/SKU/GTIN/legacy within tenant; no fuzzy matching. |
| F-20 | **Carrier names vs legal entity vs parent.** | `04`: 14 contracts; two parent/subsidiary pairs with different claim windows (CNT-2021-0118 / CNT-2023-0441: 30 vs 21 days; CNT-2024-0612 / CNT-2024-0655: 30 vs 14). Every received carrier string appears in a contract's names; none matched two legal entities (272 resolved, 0 ambiguous). **Defect**: `effective_to = "evergreen"` on rows 5, 10, 14 fails date parsing, so 148 events show "no contract effective". Rows 10 and 14 have no cold-chain clause and 7-day windows. | Claims are a separate financial track; readiness is unaffected (186/234 unchanged). | **Implemented with a defect**: ambiguity status exists and is unit-tested on synthetic data only (`test_parent_and_subsidiary_contracts_are_ambiguous`). Proposed fix: treat `evergreen` as an explicit open-ended token. Carrier end dates are inclusive here but SOP end dates exclusive — an inconsistency to resolve with legal. |
| F-21 | **`08` is reviewer-local time.** | Offsets +05:30 (138 rows), +02:00 (36), −04:00 (26). README row 41: `local_end` minus offset = alert + `days_to_disposition`. `08` row 113 (EXC-107133): `local_start` 12:24 at +05:30 = 06:54 UTC, queue wait 0.4 h; brief §2 narrates a pick-up three hours after the alert (09:30 UTC). | Cross-log ordering needs offset normalization; the brief's narrative and the log disagree. | **Unavailable to the analyzer by design** (reviewer artefact). |
| F-22 | **`spec_text_as_received` vs product master.** | Of 237 events with one master row: 45 string-equal, 192 differ; 190 of those differ although the master's `last_updated` precedes the alert (formatting variants: "2-8 °C", "Refrigerated (2-8)", "+2/+8 C"), 2 differ with a later master update. 21 distinct spec strings across events. | String equality neither detects nor excludes drift; ranges need semantic parsing. | **Not implemented**: both strings are carried; no parse or comparison. |
| F-23 | **Two clocks on one case.** | `reg_window_hours` on 28 events (`regulator_reportable` Y 28 / N 392): 24 h ×9 (T-PINNACLE 5, T-MERIDIAN 4), 72 h ×8 (T-AURA 5, T-NORDIA 3), 120 h ×3 (T-CAMPOS), 360 h ×8 (T-VIRENT 5, T-SAHYADRI 2, T-KAVERI 1). `reported_within_window` N on 14: T-AURA 5, T-NORDIA 3, T-PINNACLE 3, T-MERIDIAN 3, all in the 72 h and 24 h markets (matches `13` row 23). EXC-110287 (T-KAVERI) carries 360 h, notified at 140 h. | Disposition (median 6.1 days among opened cases here) and notification run independently. `N` is a provisional input; 24 h stands in for "next business day". | **Implemented, provisional**: clock from `alert_ts_utc`, fixed hours in UTC, `N` marked provisional, unknown window → URGENT_POLICY_REVIEW. Business-day calendars **unavailable**. |

**SOP overlaps (`05_SOP_Index`)**

| `doc_id` | Tenant | Overlapping revision pairs | Excel rows |
|---|---|---|---|
| sop-aur-6613 | T-AURA | 01/02, 02/03, 03/04 | 14–17 |
| sop-vir-9115 | T-VIRENT | 01/02, 02/03, 03/04, 04/05 | 35–39 |
| sop-pin-1059 | T-PINNACLE | 01/02 | 92–93 |
| sop-pin-8622 | T-PINNACLE | 01/02 | 98–99 |
| sop-mer-5228 | T-MERIDIAN | 01/02, 02/03, 03/04, 03/05, 04/05 | 112–116 |
| sop-mer-2013 | T-MERIDIAN | 01/02, 02/03 | 117–119 |
| sop-cam-7820 | T-CAMPOS | 01/02, 02/03, 03/04 | 163–166 |
| sop-kav-2571 | T-KAVERI | 01/02, 02/03, 03/04 | 183–186 |
| sop-kav-5329 | T-KAVERI | 01/02, 02/03, 03/04 | 198–201 |
| sop-kav-9392 | T-KAVERI | 01/02, 02/03 | 202–204 |

Rev 03 of sop-mer-5228 overlaps both Rev 04 and Rev 05, so it is not a simple chain. Documents sop-kav-2571, sop-pin-1059, sop-pin-8622 and sop-mer-2013 produce no event conflict in the 420 (no sampled excursion falls in their overlap windows, per the assessment; not separately verified).

## 4. Brief incidents checked against the pack

| Incident (`14` row) | Brief | What the pack shows | Verifiable? |
|---|---|---|---|
| INC-2411 (row 2), 2025-11-06 | §3 November: prompt change, destroy share 11%→19%, 31 of 34 customers, USD 310k | Dated before the first alert (2025-12-16): no event in `01` is from the incident. No prompt or model version column anywhere in the pack, so the version that produced any draft cannot be shown — the exact gap the EU tenant describes. In-tab drafts: DESTROY 15 of 420 (stratified, not comparable to 11%/19%). | No |
| INC-2502 (row 3), 2026-02-19 | §3 February: 1,912 alerts in 38 minutes, ~600 queued, four cases breached 72 h | 58 SYS-03 records on 2026-02-19 09:12–09:51 (39 minutes at minute resolution); 44 `case_opened = N`, 14 `Y`; attributed to three India tenants. The pack does not link the 14 late notifications (EU and US tenants) to the storm. | Count and timing only |
| INC-2506 (row 4), 2026-04-11 | §3 April: 214 cases, 61 re-adjudicated | 91 TT-2.14.3 events across all 8 tenants; 61 are `reopened_later = Y` (all 61 on TT-2.14.3), i.e. the 61 stratum is a subset of 91; 30 TT-2.14.3 events were not reopened. 63 alerts in the three weeks before the bulletin (vs 214 closed cases population-wide); 19 alerts after it. Nine withdrawn carrier invoices: no invoice data in the pack. | Partly |
| INC-2509 (row 5), 2026-06-02 | §3 June: 30-day sunset, 7-week requalification | No event-level evidence. `13` row 35: only Provider B carries 30-day notice (US only, no zero-retention); others 6–12 months. | Price list only |
| AUD-2603 (row 6), 2026-03-24 | §3 March: disposition dated 14 Aug 2025 | The audited disposition (2025-08-14) predates the pack's alert range (2025-12-16 to 2026-09-09): the audited case is not in the pack. The index lists T-AURA SOP revisions in force on that date (e.g. sop-aur-9238 Rev 04, `05` row 5, annexure not supplied); stability data, series and approver cannot be reconstructed. T-AURA has 33 events, 5 reportable, all 5 notified late (stratum effect, not a rate). | No |
| INC-2512 (row 7), 2026-08-14 | §3 August: competitor precedent leak | The pair is T-MERIDIAN and T-PINNACLE (`12` rows 5–6). They share SKUs sku-bio-0771, sku-ins-0442, sku-orl-0012; `06` rows 47 and 64 are cross-filed between them (F-07). | Leak path confirmed structurally |

## 5. Reviewer questions (`10_Reviewer_Questions`) coverage

| Q | Question (paraphrased) | Can the pack answer it? | Sheets | Prototype |
|---|---|---|---|---|
| 1 | SOP revision in force at origin and destination | Partly: index metadata only | `05`, `03` | SOP candidates as at excursion start, overlap conflicts, date-only and annexure flags. Facility applicability not evaluated beyond a "site-specific" flag. |
| 2 | Stability limit for this temperature, duration, cumulative | Partly | `06`, `02` | Study candidates with usability flags; cumulative needs batch history (absent). |
| 3 | Prior incidents on lane, carrier, equipment (90 days) | No: one count column | `01` `prior_excursions_lane_90d` | Count carried; no lane history or decision grounds. |
| 4 | Parent or subsidiary contract | Partly: 14 contracts, no amendments | `04` | Entity status, claim window; `evergreen` defect (F-20). |
| 5 | Gap overlap, measured vs interpolated | Partly: aggregates | `01`, `11` | Gap and interpolation flags; raw series missing. |
| 6 | Same physical excursion as another event | No: 107 events are labelled duplicates but every `shipment_ref` occurs once, so the earlier alert is not in the pack | `01` | No duplicate detection implemented. |
| 7 | Product loaded when facility alarmed | No: needs TMS and tenant-tagged BMS | `11`, `03` | Attribution quarantined; no load check. |
| 8 | Earlier batch excursions, cumulative exposure | No: no batch identity | — | Standing missing input. |
| 9 | Who signs, second signature | Partly: 8 tenants + one aggregate row | `12` | Signatory text carried; dual signature implemented with a local heuristic, not a production policy. |
| 10 | Reportable, market, deadline | Partly: windows on 28 events, no market field or calendar | `01`, `12`, `13` | Provisional clock from alert; unknown → urgent review. |
| 11 | What was decided last time, and why | Partly: 24 reasons, outcomes; the 1,100-row spreadsheet is not in the pack | `09`, `01` | No precedent retrieval by design (tenant isolation); proposed tenant-scoped structured argument. |
| 12 | Reconstruct in two years | No (raised at AUD-2603) | — | Frozen, hash-verified assessment packages; retention is proposed, not implemented. |

## 6. Contradictions and assumptions register

| # | Evidence | Conflict or gap | Chosen position | Risk | Resolver |
|---|---|---|---|---|---|
| A-01 | Brief §6 "about 64%" vs "82% non-actionable"; `13` rows 6, 12 | 64% of all alerts = 78% × 82%. Same denominator; not rival figures. | Treat both as consistent; 70% of all alerts requires closing ≈85% of non-actionable alerts. | Target read as 70% of non-actionable would be trivially met. | Board, with QA |
| A-02 | Brief §2 "roughly 82%"; `13` row 6; `09` | The 82% is a population share on 11,400 alerts; the pack's 275/420 is stratified. | Use `13` only for population ratios. | Sizing from the sample misleads. | Data Services |
| A-03 | Brief §3/§4 (72 h, 5 days, next business day) vs `13` row 22 | Tab 13 adds India 15 days (notifiable products only); `01` encodes 360 h for the three India tenants and 24 h for both US tenants, while the brief names one US state programme. | Windows are provisional inputs; 24 h is a stand-in. | Wrong clock for India or US. | Regulatory Affairs |
| A-04 | `13` rows 25–26 vs CFO quote | USD 1.10 per human-reviewed case × 2,050 = USD 2,255 and USD 0.06 per alert × 11,400 = USD 684 sum to USD 2,939 against a USD 3,000/month ceiling. Whether the 2,050 also incur the per-alert charge is unstated (overlap would lower the total). | Additive reading (conservative); see [risks](09-risks-assumptions-and-open-questions.md). | USD 61/month headroom; ingestion, storage, retention are outside it. | Finance |
| A-05 | `13` rows 19–20 | Average consignment USD 84,000 vs about USD 7,200 per destroy decision: destroy condemns pallets, not consignments. | Value per decision, not per consignment. | Savings overstated 10×. | QA |
| A-06 | `13` row 21; brief §2 "about a third" | 32% salvageable is an internal-audit estimate (≈USD 6.2M), not measured. | No savings claim. | Business case rests on an estimate. | Internal audit |
| A-07 | `06` `file_path_text` vs `tenant_code`; README row 38 | Path and owner disagree on 3 rows (F-07). | `tenant_code` is authoritative; paths never confer ownership. | A mislabelled `tenant_code` is itself unverifiable. | QA / data owner |
| A-08 | `05` `supersedes_text` | Free text; 27 overlapping pairs. | Overlap is a conflict for document control, not resolved by text. | Reviewer workload on overlap-heavy tenants (T-VIRENT). | Document control |
| A-09 | README row 45 | Column named for the rules engine holds assistant drafts. | Excluded; not used as a rule-engine signal. | Rules-engine accuracy unmeasurable from the pack. | Platform engineering |
| A-10 | `11` row 4; `12` row 3 | BMS has no tenant tag; attribution via TMS (absent). | Quarantine all 96 SYS-03 events. | Real alarms delayed behind attribution. | Platform + tenant |
| A-11 | `05` date-only dates | Inclusive/exclusive end and timezone undefined. | Half-open at 00:00 UTC (F-09 gap noted). | Wrong revision on boundary day. | Document control |
| A-12 | `03`; README row 31 | Two facility timezones wrong, not identified; 08 uses reviewer-local time. | Registry timezone untrusted; site confirmation required. | Calendar-day windows computed in the wrong zone. | Site operations |
| A-13 | README row 6; brief circulated 2026-09-18 | Extract date 2026-09-14 is the only global knowledge time. | Used as the `known_at` default. | Recorded-time before then unreconstructable. | Platform engineering |
| A-14 | Brief §6 "all 34 within nine months"; `12` row 10 | 14 of the 26 unlisted tenants have a residency clause and 6 prohibit third-party model APIs; with the three named residency tenants that is 17 of 34 bound. | Per-tenant gating (see [roadmap](10-future-roadmap.md)); 34 in nine months is a sequence, not a commitment. | Schedule slip or onboarding under an unqualified policy. | Board |
| A-15 | Brief §2 vs `08` row 113 | Narrated pick-up time disagrees with the log (F-21). | Log treated as the record. | Narrative figures not reusable as test fixtures. | Sponsor |
| A-16 | `04` rows 5, 10, 14 | `evergreen` effective end. | Open-ended by intent; prototype defect (F-20). | Spurious "no contract" on 148 events. | Legal; engineering fix |

## 7. What the pack cannot support

| Gap | Why it matters | Prototype treatment |
|---|---|---|
| Raw temperature series | Exposure, interpolation split, calibration re-computation | Standing missing input; aggregates only; nothing synthesized. |
| Controlled documents (SOPs, annexures, studies, contracts) | An index row is not procedure evidence | Always listed as absent; index matches are candidates. |
| Batch history and lifetime exposure | Cumulative allowances | Standing missing input. |
| Recorded-time history (when each row was entered or corrected) | True "as known then" replay | `known_at` over incidents and aliases only; corrections as appended records (demonstration fixture, not a real action). |
| Calendars (business days, holidays, per-market) | Next-business-day and calendar-day windows | Fixed-hours provisional clock; unknown window → urgent review. |
| Lane/carrier/equipment history, TMS mapping, duplicate links | Q3, Q6, Q7 | Not modelled; no inference from lookalike events. |
| Prompt and model versions | Which version produced a draft | Unavailable; production design pins versions per case revision (proposed). |
