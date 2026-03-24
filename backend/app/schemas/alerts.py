from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


DigestCadence = Literal["manual", "market_open", "market_close", "both"]


class AlertConfigResponse(BaseModel):
    regime_change_enabled: bool
    anomaly_severity_threshold: int
    digest_cadence: DigestCadence
    updated_at: datetime | None = None


class AlertConfigUpdate(BaseModel):
    regime_change_enabled: bool
    anomaly_severity_threshold: int = Field(ge=0, le=100)
    digest_cadence: DigestCadence


class AlertEventResponse(BaseModel):
    id: int
    event_type: str
    title: str
    message: str
    severity: int | None = None
    cadence: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AlertHistoryResponse(BaseModel):
    items: list[AlertEventResponse] = Field(default_factory=list)
