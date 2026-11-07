"""Finite state vocabularies shared by workflow, recommendations and reporting."""

from enum import Enum


class CaseState(str, Enum):
    RECEIVED = "RECEIVED"
    TRIAGE = "TRIAGE"
    GATHERING = "GATHERING"
    WAITING = "WAITING"
    REVIEW_READY = "REVIEW_READY"
    SIGNING = "SIGNING"
    DISPOSED = "DISPOSED"
    CLOSED_NON_ACTIONABLE = "CLOSED_NON_ACTIONABLE"
    REOPENED = "REOPENED"


class Eligibility(str, Enum):
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"


class WaitType(str, Enum):
    LAB = "LAB"
    DOCUMENT = "DOCUMENT"
    TELEMETRY = "TELEMETRY"
    SIGNATORY = "SIGNATORY"
