"""Append a new episode months later without changing original duties or decisions."""

from adjudication.domain.enums import CaseState
from adjudication.workflow.state_machine import transition


def reopen(case, reason, expected_version):
    if not reason.strip():
        raise ValueError("Reopen reason required")
    transition(case, CaseState.REOPENED, expected_version)
    case.episode += 1
    return transition(case, CaseState.GATHERING, case.version)
