from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.system import RefreshStatusResponse
from app.services.system_service import SystemService


router = APIRouter(prefix="/api/system")


@router.get("/refresh-status", response_model=RefreshStatusResponse)
def get_refresh_status(session: Session = Depends(get_db)) -> RefreshStatusResponse:
    return SystemService().get_refresh_status(session=session)
