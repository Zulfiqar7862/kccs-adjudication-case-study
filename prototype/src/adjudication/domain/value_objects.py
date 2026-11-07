"""Validated immutable values used in deterministic arithmetic."""

import math
from dataclasses import dataclass

from adjudication.temporal.timezone import utc


@dataclass(frozen=True)
class TemperatureInterval:
    lower: float
    upper: float

    def __post_init__(self):
        if not all(math.isfinite(x) for x in (self.lower, self.upper)) or self.lower > self.upper:
            raise ValueError("Finite, ordered temperature bounds required")


@dataclass(frozen=True)
class TimeWindow:
    start: str
    end: str | None = None

    def __post_init__(self):
        if self.end and utc(self.start) >= utc(self.end):
            raise ValueError("Positive half-open interval required")
        utc(self.start)

    def contains(self, instant):
        return utc(self.start) <= utc(instant) and (self.end is None or utc(instant) < utc(self.end))
