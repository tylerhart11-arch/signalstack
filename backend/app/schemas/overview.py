from datetime import datetime

from pydantic import BaseModel, Field


class IndicatorOverview(BaseModel):
    code: str
    name: str
    category: str
    unit: str
    latest_value: float
    change: float
    change_pct: float | None = None
    trend_1m: float
    trend_1m_direction: str
    trend_3m: float
    trend_3m_direction: str
    interpretation: str
    last_updated: datetime
    sparkline: list[float] = Field(default_factory=list)
    source: str
    range_position_3m: float | None = None
    history_context: dict[str, float | str] = Field(default_factory=dict)


class OverviewSummary(BaseModel):
    risk_tone: str
    inflation_tone: str
    growth_tone: str
    rates_tone: str


class OverviewResponse(BaseModel):
    as_of: datetime
    summary: OverviewSummary
    indicators: list[IndicatorOverview]
