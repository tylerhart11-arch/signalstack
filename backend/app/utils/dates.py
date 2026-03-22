from __future__ import annotations

from datetime import UTC, date, datetime, time


def utc_now() -> datetime:
    return datetime.now(UTC)


def coerce_utc_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.combine(value, time.min, tzinfo=UTC)
