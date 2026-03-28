from datetime import datetime

from pydantic import BaseModel, Field


class StaleIndicatorResponse(BaseModel):
    code: str
    name: str
    last_updated: datetime
    age_days: int
    source: str
    max_staleness_days: int


class ProviderStatusResponse(BaseModel):
    provider: str
    status: str
    expected_count: int
    indicator_count: int
    live_count: int = 0
    stale_count: int = 0


class RefreshStatusResponse(BaseModel):
    mode: str
    status: str
    last_success_at: datetime | None = None
    latest_indicator_at: datetime | None = None
    source_summary: str
    next_scheduled_refresh: datetime
    stale_indicators: list[StaleIndicatorResponse] = Field(default_factory=list)
    provider_statuses: list[ProviderStatusResponse] = Field(default_factory=list)
    last_digest_at: datetime | None = None
    recent_alert_count: int = 0
