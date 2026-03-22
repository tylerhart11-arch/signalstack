from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.thesis import SaveThesisRequest, SavedThesisResponse, ThesisAnalyzeRequest, ThesisResult
from app.services.thesis_service import ThesisService


router = APIRouter(prefix="/api/thesis")


@router.post("/analyze", response_model=ThesisResult)
def analyze_thesis(payload: ThesisAnalyzeRequest, session: Session = Depends(get_db)) -> ThesisResult:
    return ThesisService().analyze(text=payload.text, save=payload.save, session=session)


@router.get("/saved", response_model=list[SavedThesisResponse])
def list_saved_theses(session: Session = Depends(get_db)) -> list[SavedThesisResponse]:
    return ThesisService().list_saved(session=session)


@router.post("/saved", response_model=SavedThesisResponse)
def save_thesis(payload: SaveThesisRequest, session: Session = Depends(get_db)) -> SavedThesisResponse:
    return ThesisService().save(text=payload.text, session=session)
