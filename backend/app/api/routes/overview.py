from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.overview import OverviewResponse
from app.services.overview_service import OverviewService


router = APIRouter(prefix="/api")


@router.get("/overview", response_model=OverviewResponse)
def get_overview(session: Session = Depends(get_db)) -> OverviewResponse:
    service = OverviewService()
    return service.build_overview(session=session)
