# Risks, assumptions and open questions

## Positions on contradictory sources

- Narrative single-event allowance versus cumulative shelf-life language: do not choose by convenience. Obtain the approved presentation study and governing SOP annexure (brief §2; `02_Product_Master`, `06_Stability_Index`).
- Alert and excursion onset are distinct clocks; source narratives and queue timestamps do not fully reconcile. Use the explicit receipt-based notification rule while preserving conflicting source assertions (`00_README`).
- Overlapping revision validity does not prove supersession or applicability. Free-text scope and handwritten annotations need qualified stewardship (`05_SOP_Index`, `12_Tenant_Constraints`).
- Readability flags override allowance-looking index text. Long-term/accelerated studies do not automatically establish excursion permission (`06_Stability_Index`; README rule).
- A folder is not ownership authority; explicit tenant scope controls retrieval, and conflicting path metadata becomes a gap (`06_Stability_Index`).
- Clinical suitability, commercial liability and regulator notification are independent. Some override rationales conflate them; historical human choice is not automatically validated truth (`09_Override_Reasons`).
- “EU only” versus permission for some US API processing is legally ambiguous. Take the stricter geography until counsel defines the exception and derived-data treatment (`12_Tenant_Constraints`).

## Explicit assumptions and missing facts

Prototype naive/date-only timestamps use UTC midnight; production requires approved issuing/site timezone and inclusive/exclusive boundary semantics. Snapshot metadata cannot reconstruct transaction history. The exact document, batch, pallet, room occupancy and raw reading series are absent. Presentation checks are narrow lexical hazards, not a clinical classifier. Calibration is a bounded uncertainty interval; exact sensor correction and bulletin device/date scope need evidence.

Required clarifications: legal calendar timezone/holidays/cutoffs; products/markets triggering reports; who owns emergency filing; signatory/dual-approval authority and expiry; every unlisted tenant contract; approved document/annexure scope; historical correction records; legal holds/deletion conflicts; actual source peak rates; storage compression; provider regional/zero-retention terms; benchmark clinical outcomes independently approved by QA.

## Complete pack inventory

All sheets were read fully, including layout sheets. The loader retains all populated cells, original headers, formula/error locations, dimensions and row provenance. No source attachment or complete private-cell dump is public.

| Sheet | Public interpretation / caution |
|---|---|
| `00_README` | Sampling strata, known data defects and interpretation rules. Layout, not a normal table. |
| `01_Excursion_Events` | 43 columns: event/receipt/tenant/shipment/leg; source/logger/firmware; raw product/site/carrier names; mode; excursion bounds/duration; thermal summaries/spec/read-count/gaps/interpolation/dock flag; lane history/value; review/recommendation/disposition/override metrics; separate reportability/window/notification fields; reopen and notes. Historical labels are excluded from eligibility features. |
| `02_Product_Master` | ERP, tenant, brand/INN/SKU/GTIN/legacy, storage/MKT/excursion text, study reference, light sensitivity and update time. Update time is not recorded history. |
| `03_Facility_Registry` | Source IDs/names/codes, country/timezone, rooms/licence/BMS tags, creation and active status. No tenant/occupancy history and known timezone inconsistencies. |
| `04_Carrier_Contracts` | Legal entity/aliases/parent, effective interval, law, cold-chain/liability/cap/claim window and amendments. Product fitness is separate. |
| `05_SOP_Index` | Document/tenant/title/revision, effective interval, free-text supersession/site scope, format/pages/language and limit location. Metadata is not controlled bytes. |
| `06_Stability_Index` | Study/product/tenant/type/test temperatures/duration/outcome/allowance/path/pages/indexer/readability. Incomplete coverage, wrong presentation and ownership-path hazards. |
| `07_Alias_Observations` | Entity kind, two strings, sameness flag, frequencies, confirmer/date/comment. No adequate tenant/validity/authority contract. |
| `08_Reviewer_Queue_Log` | Case/reviewer/region/offset/local start/end, active time/systems/action/queue wait/interruptions/shift. Offset is reviewer-local, not facility timezone. |
| `09_Override_Reasons` | Case/reviewer, assistant suggestion, human choice and verbatim reason. Selected rationale population, not all overrides. No original rationale text is republished. |
| `10_Reviewer_Questions` | Twelve questions, current sources, typical minutes and frequency. Map to identity/reference, exposure, occupancy, contracts, authority, reportability, precedent and audit services. |
| `11_Systems_Inventory` | System/data/access/freshness/rate/ordering-backfill/availability/problems. One ingestion model cannot erase different delivery guarantees. |
| `12_Tenant_Constraints` | Tenant/region/volume/residency/API/signature/language/SOP ownership/other terms; eight examples plus an aggregate of 26. No-clause is not privacy permission. |
| `13_Volume_And_Cost` | Layout metrics plus price/input/output/region/retention/notice/latency table. Population denominators and inference/retrieval versus storage budgets differ. Personal compensation information is intentionally not reproduced. |
| `14_Incident_Log` | Reference/date/title/severity/event/consequence for six failure modes driving isolation, clocks, replay, retention and qualified changes. |

## Remaining prototype risks

In-memory workflow and local SQLite are not production durability or HA. Hash chains are not administrator-proof archives. A reviewed-basis string is not Part 11 authentication. No automatic notification or external source connector exists. Output is evidence eligibility, not disposition correctness, automation coverage or legal compliance certification.
