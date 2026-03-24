from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from app.core.config import Settings, get_settings
from app.data.refresh import refresh_application_data
from app.utils.dates import utc_now

try:
    import exchange_calendars as xcals
except ImportError:  # pragma: no cover - exercised through manual fallback
    xcals = None


logger = logging.getLogger(__name__)

SleepFn = Callable[[float], Awaitable[None]]
RefreshFn = Callable[[Settings], str]
NowFn = Callable[[], datetime]


def refresh_interval_seconds(settings: Settings) -> float:
    return float(settings.refresh_interval_hours * 60 * 60)


def _coerce_utc_datetime(value: datetime) -> datetime:
    return value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)


def _exchange_calendar_name(settings: Settings) -> str | None:
    value = (settings.exchange_calendar or "").strip()
    return value or None


@lru_cache(maxsize=8)
def _load_exchange_calendar(name: str):
    if xcals is None:
        raise RuntimeError("exchange_calendars is not installed.")
    return xcals.get_calendar(name)


def _market_timezone(settings: Settings) -> ZoneInfo:
    return ZoneInfo(settings.market_timezone)


def _market_open_time(settings: Settings) -> time:
    return time(hour=settings.market_open_hour, minute=settings.market_open_minute)


def _market_close_time(settings: Settings) -> time:
    return time(hour=settings.market_close_hour, minute=settings.market_close_minute)


def _is_trading_day(value: date) -> bool:
    return value.weekday() < 5


def _next_trading_day(value: date) -> date:
    candidate = value
    while not _is_trading_day(candidate):
        candidate += timedelta(days=1)
    return candidate


def _next_session_start(reference_utc: datetime, settings: Settings) -> datetime | None:
    calendar_name = _exchange_calendar_name(settings)
    if not calendar_name:
        return None

    calendar = _load_exchange_calendar(calendar_name)
    session = calendar.date_to_session(reference_utc.date(), direction="next")
    session_open = calendar.session_open(session).to_pydatetime().astimezone(UTC)
    session_close = calendar.session_close(session).to_pydatetime().astimezone(UTC)
    if reference_utc >= session_close:
        session = calendar.next_session(session)
        session_open = calendar.session_open(session).to_pydatetime().astimezone(UTC)
    return session_open


def _session_window(reference_utc: datetime, settings: Settings) -> tuple[datetime, datetime] | None:
    calendar_name = _exchange_calendar_name(settings)
    if not calendar_name:
        return None

    calendar = _load_exchange_calendar(calendar_name)
    session = calendar.date_to_session(reference_utc.date(), direction="next")
    session_open = calendar.session_open(session).to_pydatetime().astimezone(UTC)
    session_close = calendar.session_close(session).to_pydatetime().astimezone(UTC)
    if reference_utc >= session_close:
        session = calendar.next_session(session)
        session_open = calendar.session_open(session).to_pydatetime().astimezone(UTC)
        session_close = calendar.session_close(session).to_pydatetime().astimezone(UTC)
    return session_open, session_close


def _fallback_next_refresh_at(reference_utc: datetime, settings: Settings) -> datetime:
    market_tz = _market_timezone(settings)
    local_now = reference_utc.astimezone(market_tz)
    market_open_time = _market_open_time(settings)
    market_close_time = _market_close_time(settings)
    cadence = timedelta(seconds=refresh_interval_seconds(settings))

    def session_bounds(session_date: date) -> tuple[datetime, datetime]:
        return (
            datetime.combine(session_date, market_open_time, tzinfo=market_tz),
            datetime.combine(session_date, market_close_time, tzinfo=market_tz),
        )

    current_date = local_now.date()
    if not _is_trading_day(current_date):
        next_open, _ = session_bounds(_next_trading_day(current_date + timedelta(days=1)))
        return next_open.astimezone(UTC)

    session_open, session_close = session_bounds(current_date)
    if local_now < session_open:
        return session_open.astimezone(UTC)
    if local_now >= session_close:
        next_open, _ = session_bounds(_next_trading_day(current_date + timedelta(days=1)))
        return next_open.astimezone(UTC)

    elapsed = local_now - session_open
    intervals_elapsed = int(elapsed.total_seconds() // cadence.total_seconds()) + 1
    next_run = session_open + (cadence * intervals_elapsed)
    if next_run > session_close:
        next_run = session_close
    if next_run <= local_now:
        next_open, _ = session_bounds(_next_trading_day(current_date + timedelta(days=1)))
        return next_open.astimezone(UTC)
    return next_run.astimezone(UTC)


def next_refresh_at(now: datetime, settings: Settings) -> datetime:
    reference_utc = _coerce_utc_datetime(now)
    cadence = timedelta(seconds=refresh_interval_seconds(settings))
    session_window = _session_window(reference_utc, settings)

    if session_window is None:
        return _fallback_next_refresh_at(reference_utc, settings)

    session_open, session_close = session_window
    if reference_utc < session_open:
        return session_open
    if reference_utc >= session_close:
        next_session_open = _next_session_start(reference_utc, settings)
        return next_session_open if next_session_open is not None else _fallback_next_refresh_at(reference_utc, settings)

    elapsed = reference_utc - session_open
    intervals_elapsed = int(elapsed.total_seconds() // cadence.total_seconds()) + 1
    next_run = session_open + (cadence * intervals_elapsed)
    if next_run > session_close:
        next_run = session_close
    return next_run


def seconds_until_next_refresh(now: datetime, settings: Settings) -> float:
    next_run = next_refresh_at(now, settings)
    reference_utc = _coerce_utc_datetime(now)
    return max(0.0, (next_run - reference_utc).total_seconds())


async def run_background_refresh_loop(
    settings: Settings | None = None,
    *,
    sleep_fn: SleepFn = asyncio.sleep,
    refresh_fn: RefreshFn = refresh_application_data,
    now_fn: NowFn = utc_now,
    use_thread: bool = True,
) -> None:
    active_settings = settings or get_settings()
    schedule_label = _exchange_calendar_name(active_settings) or f"{active_settings.market_timezone} manual schedule"

    logger.info(
        "Background refresh loop enabled for %s with a %.0f-second cadence.",
        schedule_label,
        refresh_interval_seconds(active_settings),
    )

    while True:
        now = now_fn()
        next_run = next_refresh_at(now, active_settings)
        sleep_seconds = seconds_until_next_refresh(now, active_settings)
        logger.info("Next background refresh scheduled for %s.", next_run.isoformat())
        await sleep_fn(sleep_seconds)

        try:
            if use_thread:
                source_summary = await asyncio.to_thread(refresh_fn, active_settings)
            else:
                source_summary = refresh_fn(active_settings)
            logger.info("Background refresh completed using %s sources.", source_summary)
        except Exception:
            logger.exception("Background refresh failed.")
