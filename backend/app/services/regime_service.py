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
        required_codes = {
            "cpi_yoy",
            "core_cpi_yoy",
            "unemployment_rate",
            "s2s10s",
            "hy_spread",
            "ig_spread",
            "sp500",
            "qqq",
            "russell2000",
            "vix",
            "copper",
            "wti",
            "gold",
            "dxy",
            "us2y",
            "us10y",
        }
        missing_codes = sorted(code for code in required_codes if code not in states)
        if missing_codes:
            raise ValueError(
                "Live regime inputs are not available yet. Missing: "
                + ", ".join(missing_codes[:6])
                + ("..." if len(missing_codes) > 6 else "")
            )
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
