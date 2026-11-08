"""Reproducible workbook inspection and data-quality report.

Reads a Sentinel reference pack with the prototype's hardened XLSX reader and
writes a JSON report plus a Markdown summary. Values stay as the original
strings (leading zeros, timestamps and identifiers are never coerced). Only
aggregates and identifiers are emitted; narrative text columns are not copied.

Usage: python scripts/inspect_workbook.py <workbook.xlsx> --output-dir artifacts/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototype" / "src"))

from sentinel.evidence.analysis import parse_time  # noqa: E402
from sentinel.ingestion.workbook import load, sha256  # noqa: E402

ISO_LIKE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?(Z|[+-]\d{2}:?\d{2})?$")
NUMBER_LIKE = re.compile(r"^-?\d+(\.\d+)?$")
NARRATIVE_HINTS = ("note", "text", "reason", "question", "comment", "description", "narrative", "readme")


def classify(values: list[str]) -> dict[str, int]:
    kinds: Counter[str] = Counter()
    for value in values:
        text = value.strip()
        if not text:
            kinds["blank"] += 1
        elif text.casefold() in {"unknown", "n/a", "na", "null", "none", "?"}:
            kinds["explicit_unknown"] += 1
        elif ISO_LIKE.match(text):
            kinds["timestamp_like"] += 1
        elif NUMBER_LIKE.match(text):
            kinds["number_like"] += 1
        else:
            kinds["text"] += 1
    return dict(kinds)


def profile_sheet(name: str, rows: list[dict]) -> dict:
    columns = [key for key in (rows[0].keys() if rows else []) if key != "_row"]
    profile = {"rows": len(rows), "first_row": rows[0]["_row"] if rows else None,
               "last_row": rows[-1]["_row"] if rows else None, "columns": {}}
    for column in columns:
        values = [str(row.get(column, "")) for row in rows]
        kinds = classify(values)
        distinct = len({value for value in values if value.strip()})
        leading_zero = sum(1 for value in values if re.match(r"^0\d+$", value.strip()))
        entry = {"kinds": kinds, "distinct_non_blank": distinct, "leading_zero_identifiers": leading_zero}
        if not any(hint in column.casefold() for hint in NARRATIVE_HINTS) and 0 < distinct <= 12:
            entry["values"] = dict(Counter(value.strip() for value in values if value.strip()))
        profile["columns"][column] = entry
    return profile


def norm(value) -> str:
    return str(value or "").strip().casefold()


def overlapping_sops(sops: list[dict]) -> list[dict]:
    """Return SOP rows whose effective windows overlap another revision of the same document."""
    by_doc: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in sops:
        by_doc[(norm(row.get("tenant_code")), norm(row.get("doc_id")))].append(row)
    findings = []
    for (tenant, doc), revisions in by_doc.items():
        if len(revisions) < 2:
            continue
        windows = []
        for row in revisions:
            try:
                start = parse_time(str(row.get("effective_from", "")))
            except (TypeError, ValueError):
                continue
            end_text = str(row.get("effective_to", "")).strip()
            try:
                end = parse_time(end_text) if end_text else None
            except (TypeError, ValueError):
                end = None
            windows.append((start, end, row))
        for i, (s1, e1, r1) in enumerate(windows):
            for s2, e2, r2 in windows[i + 1:]:
                if s1 <= s2 < (e1 or datetime.max.replace(tzinfo=timezone.utc)) or s2 <= s1 < (e2 or datetime.max.replace(tzinfo=timezone.utc)):
                    findings.append({"tenant_code": tenant.upper(), "doc_id": doc,
                                     "revisions": sorted([str(r1.get("revision")), str(r2.get("revision"))]),
                                     "rows": sorted([r1["_row"], r2["_row"]])})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("workbook")
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()

    path = Path(args.workbook)
    tables = load(path)
    report: dict = {
        "workbook_sha256": sha256(path),
        "inspected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sheets": {name: profile_sheet(name, rows) for name, rows in tables.items()},
        "findings": {},
    }
    f = report["findings"]

    events = tables.get("01_Excursion_Events", [])
    products = tables.get("02_Product_Master", [])
    facilities = tables.get("03_Facility_Registry", [])
    carriers = tables.get("04_Carrier_Master", [])
    sops = tables.get("05_SOP_Index", [])
    stability = tables.get("06_Stability_Index", [])
    aliases = tables.get("07_Alias_Observations", [])
    tenants = tables.get("12_Tenant_Constraints", [])

    # Tenant attribution: events whose tenant code is absent from the constraints sheet.
    constraint_tenants = {norm(row.get("tenant_code")) for row in tenants}
    event_tenants = Counter(norm(row.get("tenant_code")) for row in events)
    f["event_tenants"] = {tenant.upper(): count for tenant, count in sorted(event_tenants.items())}
    f["event_tenants_without_constraint_row"] = sorted(t.upper() for t in event_tenants if t and t not in constraint_tenants)
    f["events_without_tenant"] = [row.get("event_id") for row in events if not norm(row.get("tenant_code"))]

    # Identifier reuse across tenants (product, facility, carrier).
    def reuse(rows: list[dict], key: str) -> list[dict]:
        seen: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            value = norm(row.get(key))
            if value:
                seen[value].add(norm(row.get("tenant_code")).upper())
        return [{"value": value, "tenants": sorted(owners)} for value, owners in sorted(seen.items()) if len(owners) > 1]

    f["product_identifiers_shared_across_tenants"] = {
        key: reuse(products, key) for key in ("internal_sku", "gtin", "legacy_code", "brand_as_labelled")
        if products and key in products[0]
    }

    # Product resolution for every event using exact tenant-scoped identifier match only.
    id_fields = [k for k in ("brand_as_labelled", "internal_sku", "gtin", "legacy_code") if products and k in products[0]]
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in products:
        for field in id_fields:
            value = norm(row.get(field))
            if value:
                index[(norm(row.get("tenant_code")), value)].append(row)
    resolution = Counter()
    unresolved_examples: list[str] = []
    ambiguous_examples: list[str] = []
    for event in events:
        tenant = norm(event.get("tenant_code"))
        ref = norm(event.get("product_ref_as_received"))
        if not ref:
            resolution["missing_reference"] += 1
            continue
        matches = {id(r): r for r in index.get((tenant, ref), [])}
        if not matches:
            resolution["unresolved"] += 1
            if len(unresolved_examples) < 10:
                unresolved_examples.append(str(event.get("event_id")))
        elif len(matches) > 1:
            resolution["ambiguous"] += 1
            if len(ambiguous_examples) < 10:
                ambiguous_examples.append(str(event.get("event_id")))
        else:
            resolution["resolved"] += 1
    f["product_resolution_exact_tenant_scoped"] = dict(resolution)
    f["product_unresolved_examples"] = unresolved_examples
    f["product_ambiguous_examples"] = ambiguous_examples

    # Alias observations: how many are verified, and whether they are needed for unresolved events.
    if aliases:
        status_col = next((k for k in aliases[0] if "verif" in k.casefold() or "status" in k.casefold()), None)
        f["alias_observations"] = {"rows": len(aliases), "status_column": status_col,
                                   "statuses": dict(Counter(str(r.get(status_col, "")).strip() for r in aliases)) if status_col else {}}

    # SOP overlaps and date-only effective dates.
    f["sop_overlaps"] = overlapping_sops(sops)
    f["sop_effective_from_date_only"] = sum(1 for r in sops if re.match(r"^\d{4}-\d{2}-\d{2}$", str(r.get("effective_from", "")).strip()))
    f["sop_open_ended"] = sum(1 for r in sops if not str(r.get("effective_to", "")).strip())
    f["sop_site_specific"] = sum(1 for r in sops if "site" in norm(r.get("applies_to_facilities_text")))

    # Stability: ownership vs path, readability, presentation, coverage of product study refs.
    stab_by_ref: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in stability:
        stab_by_ref[(norm(row.get("tenant_code")), norm(row.get("study_ref")))].append(row)
    product_refs = Counter()
    for row in products:
        ref = norm(row.get("stability_study_ref"))
        if not ref:
            product_refs["product_without_study_ref"] += 1
        elif (norm(row.get("tenant_code")), ref) in stab_by_ref:
            product_refs["study_ref_found_same_tenant"] += 1
        elif any(key[1] == ref for key in stab_by_ref):
            product_refs["study_ref_found_only_under_other_tenant"] += 1
        else:
            product_refs["study_ref_absent_from_index"] += 1
    f["product_to_stability_coverage"] = dict(product_refs)
    path_col = next((k for k in (stability[0] if stability else {}) if "path" in k.casefold() or "folder" in k.casefold() or "location" in k.casefold()), None)
    if path_col:
        mismatched = []
        for row in stability:
            tenant = norm(row.get("tenant_code"))
            path_text = norm(row.get(path_col))
            owner_hint = tenant.split("-")[0] if tenant else ""
            if owner_hint and owner_hint not in path_text:
                mismatched.append({"study_ref": row.get("study_ref"), "tenant_code": row.get("tenant_code"), "row": row["_row"]})
        f["stability_path_does_not_mention_owner_tenant"] = {"column": path_col, "count": len(mismatched), "examples": mismatched[:10]}
    readable_col = next((k for k in (stability[0] if stability else {}) if "readab" in k.casefold()), None)
    if readable_col:
        f["stability_readability"] = dict(Counter(str(r.get(readable_col, "")).strip() for r in stability))

    # Telemetry and firmware.
    fw_col = next((k for k in (events[0] if events else {}) if "fw" in k.casefold() or "firmware" in k.casefold()), None)
    if fw_col:
        f["logger_firmware_builds"] = dict(Counter(str(r.get(fw_col, "")).strip() for r in events))
    for column in ("gateway_gap_min", "interpolated", "readings_in_window"):
        if events and column in events[0]:
            f[f"events_{column}"] = classify([str(r.get(column, "")) for r in events])

    # Timestamps: parseability and explicit timezone markers.
    ts_cols = [k for k in (events[0] if events else {}) if k.endswith("_utc")]
    ts: dict[str, dict] = {}
    for column in ts_cols:
        parsed = invalid = tz_marked = 0
        for row in events:
            text = str(row.get(column, "")).strip()
            if not text:
                continue
            try:
                parse_time(text)
                parsed += 1
                tz_marked += text.endswith("Z") or bool(re.search(r"[+-]\d{2}:?\d{2}$", text))
            except (TypeError, ValueError):
                invalid += 1
        ts[column] = {"parsed": parsed, "invalid": invalid, "explicit_timezone_marker": tz_marked}
    f["event_timestamps"] = ts
    tz_col = next((k for k in (facilities[0] if facilities else {}) if "tz" in k.casefold() or "timezone" in k.casefold()), None)
    if tz_col:
        f["facility_timezones"] = dict(Counter(str(r.get(tz_col, "")).strip() for r in facilities))
    f["carrier_rows"] = len(carriers)

    # Historical outcome columns that must never feed the prototype's assessment.
    outcome_hints = ("disposition", "recommend", "outcome", "override", "reopen", "notif", "triage", "closed")
    f["event_outcome_columns_excluded_from_assessment"] = [k for k in (events[0] if events else {}) if any(h in k.casefold() for h in outcome_hints)]

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "workbook-inspection.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Workbook inspection\n", f"- SHA-256: `{report['workbook_sha256']}`", f"- Inspected: {report['inspected_at']}\n",
             "| Sheet | Rows | Excel rows | Columns |", "|---|---:|---|---:|"]
    for name, profile in report["sheets"].items():
        lines.append(f"| `{name}` | {profile['rows']} | {profile['first_row']}–{profile['last_row']} | {len(profile['columns'])} |")
    lines += ["", "## Findings", "", "```json", json.dumps(f, indent=2, ensure_ascii=False), "```", ""]
    (out / "workbook-inspection.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"written": [str(out / "workbook-inspection.json"), str(out / "workbook-inspection.md")],
                      "sheets": len(tables), "events": len(events)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
