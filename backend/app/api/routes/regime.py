from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.refresh_guard import ensure_daily_refresh
from app.schemas.regime import RegimeCurrentResponse, RegimeHistoryResponse
from app.services.regime_service import RegimeService


router = APIRouter(prefix="/api/regime")


@router.get("/current", response_model=RegimeCurrentResponse)
def get_current_regime(session: Session = Depends(get_db)) -> RegimeCurrentResponse:
    ensure_daily_refresh(session=session)
    try:
        return RegimeService().get_current(session=session)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/history", response_model=RegimeHistoryResponse)
def get_regime_history(session: Session = Depends(get_db)) -> RegimeHistoryResponse:
    ensure_daily_refresh(session=session)
    return RegimeService().get_history(session=session)
