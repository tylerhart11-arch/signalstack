import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings
from app.data.scheduler import next_refresh_at, run_background_refresh_loop


def build_settings() -> Settings:
    return Settings.model_construct(
        app_name="SignalStack API",
        api_prefix="/api",
        frontend_origin="http://localhost:3000",
        database_url="sqlite:///memory",
        refresh_on_startup=True,
        background_refresh_enabled=True,
        refresh_interval_hours=1,
        exchange_calendar="XNYS",
        market_timezone="America/New_York",
        market_open_hour=9,
        market_open_minute=30,
        market_close_hour=16,
        market_close_minute=0,
        market_lookback_days=160,
        fred_api_key=None,
    )


def test_next_refresh_before_open_waits_for_same_day_open() -> None:
    next_run = next_refresh_at(datetime(2026, 3, 23, 12, 0, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 3, 23, 13, 30, tzinfo=UTC)


def test_next_refresh_during_session_uses_hourly_cadence() -> None:
    next_run = next_refresh_at(datetime(2026, 3, 23, 14, 45, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 3, 23, 15, 30, tzinfo=UTC)


def test_next_refresh_near_close_clamps_to_market_close() -> None:
    next_run = next_refresh_at(datetime(2026, 3, 23, 19, 45, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 3, 23, 20, 0, tzinfo=UTC)


def test_next_refresh_on_holiday_skips_to_next_session_open() -> None:
    next_run = next_refresh_at(datetime(2026, 7, 3, 15, 0, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 7, 6, 13, 30, tzinfo=UTC)


def test_next_refresh_on_early_close_day_uses_half_day_close() -> None:
    next_run = next_refresh_at(datetime(2026, 11, 27, 17, 45, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 11, 27, 18, 0, tzinfo=UTC)


def test_next_refresh_after_friday_close_skips_to_monday_open() -> None:
    next_run = next_refresh_at(datetime(2026, 3, 27, 21, 15, tzinfo=UTC), build_settings())
    assert next_run == datetime(2026, 3, 30, 13, 30, tzinfo=UTC)


def test_background_refresh_loop_waits_for_market_schedule_then_refreshes() -> None:
    settings = build_settings()
    sleep_calls: list[float] = []
    refresh_calls: list[datetime] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    def fake_refresh(active_settings: Settings) -> str:
        refresh_calls.append(datetime(2026, 3, 23, 15, 30, tzinfo=UTC))
        raise asyncio.CancelledError()

    def fake_now() -> datetime:
        return datetime(2026, 3, 23, 14, 45, tzinfo=UTC)

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(
            run_background_refresh_loop(
                settings=settings,
                sleep_fn=fake_sleep,
                refresh_fn=fake_refresh,
                now_fn=fake_now,
                use_thread=False,
            )
        )

    assert sleep_calls == [2700.0]
    assert refresh_calls == [datetime(2026, 3, 23, 15, 30, tzinfo=UTC)]
