"""Explicit lifecycle transitions; timers are not state-machine transitions."""

from adjudication.domain.enums import CaseState as S
from adjudication.exceptions import TransitionError

ALLOWED = {
    S.RECEIVED: {S.TRIAGE},
    S.TRIAGE: {S.GATHERING, S.CLOSED_NON_ACTIONABLE},
    S.GATHERING: {S.WAITING, S.REVIEW_READY},
    S.WAITING: {S.GATHERING},
    S.REVIEW_READY: {S.SIGNING},
    S.SIGNING: {S.DISPOSED, S.GATHERING},
    S.DISPOSED: {S.REOPENED},
    S.CLOSED_NON_ACTIONABLE: {S.REOPENED},
    S.REOPENED: {S.GATHERING},
}


def transition(case, target, expected_version, basis_hash=None):
    target = S(target)
    if expected_version != case.version or target not in ALLOWED[case.state]:
        raise TransitionError("Stale version or illegal transition")
    if target in (S.DISPOSED, S.CLOSED_NON_ACTIONABLE) and not basis_hash:
        raise TransitionError("A frozen reviewed basis is required")
    case.state = target
    case.version += 1
    if target in (S.DISPOSED, S.CLOSED_NON_ACTIONABLE):
        case.prior_decisions.append({"episode": case.episode, "basis_hash": basis_hash, "state": target.value})
    return case
