import hashlib
import json
from pathlib import Path

import pytest
from adjudication.cli import run
from adjudication.ingestion.workbook_loader import Pack

BOOK = Path(__file__).resolve().parents[3] / "data/KCCS_Sentinel_Reference_Data_Pack.xlsx"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not BOOK.exists(), reason="Private workbook is local-only; copy it into data/ to enable integration tests"
    ),
]


def test_real_workbook_full_flow_and_reproducibility(tmp_path):
    before = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    report = run(BOOK, tmp_path / "one")
    run(BOOK, tmp_path / "two")
    summary = report["summary"]
    assert summary["events"] == 420 and summary["sheet_count"] == 15
    assert summary["notification_statuses"] == {"LATE": 14, "NOT_REPORTABLE_IN_EXTRACT": 392, "WITHIN_WINDOW": 14}
    assert summary["product_match_statuses"] == {"EXACT_SOURCE_MATCH": 297, "UNVERIFIED_ALIAS": 72, "MISSING": 51}
    assert summary["auto_closures_proposed"] == 0
    for p in (tmp_path / "one").iterdir():
        assert p.read_bytes() == (tmp_path / "two" / p.name).read_bytes()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == before
    assert json.loads((tmp_path / "one/run_manifest.json").read_text())["input_sha256"] == before


def test_every_source_sheet_and_cell_is_inventoried():
    pack = Pack(BOOK)
    assert len(pack.inventory) == 15 and len(pack.events) == 420
    assert pack.audit()["sheet_count"] == 15
    assert all(v["columns"] > 0 and v["rows_including_header"] > 0 for v in pack.inventory.values())
    assert len(pack.cells) == 15
