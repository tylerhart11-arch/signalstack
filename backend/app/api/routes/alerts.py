from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.alerts import AlertConfigResponse, AlertConfigUpdate, AlertEventResponse, AlertHistoryResponse
from app.services.alert_service import AlertService


router = APIRouter(prefix="/api/alerts")


@router.get("/config", response_model=AlertConfigResponse)
def get_alert_config(session: Session = Depends(get_db)) -> AlertConfigResponse:
    return AlertService().get_config(session=session)


@router.put("/config", response_model=AlertConfigResponse)
def update_alert_config(payload: AlertConfigUpdate, session: Session = Depends(get_db)) -> AlertConfigResponse:
    return AlertService().update_config(session=session, payload=payload)


@router.get("/history", response_model=AlertHistoryResponse)
def get_alert_history(
    limit: int = Query(default=40, ge=1, le=100),
    session: Session = Depends(get_db),
) -> AlertHistoryResponse:
    return AlertService().list_history(session=session, limit=limit)


@router.post("/run-digest", response_model=AlertEventResponse)
def run_digest(session: Session = Depends(get_db)) -> AlertEventResponse:
    try:
        return AlertService().run_manual_digest(session=session)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
