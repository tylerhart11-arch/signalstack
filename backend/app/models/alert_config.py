from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AlertConfig(Base):
    __tablename__ = "alert_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    regime_change_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    anomaly_severity_threshold: Mapped[int] = mapped_column(Integer, default=75)
    digest_cadence: Mapped[str] = mapped_column(String(32), default="market_close")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
