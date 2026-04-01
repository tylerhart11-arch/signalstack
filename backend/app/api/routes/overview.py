from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.refresh_guard import ensure_daily_refresh
from app.schemas.overview import OverviewResponse
from app.services.overview_service import OverviewService


router = APIRouter(prefix="/api")


@router.get("/overview", response_model=OverviewResponse)
def get_overview(session: Session = Depends(get_db)) -> OverviewResponse:
    ensure_daily_refresh(session=session)
    service = OverviewService()
    try:
        return service.build_overview(session=session)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
