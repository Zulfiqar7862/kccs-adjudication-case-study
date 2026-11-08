"""Explain one alert's assessment in plain English.

Usage: python scripts/explain.py EVENT_ID [--db PATH] [--known-at ISO] [--corrections FILE]

This is a local convenience for someone reading their own database. It looks up
the alert's tenant and then calls the same tenant-scoped assessment the CLI and
API use, so nothing here bypasses the tenant check — it just saves typing it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototype" / "src"))

from sentinel.config import output_directory  # noqa: E402
from sentinel.evidence.assessment import AccessDenied, assess  # noqa: E402
from sentinel.workflow.service import Engine  # noqa: E402

READINESS = {
    "BLOCKED_BY_CONFLICTS": "BLOCKED — something in the evidence contradicts itself and a person must settle it first.",
    "INCOMPLETE_EVIDENCE": "INCOMPLETE — nothing contradicts, but required evidence is missing.",
    "EVIDENCE_ASSEMBLED": "ASSEMBLED — every required piece of evidence is present and consistent.",
}
STATUS = {
    "RESOLVED": "found", "RESOLVED_EXACT_TENANT_SCOPED": "found (exact match in this customer's own records)",
    "RESOLVED_MULTIPLE_SOURCE_RECORDS": "found, but several systems describe it differently",
    "CONFLICTING_SOURCE_RECORDS": "found, but the systems contradict each other",
    "AMBIGUOUS": "matches more than one record — cannot tell which",
    "AMBIGUOUS_PARENT_OR_SUBSIDIARY": "matches contracts with two different legal entities",
    "UNRESOLVED": "not found", "MISSING_REFERENCE": "not stated on the alert",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("event")
    parser.add_argument("--db", default=str(output_directory() / "private.db"))
    parser.add_argument("--known-at", help="Pretend it is this moment; anything recorded later is hidden")
    parser.add_argument("--corrections", help="JSON file of corrections to overlay")
    args = parser.parse_args()

    try:
        tables = Engine(Path(args.db)).tables()
    except Exception as error:  # noqa: BLE001 - surface the service's own message
        print(f"Could not open {args.db}: {error}\nImport a workbook first: ./run.sh pack /path/to/pack.xlsx")
        return 1
    event = next((e for e in tables["01_Excursion_Events"] if e["event_id"].casefold() == args.event.casefold()), None)
    if event is None:
        print(f"No alert called {args.event!r} in {args.db}.")
        return 1
    corrections = json.loads(Path(args.corrections).read_text(encoding="utf-8")) if args.corrections else None
    try:
        a = assess(tables, event["event_id"], principal_tenant=event["tenant_code"], known_at=args.known_at, corrections=corrections)
    except AccessDenied as denied:
        print(str(denied))
        return 1

    print(f"ALERT {a['event_id']}  (customer {a['tenant_code']})")
    print(f"  Product went out of range at: {a['time_semantics']['as_at'] or 'unknown'}")
    print(f"  Facts considered as known at:  {a['time_semantics']['known_at']}")
    if a["inputs"]["corrections_applied"]:
        print(f"  Corrections applied: {len(a['inputs']['corrections_applied'])}")
    print()
    print("WHAT WAS IDENTIFIED")
    for entity in a["entities"]:
        label = entity["kind"].replace("_", " ").lower()
        if entity.get("role"):
            label = f"{entity['role']} {label}"
        print(f"  - {label} '{entity.get('as_received', '')}': {STATUS.get(entity['status'], entity['status'])}")
        for alias in entity.get("unverified_alias_candidates", []):
            print(f"      (a reviewer once noted it may be '{alias['alias']}' — not verified, not used)")
    print()
    sop = a["evidence"]["sop"]
    print(f"PROCEDURE (SOP) IN FORCE AT THAT TIME: {len(sop['candidates'])} candidate(s)")
    for c in sop["candidates"]:
        flags = f"  [{'; '.join(c['flags'])}]" if c["flags"] else ""
        print(f"  - {c['doc_id']} {c['revision']} ({c['effective_from']} to {c['effective_to'] or 'open'}){flags}")
    for r in sop["rejected"]:
        print(f"  - set aside: {r['doc_id']} {r['revision']} — {r['reason']}")
    stab = a["evidence"]["stability"]
    print(f"STABILITY STUDY FOR THIS PRODUCT: {len(stab['candidates'])} candidate(s)")
    for c in stab["candidates"]:
        print(f"  - {c['study_ref']} ({c['study_type']}): {'usable' if c['usable'] else 'NOT usable'}{'  [' + '; '.join(c['flags']) + ']' if c['flags'] else ''}")
    for r in stab["rejected"]:
        print(f"  - {r['study_ref']}: {r['reason']}")
    tele = a["evidence"]["telemetry"]
    print("TEMPERATURE DATA")
    print(f"  - {tele['basis']}")
    for b in tele["bulletins"]:
        print(f"  - calibration bulletin {b['bulletin']}: {b.get('effect') or b.get('note')}")
    for f in tele["flags"]:
        print(f"  - {f}")
    print()
    if a["conflicts"]:
        print("CONFLICTS (block the case until a person settles them)")
        for c in a["conflicts"]:
            print(f"  ! {c}")
        print()
    print("MISSING (the workbook cannot supply these)")
    for m in a["missing_inputs"]:
        print(f"  - {m}")
    print()
    print("WHAT A PERSON MUST DO NEXT")
    for h in a["required_human_actions"]:
        print(f"  * {h}")
    print()
    n = a["notification"]
    print("REGULATOR CLOCK (runs separately from the decision)")
    print(f"  starts: {n['clock_starts_at']}   due: {n['due_at'] or 'n/a'}   status: {n['status']}")
    print(f"  signs the decision: {n['signatory_policy'] or 'unknown'}   regulator language: {n['regulator_output_language'] or 'unknown'}")
    print()
    print(f"RESULT: {READINESS.get(a['conclusion']['readiness'], a['conclusion']['readiness'])}")
    print("  Decision proposed by the software: NONE (it always abstains; a named human decides).")
    print(f"  Fingerprint of this assessment: {a['assessment_sha256'][:16]}…  (same inputs ⇒ same fingerprint)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
