from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.indicator_snapshot import IndicatorSnapshot


router = APIRouter()


@router.get("/health")
def health(session: Session = Depends(get_db)) -> dict[str, str | int]:
    session.execute(text("SELECT 1"))
    indicator_count = session.query(IndicatorSnapshot).count()
    return {
        "status": "ok",
        "database": "connected",
        "indicator_snapshots": indicator_count,
    }
