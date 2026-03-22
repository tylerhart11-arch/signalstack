from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.thesis_engine import ThesisEngine
from app.models.saved_thesis import SavedThesis
from app.schemas.thesis import SavedThesisResponse, ThesisResult


class ThesisService:
    def __init__(self) -> None:
        self.engine = ThesisEngine()

    def analyze(self, text: str, save: bool, session: Session) -> ThesisResult:
        result = self.engine.analyze(text)
        if save:
            session.add(
                SavedThesis(
                    input_text=text,
                    interpreted_theme=result.interpreted_theme,
                    result=result.model_dump(),
                )
            )
            session.commit()
        return result

    def list_saved(self, session: Session, limit: int = 20) -> list[SavedThesisResponse]:
        items = session.execute(select(SavedThesis).order_by(SavedThesis.created_at.desc()).limit(limit)).scalars().all()
        return [
            SavedThesisResponse(
                id=item.id,
                input_text=item.input_text,
                interpreted_theme=item.interpreted_theme,
                result=ThesisResult(**item.result),
                created_at=item.created_at,
            )
            for item in items
        ]

    def save(self, text: str, session: Session) -> SavedThesisResponse:
        result = self.engine.analyze(text)
        item = SavedThesis(
            input_text=text,
            interpreted_theme=result.interpreted_theme,
            result=result.model_dump(),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return SavedThesisResponse(
            id=item.id,
            input_text=item.input_text,
            interpreted_theme=item.interpreted_theme,
            result=result,
            created_at=item.created_at,
        )
