"""Select real workbook cases that exhibit specific failure modes, and write their evidence packages.

Cases are chosen programmatically from the imported snapshot (no event ids are
hard-coded). For each failure mode the first matching event in workbook order is
used. Also demonstrates knowledge-cutoff replay and a correction overlay that
yields a new assessment while leaving the original package untouched.

Usage: python scripts/select_demo_cases.py --db prototype/output/private.db --output-dir artifacts/private
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototype" / "src"))

from sentinel.evidence.assessment import assess, package, verify_package  # noqa: E402
from sentinel.workflow.service import Engine  # noqa: E402

MODES = {
    "firmware_bulletin": lambda a: any("bulletins" in a["evidence"]["telemetry"] and b.get("effect") for b in a["evidence"]["telemetry"]["bulletins"]),
    "stability_presentation_mismatch": lambda a: any("Presentation mismatch" in f for c in a["evidence"]["stability"]["candidates"] for f in c["flags"]),
    "sop_overlap_at_excursion": lambda a: bool(a["evidence"]["sop"]["conflicts"]),
    "unreadable_stability": lambda a: any("Readability" in f for c in a["evidence"]["stability"]["candidates"] for f in c["flags"]),
    "study_absent_from_index": lambda a: any("Not in the stability index" in r["reason"] for r in a["evidence"]["stability"]["rejected"]),
    "product_unresolved_with_alias_hint": lambda a: any(e["kind"] == "PRODUCT" and e["status"] == "UNRESOLVED" and e["unverified_alias_candidates"] for e in a["entities"]),
    "product_reference_missing": lambda a: any(e["kind"] == "PRODUCT" and e["status"] == "MISSING_REFERENCE" for e in a["entities"]),
    "untagged_bms_source": lambda a: a["evidence"]["telemetry"]["source_system"].upper() == "SYS-03",
    "carrier_parent_subsidiary_ambiguity": lambda a: any(e["kind"] == "CARRIER_CONTRACT" and e["status"] == "AMBIGUOUS_PARENT_OR_SUBSIDIARY" for e in a["entities"]),
    "sop_boundary_day": lambda a: any("date-only" in f for c in a["evidence"]["sop"]["candidates"] for f in c["flags"]) or bool(a["evidence"]["sop"]["rejected"]),
    "notification_window_recorded": lambda a: a["notification"]["due_at"] is not None,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    (out / "cases").mkdir(parents=True, exist_ok=True)
    tables = Engine(Path(args.db)).tables()

    selected: dict[str, str] = {}
    assessments: dict[str, dict] = {}
    for event in tables["01_Excursion_Events"]:
        if len(selected) == len(MODES):
            break
        result = assess(tables, event["event_id"])
        for mode, predicate in MODES.items():
            if mode not in selected and predicate(result):
                selected[mode] = result["event_id"]
                assessments[result["event_id"]] = result

    index = {"selection_rule": "first event in workbook order matching each failure mode", "cases": {}}
    for mode, event_id in selected.items():
        bundle = package(assessments[event_id])
        path = out / "cases" / f"{event_id}.json"
        path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        index["cases"][mode] = {"event_id": event_id, "tenant_code": bundle["tenant_code"], "package": str(path),
                               "package_sha256": bundle["package_sha256"], "readiness": bundle["assessment"]["conclusion"]["readiness"],
                               "conflicts": bundle["assessment"]["conflicts"]}
    index["unmatched_modes"] = sorted(set(MODES) - set(selected))

    # Knowledge-cutoff replay: the same firmware event assessed as known before the bulletin date.
    if "firmware_bulletin" in selected:
        event_id = selected["firmware_bulletin"]
        bulletin = assessments[event_id]["evidence"]["telemetry"]["bulletins"][0]
        before = assess(tables, event_id, known_at=bulletin["recorded_at"].replace("T00:00:00", "T00:00:00"))
        earlier = assess(tables, event_id, known_at="2026-01-01T00:00:00+00:00")
        index["knowledge_cutoff_replay"] = {
            "event_id": event_id, "bulletin": bulletin["bulletin"], "bulletin_recorded_at": bulletin["recorded_at"],
            "known_at_2026-01-01": {"bulletin_status": earlier["evidence"]["telemetry"]["bulletins"][0].get("status"),
                                    "conflicts": earlier["conflicts"], "assessment_sha256": earlier["assessment_sha256"]},
            "known_at_bulletin_date": {"conflicts": before["conflicts"], "assessment_sha256": before["assessment_sha256"]},
            "meaning": "The same alert yields different, separately hashed assessments depending on what was known; neither overwrites the other.",
        }

    # Correction overlay: fix the product master's study reference for the presentation-mismatch case.
    if "stability_presentation_mismatch" in selected:
        event_id = selected["stability_presentation_mismatch"]
        original = assessments[event_id]
        product = next(e for e in original["entities"] if e["kind"] == "PRODUCT")
        row = int(product["candidates"][0]["source_ref"].split("row=")[1])
        correction = [{"id": "demo-correction-1", "recorded_at": "2026-09-20T09:00:00+00:00", "sheet": "02_Product_Master", "row": row,
                       "field": "stability_study_ref", "value": "STB-UNKNOWN-PENDING-REGISTRATION",
                       "reason": "ERP reference pointed at a study for another presentation; replaced with a placeholder pending QA registration of the correct study",
                       "source": "demonstration fixture, not a real QA action"}]
        (out / "demo-correction.json").write_text(json.dumps(correction, indent=2) + "\n", encoding="utf-8")
        hidden = assess(tables, event_id, known_at="2026-09-14T00:00:00+00:00", corrections=correction)
        applied = assess(tables, event_id, known_at="2026-09-21T00:00:00+00:00", corrections=correction)
        original_path = out / "cases" / f"{event_id}.json"
        index["correction_replay"] = {
            "event_id": event_id, "correction_file": str(out / "demo-correction.json"),
            "original_assessment_sha256": original["assessment_sha256"],
            "known_at_before_correction_recorded": {"corrections_applied": hidden["inputs"]["corrections_applied"], "assessment_sha256": hidden["assessment_sha256"],
                                                    "same_as_original": hidden["assessment_sha256"] == original["assessment_sha256"] or
                                                    hidden["conflicts"] == original["conflicts"]},
            "known_at_after_correction_recorded": {"corrections_applied": applied["inputs"]["corrections_applied"], "assessment_sha256": applied["assessment_sha256"],
                                                   "conflicts": applied["conflicts"],
                                                   "stability_rejected": applied["evidence"]["stability"]["rejected"]},
            "original_package_still_verifies": verify_package(json.loads(original_path.read_text(encoding="utf-8"))),
        }

    (out / "demo-cases.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"written": str(out / "demo-cases.json"), "selected": selected, "unmatched_modes": index["unmatched_modes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
