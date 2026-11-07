"""Workflow aggregate and immutable evidence-dossier envelope."""

from dataclasses import asdict, dataclass, field

from adjudication.domain.enums import CaseState, Eligibility


@dataclass
class Case:
    tenant: str
    case_id: str
    original_due: str | None
    state: CaseState = CaseState.RECEIVED
    version: int = 0
    episode: int = 1
    prior_decisions: list = field(default_factory=list)
    wait: dict | None = None


@dataclass(frozen=True)
class Dossier:
    event_id: str
    tenant_code: str
    issues: list[str]
    status: Eligibility = Eligibility.NEEDS_EVIDENCE
    signed_disposition: str | None = None
    proposed_auto_close: bool = False

    def to_dict(self):
        return asdict(self)
