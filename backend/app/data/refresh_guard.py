from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.data.refresh import refresh_application_data
from app.models.refresh_run import RefreshRun
from app.utils.dates import utc_now


def _latest_successful_refresh(session: Session) -> RefreshRun | None:
    return session.execute(
        select(RefreshRun)
        .where(RefreshRun.status == "success")
        .order_by(RefreshRun.completed_at.desc(), RefreshRun.id.desc())
    ).scalars().first()


def ensure_daily_refresh(session: Session, settings: Settings | None = None, *, now: datetime | None = None) -> None:
    active_settings = settings or get_settings()
    market_tz = ZoneInfo(active_settings.market_timezone)
    reference_now = now or utc_now()
    latest_success = _latest_successful_refresh(session)

    if latest_success is None or latest_success.completed_at is None:
        refresh_application_data(settings=active_settings)
        return

    last_completed_local_date = latest_success.completed_at.astimezone(market_tz).date()
    current_local_date = reference_now.astimezone(market_tz).date()
    if last_completed_local_date < current_local_date:
        refresh_application_data(settings=active_settings)
