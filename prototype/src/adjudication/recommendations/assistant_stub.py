"""An optional drafting dependency is explicitly unavailable and makes no network calls."""

from adjudication.recommendations.deterministic import recommend


class AssistantStub:
    available = False

    def draft(self, dossier):
        return {"mode": "deterministic_fallback", **recommend(dossier["issues"])}
