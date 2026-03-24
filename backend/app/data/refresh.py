from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import Base, SessionLocal, engine
from app.data.mappers.indicator_mapper import INDICATOR_DEFINITIONS, INDICATOR_MAP
from app.data.providers.demo_provider import SeriesPoint, generate_demo_history
from app.data.providers.fred_provider import FredProvider
from app.data.providers.market_provider import MarketProvider
from app.engines.anomaly_engine import AnomalyContext, AnomalyEngine
from app.engines.regime_engine import RegimeEngine
from app.engines.thesis_engine import ThesisEngine
from app.models.anomaly_item import AnomalyItem
from app.models.indicator_snapshot import IndicatorSnapshot
from app.models.regime_history import RegimeHistory
from app.models.saved_thesis import SavedThesis
from app.services.overview_service import OverviewService
from app.utils.dates import coerce_utc_datetime, utc_now


class DataRefreshService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.fred_provider = FredProvider(settings.fred_api_key)
        self.market_provider = MarketProvider()

    def refresh(self, session: Session, as_of: date | datetime | None = None) -> str:
        effective_date = as_of or utc_now()
        demo_history = generate_demo_history(effective_date, periods=self.settings.market_lookback_days)

        if self.settings.use_demo_data:
            history = demo_history
            sources = self._build_demo_source_map(history)
            source_summary = "demo"
        else:
            history, sources = self._load_blended_history(effective_date=effective_date, demo_history=demo_history)
            live_count = sum(1 for source in sources.values() if source.startswith("live"))
            fallback_count = sum(1 for source in sources.values() if "fallback" in source)
            source_summary = "mixed-live" if live_count and fallback_count else "live" if live_count else "demo-fallback"

        session.execute(delete(IndicatorSnapshot))
        session.flush()

        for code, points in history.items():
            definition = INDICATOR_MAP[code]
            for point in points:
                session.add(
                    IndicatorSnapshot(
                        indicator_code=code,
                        timestamp=point.timestamp,
                        value=point.value,
                        source=sources.get(code, source_summary),
                        meta={"unit": definition.unit, "name": definition.name},
                    )
                )

        session.commit()
        return source_summary

    def _build_demo_source_map(self, history: dict[str, list[SeriesPoint]]) -> dict[str, str]:
        return {
            code: "demo-derived" if INDICATOR_MAP[code].provider == "derived" else "demo"
            for code in history
            if code in INDICATOR_MAP
        }

    def _load_blended_history(
        self,
        effective_date: date | datetime,
        demo_history: dict[str, list[SeriesPoint]],
    ) -> tuple[dict[str, list[SeriesPoint]], dict[str, str]]:
        # Load every series independently so one flaky provider does not force the
        # whole app into demo mode.
        history = {code: list(points) for code, points in demo_history.items() if code in INDICATOR_MAP}
        sources = self._build_demo_source_map(history)

        for definition in INDICATOR_DEFINITIONS:
            if definition.provider == "derived":
                continue
            live_points = self._safe_fetch_live_series(definition.provider, definition.provider_id, definition.transform)
            if self._is_series_usable(definition.code, live_points, effective_date):
                history[definition.code] = live_points
                sources[definition.code] = f"live-{definition.provider}"
            else:
                history[definition.code] = list(demo_history[definition.code])
                sources[definition.code] = f"demo-fallback-{definition.provider}"

        self._build_derived_series(history, sources)
        return history, sources

    def _safe_fetch_live_series(self, provider: str, provider_id: str | None, transform: str | None) -> list[SeriesPoint]:
        if not provider_id:
            return []
        try:
            if provider == "yahoo":
                return [
                    SeriesPoint(timestamp=timestamp, value=value)
                    for timestamp, value in self.market_provider.fetch_history(provider_id)
                ]
            if provider == "fred":
                values = [
                    SeriesPoint(timestamp=timestamp, value=value)
                    for timestamp, value in self.fred_provider.fetch_series(provider_id)
                ]
                return self._transform_to_yoy(values) if transform == "yoy" else values
        except Exception:
            return []
        return []

    def _build_derived_series(self, history: dict[str, list[SeriesPoint]], sources: dict[str, str] | None = None) -> None:
        if "us2y" not in history or "us10y" not in history:
            return

        paired_length = min(len(history["us2y"]), len(history["us10y"]))
        if paired_length == 0:
            return

        history["s2s10s"] = [
            SeriesPoint(
                timestamp=history["us2y"][index].timestamp,
                value=round((history["us10y"][index].value - history["us2y"][index].value) * 100, 2),
            )
            for index in range(paired_length)
        ]

        if sources is not None:
            underlying_sources = [sources.get("us2y", "unknown"), sources.get("us10y", "unknown")]
            sources["s2s10s"] = "live-derived" if all(source.startswith("live") for source in underlying_sources) else "mixed-derived" if any(source.startswith("live") for source in underlying_sources) else "demo-derived"

    def _is_series_usable(self, code: str, series: list[SeriesPoint], effective_date: date | datetime) -> bool:
        if not series:
            return False

        clean_series = [point for point in series if point.value == point.value and point.value not in {float("inf"), float("-inf")}]
        if len(clean_series) != len(series):
            series[:] = clean_series
        if not series:
            return False

        minimum_points = 14 if code in {"cpi_yoy", "core_cpi_yoy", "unemployment_rate", "fed_funds_rate"} else 60
        if len(series) < minimum_points:
            return False

        effective_dt = coerce_utc_datetime(effective_date)
        latest_timestamp = series[-1].timestamp.astimezone(UTC)
        max_staleness_days = 45 if code in {"cpi_yoy", "core_cpi_yoy", "unemployment_rate", "fed_funds_rate"} else 10
        return (effective_dt.date() - latest_timestamp.date()).days <= max_staleness_days

    def _transform_to_yoy(self, series: list[SeriesPoint]) -> list[SeriesPoint]:
        if len(series) <= 12:
            return series
        transformed: list[SeriesPoint] = []
        for index in range(12, len(series)):
            current = series[index]
            prior = series[index - 12]
            if prior.value == 0:
                continue
            yoy = ((current.value / prior.value) - 1) * 100
            transformed.append(SeriesPoint(timestamp=current.timestamp, value=round(yoy, 4)))
        return transformed


def refresh_application_data(
    settings: Settings | None = None,
    as_of: date | datetime | None = None,
) -> str:
    active_settings = settings or get_settings()
    with SessionLocal() as session:
        source_summary = DataRefreshService(settings=active_settings).refresh(session=session, as_of=as_of)
        hydrate_derived_tables(session=session)
    return source_summary


def bootstrap_application() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()

    with SessionLocal() as session:
        has_data = session.scalar(select(func.count(IndicatorSnapshot.id))) or 0
        has_saved_theses = session.scalar(select(func.count(SavedThesis.id))) or 0

        if settings.refresh_on_startup or not has_data:
            DataRefreshService(settings=settings).refresh(session=session)
        hydrate_derived_tables(session=session)
        if not has_saved_theses:
            seed_demo_theses(session=session)


def hydrate_derived_tables(session: Session) -> None:
    overview_service = OverviewService()
    regime_engine = RegimeEngine()
    anomaly_engine = AnomalyEngine()

    # These tables are derived from the indicator snapshot history and are safe to
    # rebuild whenever fresh data is loaded.
    session.execute(delete(RegimeHistory))
    session.execute(delete(AnomalyItem))
    session.flush()

    states = overview_service.build_indicator_states(session=session)
    if not states:
        session.commit()
        return

    anchor_history = states["sp500"].history
    recent_window = anchor_history[-56:] if len(anchor_history) >= 56 else anchor_history
    anchor_dates = [record.timestamp for record in recent_window[::7]]
    if recent_window and recent_window[-1].timestamp not in anchor_dates:
        anchor_dates.append(recent_window[-1].timestamp)

    previous_regime: str | None = None
    for index, anchor_date in enumerate(anchor_dates):
        point_in_time_states = overview_service.build_indicator_states(session=session, as_of=anchor_date)
        if len(point_in_time_states) < 8:
            continue

        evaluation = regime_engine.evaluate(states=point_in_time_states, as_of=anchor_date, previous_regime=previous_regime)
        previous_regime = evaluation.regime
        session.add(
            RegimeHistory(
                as_of=evaluation.as_of,
                regime=evaluation.regime,
                confidence=evaluation.confidence,
                summary=evaluation.summary,
                drivers=[driver.model_dump() for driver in evaluation.drivers],
                supporting_indicators=evaluation.supporting_indicators,
            )
        )

        if index >= len(anchor_dates) - 5:
            for anomaly in anomaly_engine.evaluate(AnomalyContext(as_of=anchor_date, states=point_in_time_states)):
                session.add(
                    AnomalyItem(
                        detected_at=anomaly.detected_at,
                        rule_code=anomaly.rule_code,
                        title=anomaly.title,
                        explanation=anomaly.explanation,
                        category=anomaly.category,
                        severity=anomaly.severity,
                        related_assets=anomaly.related_assets,
                        supporting_metrics=anomaly.supporting_metrics,
                    )
                )

    session.commit()


def seed_demo_theses(session: Session) -> None:
    demo_texts = [
        "AI data centers will drive electricity demand higher",
        "Higher-for-longer rates will pressure small caps",
        "Home energy costs will continue rising",
        "Credit stress will appear before equities react",
    ]
    engine = ThesisEngine()
    for text in demo_texts:
        result = engine.analyze(text)
        session.add(
            SavedThesis(
                input_text=text,
                interpreted_theme=result.interpreted_theme,
                result=result.model_dump(),
            )
        )
    session.commit()
