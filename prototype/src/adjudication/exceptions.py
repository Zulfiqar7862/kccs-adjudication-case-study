"""Explicit domain and input errors suitable for a CLI or API boundary."""


class AdjudicationError(ValueError):
    """Base error for a rejected domain operation."""


class DataContractError(AdjudicationError):
    """Input cannot be safely interpreted under the declared contract."""


class TransitionError(AdjudicationError):
    """Illegal lifecycle transition or stale aggregate version."""
