from datetime import datetime

from pydantic import BaseModel, Field


class ThesisAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=3)
    save: bool = False


class SaveThesisRequest(BaseModel):
    text: str = Field(..., min_length=3)


class ThemeSignal(BaseModel):
    name: str
    rationale: str


class ExposureIdea(BaseModel):
    name: str
    symbol: str | None = None
    stance: str
    rationale: str


class SectorIdea(BaseModel):
    name: str
    stance: str
    rationale: str


class ThesisResult(BaseModel):
    interpreted_theme: str
    confidence: float
    theme_family: str | None = None
    time_horizon: str | None = None
    expression_style: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)
    secondary_themes: list[str] = Field(default_factory=list)
    transmission_channels: list[ThemeSignal] = Field(default_factory=list)
    sectors: list[SectorIdea] = Field(default_factory=list)
    etf_exposures: list[ExposureIdea] = Field(default_factory=list)
    representative_stocks: list[ExposureIdea] = Field(default_factory=list)
    catalysts: list[ThemeSignal] = Field(default_factory=list)
    confirming_signals: list[ThemeSignal] = Field(default_factory=list)
    invalidation_signals: list[ThemeSignal] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SavedThesisResponse(BaseModel):
    id: int
    input_text: str
    interpreted_theme: str
    result: ThesisResult
    created_at: datetime
