"""Independent historical fixed-hour replay; not a qualified legal calendar."""

import math
from datetime import timedelta

from adjudication.temporal.timezone import utc


def notification(event):
    if event.get("regulator_reportable") not in ("Y", "N"):
        return {
            "status": "UNKNOWN_REPORTABILITY",
            "calendar_qualified": False,
            "basis": "Escalate to Regulatory Affairs; missing flag is not permission to ignore",
        }
    if event.get("regulator_reportable") == "N":
        return {
            "status": "NOT_REPORTABLE_IN_EXTRACT",
            "basis": "Historical flag only; not an independent reportability decision",
        }
    window = event.get("reg_window_hours")
    if window is None:
        return {"status": "UNKNOWN_WINDOW", "calendar_qualified": False}
    if not math.isfinite(float(window)) or float(window) <= 0:
        raise ValueError("Positive notification window required")
    alert = utc(event["alert_ts_utc"])
    due = alert + timedelta(hours=float(window))
    elapsed = event.get("hours_to_notification")
    if elapsed is not None and (not math.isfinite(float(elapsed)) or float(elapsed) < 0):
        raise ValueError("Nonnegative notification elapsed time required")
    return {
        "status": "PENDING" if elapsed is None else ("WITHIN_WINDOW" if elapsed <= window else "LATE"),
        "alert_utc": alert.isoformat(),
        "due_utc": due.isoformat(),
        "notified_utc": (alert + timedelta(hours=elapsed)).isoformat() if elapsed is not None else None,
        "window_hours_from_extract": window,
        "calendar_qualified": False,
        "basis": "Historical fixed-hour replay only; no jurisdiction calendar is legally qualified",
    }
