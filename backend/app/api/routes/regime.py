from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.regime import RegimeCurrentResponse, RegimeHistoryResponse
from app.services.regime_service import RegimeService


router = APIRouter(prefix="/api/regime")


@router.get("/current", response_model=RegimeCurrentResponse)
def get_current_regime(session: Session = Depends(get_db)) -> RegimeCurrentResponse:
    return RegimeService().get_current(session=session)


@router.get("/history", response_model=RegimeHistoryResponse)
def get_regime_history(session: Session = Depends(get_db)) -> RegimeHistoryResponse:
    return RegimeService().get_history(session=session)
