from datetime import datetime

from pydantic import BaseModel, Field


class AnomalyItemResponse(BaseModel):
    id: int | None = None
    detected_at: datetime
    rule_code: str
    title: str
    explanation: str
    category: str
    severity: int
    related_assets: list[str] = Field(default_factory=list)
    supporting_metrics: dict[str, float | str] = Field(default_factory=dict)


class AnomalyResponse(BaseModel):
    as_of: datetime | None = None
    items: list[AnomalyItemResponse] = Field(default_factory=list)
