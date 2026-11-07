"""In-memory case aggregate boundary with idempotent create and auditable commands."""

from adjudication.domain.models import Case
from adjudication.exceptions import TransitionError
from adjudication.workflow.reopen import reopen
from adjudication.workflow.state_machine import transition
from adjudication.workflow.waits import start_wait, wake


class CaseService:
    def __init__(self, audit):
        self.audit = audit
        self.cases = {}

    def create(self, tenant, case_id, due=None):
        key = (tenant, case_id)
        if key in self.cases:
            case = self.cases[key]
            if case.original_due != due:
                raise TransitionError("Conflicting idempotent create")
            return case
        case = Case(tenant, case_id, due)
        self.cases[key] = case
        self.audit.record(case, "CREATED")
        return case

    def move(self, case, target, expected_version, basis_hash=None):
        transition(case, target, expected_version, basis_hash)
        self.audit.record(case, "TRANSITION")
        return case

    def wait(self, case, kind, owner, wake_at, expected_version):
        start_wait(case, kind, owner, wake_at, expected_version)
        self.audit.record(case, "WAIT_STARTED", **case.wait)
        return case

    def wake(self, case, expected_version):
        wake(case, expected_version)
        self.audit.record(case, "WAIT_COMPLETED")
        return case

    def reopen(self, case, reason, expected_version):
        reopen(case, reason, expected_version)
        self.audit.record(case, "REOPENED", reason=reason)
        return case
