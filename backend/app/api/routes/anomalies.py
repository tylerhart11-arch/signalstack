from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.refresh_guard import ensure_daily_refresh
from app.schemas.anomaly import AnomalyResponse
from app.services.anomaly_service import AnomalyService


router = APIRouter(prefix="/api")


@router.get("/anomalies", response_model=AnomalyResponse)
def get_anomalies(session: Session = Depends(get_db)) -> AnomalyResponse:
    ensure_daily_refresh(session=session)
    return AnomalyService().list_current(session=session)
