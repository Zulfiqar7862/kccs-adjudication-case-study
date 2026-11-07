"""Audit boundary stamps immutable case-version/episode facts, not mutable source truth."""


class AuditService:
    def __init__(self, store):
        self.store = store

    def record(self, case, action, **details):
        return self.store.append(
            case.tenant,
            case.case_id,
            {"action": action, "state": case.state.value, "version": case.version, "episode": case.episode, **details},
        )
