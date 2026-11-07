"""Owned durable-shape wait records; the demonstration stores them in memory."""

from adjudication.domain.enums import CaseState, WaitType
from adjudication.temporal.timezone import utc
from adjudication.workflow.state_machine import transition


def start_wait(case, kind, owner, wake_at, expected_version):
    if not owner or not wake_at:
        raise ValueError("Named owner and wake time required")
    utc(wake_at)
    kind = WaitType(kind)
    transition(case, CaseState.WAITING, expected_version)
    case.wait = {"kind": kind.value, "owner": owner, "wake_at": wake_at}
    return case


def wake(case, expected_version):
    transition(case, CaseState.GATHERING, expected_version)
    case.wait = None
    return case
