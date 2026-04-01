from __future__ import annotations

from datetime import datetime
from threading import Lock
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.data.refresh import refresh_application_data
from app.models.refresh_run import RefreshRun
from app.utils.dates import utc_now


_daily_refresh_lock = Lock()


def _latest_successful_refresh(session: Session) -> RefreshRun | None:
    return session.execute(
        select(RefreshRun)
        .where(RefreshRun.status == "success")
        .order_by(RefreshRun.completed_at.desc(), RefreshRun.id.desc())
    ).scalars().first()


def _reset_session_state(session: Session) -> None:
    # The guard only runs on read routes, so clearing any open transaction is safe
    # and prevents SQLite readers from blocking the writer that performs the refresh.
    session.rollback()
    session.expire_all()


def _has_current_day_refresh(
    session: Session,
    *,
    settings: Settings,
    reference_now: datetime,
) -> bool:
    market_tz = ZoneInfo(settings.market_timezone)
    latest_success = _latest_successful_refresh(session)
    if latest_success is None or latest_success.completed_at is None:
        return False

    last_completed_local_date = latest_success.completed_at.astimezone(market_tz).date()
    current_local_date = reference_now.astimezone(market_tz).date()
    return last_completed_local_date >= current_local_date


def ensure_daily_refresh(session: Session, settings: Settings | None = None, *, now: datetime | None = None) -> None:
    active_settings = settings or get_settings()
    reference_now = now or utc_now()
    if _has_current_day_refresh(session=session, settings=active_settings, reference_now=reference_now):
        return

    _reset_session_state(session)
    with _daily_refresh_lock:
        if _has_current_day_refresh(session=session, settings=active_settings, reference_now=reference_now):
            return

        _reset_session_state(session)
        refresh_application_data(settings=active_settings)
        _reset_session_state(session)
