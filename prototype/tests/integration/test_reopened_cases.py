from pathlib import Path

import pytest
from adjudication.audit.audit_service import AuditService
from adjudication.audit.event_store import EventStore
from adjudication.domain.enums import CaseState as S
from adjudication.ingestion.workbook_loader import Pack
from adjudication.temporal.clock import notification
from adjudication.workflow.case_service import CaseService

BOOK = Path(__file__).resolve().parents[3] / "data/KCCS_Sentinel_Reference_Data_Pack.xlsx"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not BOOK.exists(), reason="Private workbook is local-only; copy it into data/ to enable integration tests"
    ),
]


def test_each_historical_reopen_preserves_duty_and_prior_episode():
    pack = Pack(BOOK)
    rows = [r for r in pack.events if r["reopened_later"] == "Y"]
    assert len(rows) == 61
    store = EventStore()
    svc = CaseService(AuditService(store))
    for row in rows:
        due = notification(row).get("due_utc")
        case = svc.create(row["tenant_code"], row["event_id"], due)
        svc.move(case, S.TRIAGE, 0)
        svc.move(case, S.CLOSED_NON_ACTIONABLE, 1, "test-only-simulated-basis")
        svc.reopen(case, "test-only historical reopen replay", 2)
        assert case.original_due == due and case.episode == 2 and len(case.prior_decisions) == 1
    assert store.verify()
    store.close()
