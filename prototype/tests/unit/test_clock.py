import pytest
from adjudication.domain.value_objects import TemperatureInterval, TimeWindow
from adjudication.rules.policies import temperature_interval
from adjudication.temporal.clock import notification
from adjudication.temporal.timezone import berlin, utc
from hypothesis import given
from hypothesis import strategies as st


@pytest.mark.parametrize(
    "elapsed,status", [(0, "WITHIN_WINDOW"), (72, "WITHIN_WINDOW"), (72.01, "LATE"), (None, "PENDING")]
)
def test_deadline_boundary(elapsed, status):
    value = notification(
        dict(regulator_reportable="Y", reg_window_hours=72, alert_ts_utc="2030-01-01", hours_to_notification=elapsed)
    )
    assert value["status"] == status
    assert value["calendar_qualified"] is False


@pytest.mark.parametrize(
    "flag,status", [(None, "UNKNOWN_REPORTABILITY"), ("?", "UNKNOWN_REPORTABILITY"), ("N", "NOT_REPORTABLE_IN_EXTRACT")]
)
def test_reportability_is_not_invented(flag, status):
    assert notification({"regulator_reportable": flag})["status"] == status


def test_unknown_window():
    assert notification({"regulator_reportable": "Y"})["status"] == "UNKNOWN_WINDOW"


@pytest.mark.parametrize("window", [0, -1, float("nan"), float("inf")])
def test_bad_window(window):
    with pytest.raises(ValueError):
        notification(dict(regulator_reportable="Y", reg_window_hours=window))


@pytest.mark.parametrize("elapsed", [-1, float("nan"), float("inf")])
def test_bad_elapsed(elapsed):
    with pytest.raises(ValueError):
        notification(
            dict(
                regulator_reportable="Y", reg_window_hours=72, alert_ts_utc="2030-01-01", hours_to_notification=elapsed
            )
        )


@given(st.integers(1, 1000), st.integers(0, 1000))
def test_disposition_wait_cannot_move_notification(hours, days):
    event = dict(regulator_reportable="Y", reg_window_hours=hours, alert_ts_utc="2030-01-01", days_to_disposition=days)
    original = notification(event)
    event["days_to_disposition"] += 1000
    assert notification(event) == original


@given(st.floats(-200, 100, allow_nan=False, allow_infinity=False))
def test_underreading_interval_never_lowers_value(value):
    lower, upper = temperature_interval(value, "TT-2.14.3")
    assert lower == value and upper >= lower
    assert upper == pytest.approx(value + 1.8, abs=1e-5)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_temperature(value):
    with pytest.raises(ValueError):
        temperature_interval(value, "SYN-FW")


def test_timezones_and_half_open_ranges():
    assert utc("2030-01-01T01:00:00+01:00") == utc("2030-01-01T00:00:00Z")
    assert berlin("2030-01-01").hour == 1
    window = TimeWindow("2030-01-01", "2030-02-01")
    assert window.contains("2030-01-01") and not window.contains("2030-02-01")
    assert TimeWindow("2030-01-01").contains("2031-01-01")
    with pytest.raises(ValueError):
        TimeWindow("2030-02-01", "2030-01-01")
    with pytest.raises(ValueError):
        TemperatureInterval(2, 1)
    with pytest.raises(ValueError):
        TemperatureInterval(0, float("nan"))
