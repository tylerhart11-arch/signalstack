from datetime import datetime

from pydantic import BaseModel, Field


class RegimeDriver(BaseModel):
    label: str
    detail: str
    weight: float


class RegimeCurrentResponse(BaseModel):
    as_of: datetime
    regime: str
    previous_regime: str | None = None
    confidence: float
    summary: str
    drivers: list[RegimeDriver] = Field(default_factory=list)
    supporting_indicators: dict[str, float] = Field(default_factory=dict)
    regime_scores: dict[str, float] = Field(default_factory=dict)
    pillar_scores: dict[str, float] = Field(default_factory=dict)


class RegimeHistoryEntry(BaseModel):
    as_of: datetime
    regime: str
    confidence: float
    summary: str


class RegimeHistoryResponse(BaseModel):
    items: list[RegimeHistoryEntry] = Field(default_factory=list)
