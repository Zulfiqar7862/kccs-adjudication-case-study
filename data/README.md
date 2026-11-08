# Public evaluation workbook

[Download `anonymized-evaluation.xlsx`](anonymized-evaluation.xlsx?raw=true). GitHub may show a download link rather than an Excel preview; open the downloaded file in Excel or LibreOffice.

## What reviewers receive

This is a **rebuilt anonymized derivative of the supplied workbook**, not the original and not the small fictional demo fixture. It retains all 15 sheet names, reviewed column names, per-sheet row counts and 420 event records. Open `00_README` first, then `01_Excursion_Events`, `02_Product_Master`, `05_SOP_Index`, `06_Stability_Index` and `12_Tenant_Constraints` to follow evidence relationships.

- Exact identifier values are replaced consistently with opaque `REF-` tokens, including references between events, products, studies and tenants. No original-to-public mapping is published.
- Names, addresses, contracts, narratives, reviewer notes and other unrestricted text are replaced with neutral redaction text. Narrative/compound references are not reconstructed.
- All recognized dates/times are mapped onto a synthetic hourly sequence beginning in 2020. Ordering is retained, but elapsed durations and calendar semantics are **not** preserved. Unparseable date descriptions are blanked.
- Numeric measurements and operating values are replaced with fixed illustrative values. Only approved categorical flags/dispositions are retained; unknown categories become `UNKNOWN`. Signatory descriptions become a synthetic dual-approval policy.
- The ZIP/XML package is built from scratch with plain inline text. It has no source metadata, comments, formulas, hidden sheets, external links, embedded objects or source hashes.

The derivative intentionally preserves structure, record counts, categorical distributions and some relationships. It is not a formal guarantee against re-identification by someone who already possesses the source. It is not valid for clinical accuracy, original cost calculations, legal deadlines, original outcome comparisons or source-document interpretation. References to original workbook row numbers in the design documents refer to the **private original**, not this rebuilt copy.

## Run it step by step

After [installation](../prototype/WALKTHROUGH.md#step-1--get-the-project-and-install-it), run from the repository root:

```sh
python -m sentinel --db prototype/output/evaluation.db import data/anonymized-evaluation.xlsx
python -m sentinel --db prototype/output/evaluation.db report --output prototype/output/evaluation-report.json
python scripts/check.py
```

**Scope:** importing this file does not answer the twelve reviewer questions. Alias observations, lane history, contracts and calibration-bulletin interpretation are not implemented evidence-resolution capabilities; the prototype exposes blockers for human review rather than solving those questions. A passing test proves structural workflow properties, not adjudication quality.

Expect 420 imported cases in `WAITING_EVIDENCE`, no automatic dispositions, and explicit evidence blockers. Repeating an identical import is replay-safe. Use a new database for any different workbook. The standard suite tests the committed evaluation workbook without private input. For the full case review/sign/reopen demonstration, use `python -m sentinel demo`; its evidence stubs are fictional and are not substituted into this workbook.

The original workbook is tested separately through `SENTINEL_WORKBOOK`; it is never silently replaced by this public copy. Keep original attachments and source-derived reports private. Other `.xlsx` and `.pdf` files remain ignored; only this reviewed evaluation file is allowlisted.

## Regeneration and review

Maintainers with authorized source access can run:

```sh
python scripts/build_anonymized_workbook.py /absolute/private/workbook.xlsx /temporary/evaluation.xlsx
```

The builder fails on unreviewed sheet/column changes and never copies free text or package parts. Inspect privacy, referential behavior and tests again before replacing the public artifact. Never commit the private source, a mapping table or original-source reports.
