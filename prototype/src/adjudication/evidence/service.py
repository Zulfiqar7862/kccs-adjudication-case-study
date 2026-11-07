"""Typed evidence lookup hazards; no clinical limits are parsed from indexes."""

import re

from adjudication.ingestion.normalizer import normalize as norm


def resolve_study(tables, product):
    tenant = product["tenant_code"]
    ref = product["stability_study_ref"]
    rows = (
        [x for x in tables.get("06_Stability_Index", []) if x["tenant_code"] == tenant and x["study_ref"] == ref]
        if ref
        else []
    )
    issues = []
    if not rows:
        return {"candidates": [], "issues": ["STUDY_NOT_INDEXED" if ref else "STUDY_REFERENCE_MISSING"]}
    for s in rows:
        if s["readable"] != "Y":
            issues.append("STUDY_UNREADABLE" if str(s["readable"]).startswith("N") else "STUDY_PARTIAL")
        if s["study_type"] != "Excursion / thermal cycling" or not s["permitted_excursion_text"]:
            issues.append("NO_USABLE_EXCURSION_LIMIT")
        ptext = norm(product["brand_as_labelled"])
        stext = norm(s["product_text_as_written"])
        if ("pfs" in ptext or "solojet" in ptext) and "vial" in stext:
            issues.append("WRONG_PRESENTATION")
        if "—" not in str(s["product_text_as_written"]) and not any(
            z in stext for z in ("vial", "pen", "syringe", "tabs", "sachet")
        ):
            issues.append("PRESENTATION_UNVERIFIED")
        paths = re.findall(r"T-[A-Z]+", str(s["file_path_text"]))
        if paths and any(t != tenant for t in paths):
            issues.append("OWNERSHIP_PATH_CONFLICT")
    if len(rows) > 1:
        issues.append("STUDY_AMBIGUOUS")
    return {"candidates": rows, "issues": sorted(set(issues))}
