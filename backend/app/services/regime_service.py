from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.regime_engine import RegimeEngine
from app.models.regime_history import RegimeHistory
from app.schemas.regime import RegimeCurrentResponse, RegimeHistoryEntry, RegimeHistoryResponse
from app.services.overview_service import OverviewService


class RegimeService:
    def __init__(self) -> None:
        self.overview_service = OverviewService()
        self.engine = RegimeEngine()

    def get_current(self, session: Session) -> RegimeCurrentResponse:
        history = session.execute(select(RegimeHistory).order_by(RegimeHistory.as_of.desc())).scalars().all()
        states = self.overview_service.build_indicator_states(session=session)
        previous_regime = history[1].regime if len(history) > 1 else None
        return self.engine.evaluate(
            states=states,
            as_of=max(state.last_updated for state in states.values()),
            previous_regime=previous_regime,
        )

    def get_history(self, session: Session, limit: int = 12) -> RegimeHistoryResponse:
        items = session.execute(select(RegimeHistory).order_by(RegimeHistory.as_of.desc()).limit(limit)).scalars().all()
        return RegimeHistoryResponse(
            items=[
                RegimeHistoryEntry(
                    as_of=item.as_of,
                    regime=item.regime,
                    confidence=item.confidence,
                    summary=item.summary,
                )
                for item in reversed(items)
            ]
        )
