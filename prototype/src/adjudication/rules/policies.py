"""Conservative measurement uncertainty, never an assumed exact calibration correction."""

import math

from adjudication.domain.value_objects import TemperatureInterval


def temperature_interval(value, firmware):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("Temperature must be finite")
    interval = TemperatureInterval(x, round(x + 1.8, 6) if firmware == "TT-2.14.3" else x)
    return [interval.lower, interval.upper]
