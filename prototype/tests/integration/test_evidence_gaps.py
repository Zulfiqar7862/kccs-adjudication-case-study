from pathlib import Path

import pytest
from adjudication.ingestion.workbook_loader import Pack
from adjudication.reporting.report_builder import build_report

BOOK = Path(__file__).resolve().parents[3] / "data/KCCS_Sentinel_Reference_Data_Pack.xlsx"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not BOOK.exists(), reason="Private workbook is local-only; copy it into data/ to enable integration tests"
    ),
]


def test_real_evidence_gaps_and_tenant_isolation():
    report = build_report(Pack(BOOK))
    assert report["summary"]["issue_counts"]["WRONG_PRESENTATION"] == 42
    assert report["summary"]["issue_counts"]["SOP_OVERLAP"] == 78
    for c in report["cases"]:
        assert c["status"] == "NEEDS_EVIDENCE" and c["signed_disposition"] is None
        tenant = c["tenant_code"]
        assert all(p["tenant_code"] == tenant for p in c["product"]["candidates"])
        assert all(s["tenant_code"] == tenant for group in c["studies"] for s in group["candidates"])
        assert all(s["tenant_code"] == tenant for group in c["sop_candidates"] for s in group["candidates"])
