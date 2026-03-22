from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AnomalyItem(Base):
    __tablename__ = "anomaly_feed_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    rule_code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    explanation: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[int] = mapped_column(Integer)
    related_assets: Mapped[list] = mapped_column(JSON, default=list)
    supporting_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
