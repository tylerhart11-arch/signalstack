from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SavedThesis(Base):
    __tablename__ = "saved_theses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    input_text: Mapped[str] = mapped_column(Text)
    interpreted_theme: Mapped[str] = mapped_column(String(255))
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
