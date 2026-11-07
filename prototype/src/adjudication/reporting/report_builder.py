"""Aggregate counts have explicit denominators; clinical labels never become features."""

from collections import Counter

from adjudication.rules.engine import EvidenceKernel


def build_report(pack):
    kernel = EvidenceKernel(pack)
    cases = [kernel.evaluate(event) for event in pack.events]
    summary = {
        "events": len(cases),
        "sheet_count": len(pack.tables),
        "eligibility_statuses": dict(Counter(c["status"] for c in cases)),
        "product_match_statuses": dict(Counter(c["product"]["status"] for c in cases)),
        "notification_statuses": dict(Counter(c["notification"]["status"] for c in cases)),
        "issue_counts": dict(Counter(gap for c in cases for gap in c["issues"])),
        "auto_closures_proposed": sum(c["proposed_auto_close"] for c in cases),
    }
    return {"summary": summary, "cases": cases}
