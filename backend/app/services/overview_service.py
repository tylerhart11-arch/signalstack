from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import mean, pstdev

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.mappers.indicator_mapper import FEATURED_INDICATORS, INDICATOR_MAP, IndicatorDefinition
from app.models.indicator_snapshot import IndicatorSnapshot
from app.schemas.overview import IndicatorOverview, OverviewResponse, OverviewSummary
from app.utils.dates import coerce_utc_datetime


@dataclass
class SnapshotRecord:
    timestamp: datetime
    value: float


@dataclass
class IndicatorState:
    definition: IndicatorDefinition
    history: list[SnapshotRecord]
    source: str

    @property
    def latest_record(self) -> SnapshotRecord:
        return self.history[-1]

    @property
    def latest(self) -> float:
        return self.latest_record.value

    @property
    def last_updated(self) -> datetime:
        return self.latest_record.timestamp

    def _index_from_window(self, window: int) -> int:
        return max(0, len(self.history) - 1 - max(1, window))

    def value_at_window(self, window: int) -> float:
        return self.history[self._index_from_window(window)].value

    def delta(self, window: int) -> float:
        return self.latest - self.value_at_window(window)

    def delta_pct(self, window: int) -> float | None:
        base = self.value_at_window(window)
        if abs(base) < 1e-9:
            return None
        return ((self.latest / base) - 1.0) * 100

    def zscore(self, window: int = 5, pct: bool = False) -> float:
        if len(self.history) <= window + 5:
            return 0.0
        changes: list[float] = []
        for index in range(window, len(self.history)):
            current = self.history[index].value
            prior = self.history[index - window].value
            if pct:
                if abs(prior) < 1e-9:
                    continue
                changes.append(((current / prior) - 1.0) * 100)
            else:
                changes.append(current - prior)

        if len(changes) < 2:
            return 0.0

        latest = changes[-1]
        sigma = pstdev(changes)
        if sigma == 0:
            return 0.0
        return (latest - mean(changes)) / sigma

    def trailing_values(self, window: int) -> list[float]:
        return [point.value for point in self.history[-max(1, window) :]]

    def rolling_min(self, window: int) -> float:
        return min(self.trailing_values(window))

    def rolling_max(self, window: int) -> float:
        return max(self.trailing_values(window))

    def range_position(self, window: int) -> float | None:
        values = self.trailing_values(window)
        floor = min(values)
        ceiling = max(values)
        spread = ceiling - floor
        if spread == 0:
            return None
        return ((self.latest - floor) / spread) * 100


class OverviewService:
    def load_indicator_histories(self, session: Session, as_of: datetime | None = None) -> tuple[dict[str, list[SnapshotRecord]], dict[str, str]]:
        query = (
            select(IndicatorSnapshot)
            .where(IndicatorSnapshot.source.like("live%"))
            .order_by(IndicatorSnapshot.indicator_code, IndicatorSnapshot.timestamp)
        )
        if as_of is not None:
            query = query.where(IndicatorSnapshot.timestamp <= as_of)
        rows = session.execute(query).scalars().all()

        histories: dict[str, list[SnapshotRecord]] = {}
        sources: dict[str, str] = {}
        for row in rows:
            histories.setdefault(row.indicator_code, []).append(
                SnapshotRecord(timestamp=coerce_utc_datetime(row.timestamp), value=row.value)
            )
            sources[row.indicator_code] = row.source
        return histories, sources

    def build_indicator_states(self, session: Session, as_of: datetime | None = None) -> dict[str, IndicatorState]:
        histories, sources = self.load_indicator_histories(session=session, as_of=as_of)
        states: dict[str, IndicatorState] = {}
        for code, definition in INDICATOR_MAP.items():
            history = histories.get(code)
            if not history:
                continue
            states[code] = IndicatorState(definition=definition, history=history, source=sources.get(code, "unknown"))
        return states

    def build_overview(self, session: Session) -> OverviewResponse:
        states = self.build_indicator_states(session=session)
        if not states:
            raise ValueError("Live market data is not available yet.")

        indicators: list[IndicatorOverview] = []
        featured_states = [states[code] for code in FEATURED_INDICATORS if code in states]
        if not featured_states:
            raise ValueError("Featured live indicators are not available yet.")
        as_of = max(state.last_updated for state in featured_states)

        for state in featured_states:
            change = state.delta(state.definition.change_window)
            change_pct = state.delta_pct(state.definition.change_window)
            trend_1m = self._metric_for_state(state, state.definition.trend_1m_window)
            trend_3m = self._metric_for_state(state, state.definition.trend_3m_window)
            trend_1m_direction = self._direction_from_metric(state.definition, trend_1m)
            trend_3m_direction = self._direction_from_metric(state.definition, trend_3m)
            range_position_3m = state.range_position(state.definition.trend_3m_window)
            history_context = self._history_context(state)

            indicators.append(
                IndicatorOverview(
                    code=state.definition.code,
                    name=state.definition.name,
                    category=state.definition.category,
                    unit=state.definition.unit,
                    latest_value=round(state.latest, state.definition.display_precision),
                    change=round(change, state.definition.display_precision),
                    change_pct=round(change_pct, 2) if change_pct is not None else None,
                    trend_1m=round(trend_1m, 2),
                    trend_1m_direction=trend_1m_direction,
                    trend_3m=round(trend_3m, 2),
                    trend_3m_direction=trend_3m_direction,
                    interpretation=self._interpret_indicator(state),
                    last_updated=state.last_updated,
                    sparkline=[round(point.value, state.definition.display_precision) for point in state.history[-state.definition.sparkline_points :]],
                    source=state.source,
                    range_position_3m=round(range_position_3m, 1) if range_position_3m is not None else None,
                    history_context=history_context,
                )
            )

        summary = OverviewSummary(
            risk_tone=self._risk_tone(states),
            inflation_tone=self._inflation_tone(states),
            growth_tone=self._growth_tone(states),
            rates_tone=self._rates_tone(states),
        )

        return OverviewResponse(as_of=as_of, summary=summary, indicators=indicators)

    def _metric_for_state(self, state: IndicatorState, window: int) -> float:
        if state.definition.trend_metric == "absolute":
            value = state.delta(window)
            if state.definition.unit == "bps" and state.definition.code == "s2s10s":
                return value
            if state.definition.unit == "%":
                return value * (100 if state.definition.code in {"us2y", "us10y", "hy_spread", "ig_spread", "fed_funds_rate"} else 1)
            return value
        value = state.delta_pct(window)
        return value or 0.0

    def _direction_from_metric(self, definition: IndicatorDefinition, metric: float) -> str:
        if metric > definition.direction_threshold:
            return "rising"
        if metric < -definition.direction_threshold:
            return "falling"
        return "flat"

    def _interpret_indicator(self, state: IndicatorState) -> str:
        code = state.definition.code
        trend_1m = self._metric_for_state(state, state.definition.trend_1m_window)
        trend_3m = self._metric_for_state(state, state.definition.trend_3m_window)
        trend_1m_direction = self._direction_from_metric(state.definition, trend_1m)
        range_position = state.range_position(state.definition.trend_3m_window) or 50.0

        if code in {"sp500", "nasdaq100"}:
            if trend_1m_direction == "rising" and trend_3m > 5:
                return "uptrend intact"
            if trend_1m_direction == "falling" and range_position < 35:
                return "pullback pressure"
            return "leadership narrowing"
        if code == "russell2000":
            if trend_1m_direction == "rising" and range_position > 65:
                return "breadth improving"
            if trend_1m_direction == "falling":
                return "financing stress"
            return "breadth neutral"
        if code == "vix":
            if state.latest >= 24:
                return "stress bid"
            if state.latest <= 15 and trend_1m_direction != "rising":
                return "complacent"
            if trend_1m_direction == "rising":
                return "hedging demand"
            return "watchful"
        if code in {"us2y", "fed_funds_rate"}:
            if state.latest >= 4.5 and trend_1m_direction == "falling":
                return "restrictive but easing"
            if state.latest >= 4.5:
                return "restrictive hold"
            if trend_1m_direction == "falling":
                return "easing cycle"
            return "policy firm"
        if code == "us10y":
            if trend_1m_direction == "rising" and state.latest >= 4.4:
                return "term premium pressure"
            if trend_1m_direction == "falling":
                return "duration relief"
            return "rate range"
        if code == "s2s10s":
            if state.latest < 0 and trend_1m_direction == "rising":
                return "de-inverting"
            if state.latest < 0:
                return "deep inversion"
            return "normalizing"
        if code in {"hy_spread", "ig_spread"}:
            if trend_1m_direction == "rising" and range_position > 70:
                return "spread stress building"
            if trend_1m_direction == "falling" and range_position < 45:
                return "credit healing"
            return "credit caution"
        if code == "dxy":
            if trend_1m_direction == "rising" and state.latest >= 104:
                return "financial conditions tighter"
            if trend_1m_direction == "falling":
                return "conditions easing"
            return "dollar range"
        if code == "wti":
            if trend_1m_direction == "rising" and state.latest >= 80:
                return "energy shock risk"
            if trend_1m_direction == "rising":
                return "reflation bid"
            return "demand cooling"
        if code == "gold":
            return "macro hedge bid" if trend_1m_direction == "rising" else "hedge unwind"
        if code == "copper":
            return "cyclical pulse" if trend_1m_direction == "rising" else "growth doubt"
        if code in {"cpi_yoy", "core_cpi_yoy"}:
            if trend_1m_direction == "falling" and state.latest > 3:
                return "disinflation intact"
            if trend_1m_direction == "falling":
                return "cooling toward target"
            if state.latest > 3:
                return "sticky inflation"
            return "re-acceleration risk"
        if code == "unemployment_rate":
            if trend_1m_direction == "rising" and state.latest >= 4.2:
                return "slack building"
            if trend_1m_direction == "rising":
                return "labor softening"
            return "labor resilient"
        return "stable"

    def _history_context(self, state: IndicatorState) -> dict[str, float | str]:
        lookback = state.definition.trend_3m_window
        context: dict[str, float | str] = {
            "three_month_low": round(state.rolling_min(lookback), state.definition.display_precision),
            "three_month_high": round(state.rolling_max(lookback), state.definition.display_precision),
            "move_zscore": round(state.zscore(state.definition.change_window, pct=state.definition.trend_metric == "pct"), 2),
        }
        range_position = state.range_position(lookback)
        if range_position is not None:
            context["range_position_3m"] = round(range_position, 1)
        return context

    def _risk_tone(self, states: dict[str, IndicatorState]) -> str:
        if not all(code in states for code in ("sp500", "russell2000", "vix")):
            return "insufficient live data"
        sp = states["sp500"].delta_pct(21) or 0.0
        russell = states["russell2000"].delta_pct(21) or 0.0
        vix = states["vix"].delta_pct(21) or 0.0
        if sp > 2 and russell > 0.5 and vix < 0:
            return "broad risk-on"
        if sp > 2 and russell < 0:
            return "constructive but narrow"
        if sp < -2 or vix > 15:
            return "fragile risk"
        return "mixed"

    def _inflation_tone(self, states: dict[str, IndicatorState]) -> str:
        if not all(code in states for code in ("cpi_yoy", "core_cpi_yoy")):
            return "insufficient live data"
        cpi = states["cpi_yoy"].delta(1)
        core = states["core_cpi_yoy"].delta(1)
        if cpi < 0 and core < 0:
            return "disinflation intact"
        if cpi > 0.08 or core > 0.06:
            return "re-acceleration risk"
        return "sticky but stable"

    def _growth_tone(self, states: dict[str, IndicatorState]) -> str:
        if not all(code in states for code in ("copper", "russell2000", "unemployment_rate")):
            return "insufficient live data"
        copper = states["copper"].delta_pct(21) or 0.0
        small_caps = states["russell2000"].delta_pct(21) or 0.0
        unemployment = states["unemployment_rate"].delta(1)
        if copper > 2 and small_caps > 1 and unemployment <= 0:
            return "reaccelerating"
        if unemployment > 0.1 or small_caps < -2:
            return "late-cycle softening"
        return "stable"

    def _rates_tone(self, states: dict[str, IndicatorState]) -> str:
        if not all(code in states for code in ("us2y", "s2s10s")):
            return "insufficient live data"
        two_year = states["us2y"].delta(21)
        slope = states["s2s10s"].delta(21)
        if two_year < 0 and slope > 0:
            return "easing with steepening"
        if two_year > 0 and slope < 0:
            return "tightening bias"
        return "range-bound"
