import pytest
from adjudication.audit.audit_service import AuditService
from adjudication.audit.event_store import EventStore
from adjudication.domain.enums import CaseState as S
from adjudication.exceptions import TransitionError
from adjudication.workflow.case_service import CaseService


def service():
    store = EventStore()
    return CaseService(AuditService(store)), store


def test_wait_and_reopen_preserve_original_clock_and_signed_basis():
    svc, store = service()
    case = svc.create("SYN-A", "SYN-CASE", "2030-01-04")
    assert svc.create("SYN-A", "SYN-CASE", "2030-01-04") is case
    svc.move(case, S.TRIAGE, 0)
    svc.move(case, S.GATHERING, 1)
    svc.wait(case, "LAB", "synthetic-owner", "2030-01-10", 2)
    assert case.state == S.WAITING and case.original_due == "2030-01-04"
    svc.wake(case, 3)
    svc.move(case, S.REVIEW_READY, 4)
    svc.move(case, S.SIGNING, 5)
    svc.move(case, S.DISPOSED, 6, basis_hash="synthetic-reviewed-hash")
    original = list(case.prior_decisions)
    svc.reopen(case, "synthetic calibration notice months later", 7)
    assert case.episode == 2 and case.state == S.GATHERING
    assert case.prior_decisions == original and case.original_due == "2030-01-04"
    assert store.verify()
    store.close()


def test_reject_stale_illegal_and_unsigned_transitions():
    svc, store = service()
    case = svc.create("SYN-A", "SYN-C")
    with pytest.raises(TransitionError):
        svc.create("SYN-A", "SYN-C", "different")
    with pytest.raises(TransitionError):
        svc.move(case, S.TRIAGE, 99)
    with pytest.raises(TransitionError):
        svc.move(case, S.DISPOSED, 0)
    svc.move(case, S.TRIAGE, 0)
    with pytest.raises(TransitionError):
        svc.move(case, S.CLOSED_NON_ACTIONABLE, 1)
    svc.move(case, S.CLOSED_NON_ACTIONABLE, 1, "synthetic-closure-basis")
    with pytest.raises(ValueError):
        svc.reopen(case, " ", 2)
    svc.reopen(case, "new evidence", 2)
    with pytest.raises(ValueError):
        svc.wait(case, "LAB", "", "2030-01-10", case.version)
    with pytest.raises(ValueError):
        svc.wait(case, "LAB", "owner", "", case.version)
    with pytest.raises(ValueError):
        svc.wait(case, "INVALID", "owner", "2030-01-10", case.version)
    store.close()
