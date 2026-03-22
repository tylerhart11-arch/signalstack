from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RegimeHistory(Base):
    __tablename__ = "regime_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    regime: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(Text)
    drivers: Mapped[list] = mapped_column(JSON, default=list)
    supporting_indicators: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
