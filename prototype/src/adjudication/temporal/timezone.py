"""UTC comparison instants; date-only/naive input is an explicitly provisional UTC assumption."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def utc(value):
    instant = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return instant.replace(tzinfo=timezone.utc) if instant.tzinfo is None else instant.astimezone(timezone.utc)


def berlin(value):
    return utc(value).astimezone(ZoneInfo("Europe/Berlin"))
