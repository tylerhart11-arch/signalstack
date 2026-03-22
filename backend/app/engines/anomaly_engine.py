from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.schemas.anomaly import AnomalyItemResponse
from app.services.overview_service import IndicatorState
from app.utils.math_utils import clamp


def _scale(value: float, floor: float, span: float, cap: float = 3.0) -> float:
    if span <= 0:
        return 0.0
    return clamp((value - floor) / span, 0.0, cap)


def _abs_max(values: list[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


@dataclass
class AnomalyContext:
    as_of: datetime
    states: dict[str, IndicatorState]


class AnomalyEngine:
    def evaluate(self, context: AnomalyContext) -> list[AnomalyItemResponse]:
        rules = [
            self._equities_up_credit_worse,
            self._oil_up_energy_lagging,
            self._long_end_rising_despite_cooling_inflation,
            self._small_caps_lag_risk_sentiment,
            self._volatility_inconsistent_with_equities,
            self._sector_factor_divergence,
        ]

        anomalies: list[AnomalyItemResponse] = []
        for rule in rules:
            result = rule(context)
            if result is not None:
                anomalies.append(result)

        return sorted(
            anomalies,
            key=lambda item: (item.severity, item.detected_at.timestamp(), item.rule_code),
            reverse=True,
        )

    def _build_signal(
        self,
        context: AnomalyContext,
        *,
        rule_code: str,
        title: str,
        explanation: str,
        category: str,
        related_assets: list[str],
        importance: float,
        divergence: float,
        novelty: float,
        breadth: float,
        supporting_metrics: dict[str, float | str],
    ) -> AnomalyItemResponse:
        score = 26 + (importance * 12.0) + (divergence * 17.0) + (novelty * 10.0) + (breadth * 8.0)
        severity = int(round(clamp(score, 18.0, 99.0)))

        enriched_metrics = {
            **supporting_metrics,
            "rank_score": severity,
            "novelty_score": round(novelty, 2),
            "divergence_score": round(divergence, 2),
            "breadth_score": round(breadth, 2),
        }

        return AnomalyItemResponse(
            detected_at=context.as_of,
            rule_code=rule_code,
            title=title,
            explanation=explanation,
            category=category,
            severity=severity,
            related_assets=related_assets,
            supporting_metrics=enriched_metrics,
        )

    def _equities_up_credit_worse(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        sp = context.states["sp500"].delta_pct(5) or 0.0
        hy_change = context.states["hy_spread"].delta(5)
        ig_change = context.states["ig_spread"].delta(5)
        hy_z = context.states["hy_spread"].zscore(5)
        ig_z = context.states["ig_spread"].zscore(5)
        xlf_1m = context.states["xlf"].delta_pct(21) or 0.0

        if sp <= 0.7 or hy_change <= 0.06:
            return None

        divergence = _scale(sp, 0.5, 0.9) + _scale(hy_change, 0.05, 0.06)
        novelty = _scale(_abs_max([hy_z, ig_z]), 0.8, 0.7)
        breadth = 0.6 * float(ig_change > 0.02) + 0.5 * float(xlf_1m < 0) + 0.4 * float(context.states["vix"].latest >= 18)

        return self._build_signal(
            context,
            rule_code="equities_up_credit_worse",
            title="Equity tape is outrunning credit confirmation",
            explanation="Stocks are still pushing higher, but both high-yield and investment-grade spreads are leaking wider. That usually points to a rally led by index concentration rather than broad confidence in balance sheets.",
            category="Cross-asset divergence",
            related_assets=["S&P 500", "High Yield Spreads", "Investment Grade Spreads"],
            importance=3.2,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "sp500_5d_pct": round(sp, 2),
                "hy_spread_5d_change": round(hy_change, 2),
                "ig_spread_5d_change": round(ig_change, 2),
                "credit_move_zscore": round(_abs_max([hy_z, ig_z]), 2),
            },
        )

    def _oil_up_energy_lagging(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        oil = context.states["wti"].delta_pct(10) or 0.0
        xle = context.states["xle"].delta_pct(10) or 0.0
        sp = context.states["sp500"].delta_pct(10) or 0.0
        gap = oil - xle
        oil_z = context.states["wti"].zscore(10, pct=True)
        xle_z = context.states["xle"].zscore(10, pct=True)

        if oil <= 3.0 or gap <= 2.5:
            return None

        divergence = _scale(gap, 2.0, 1.8) + _scale(oil, 3.0, 2.5)
        novelty = _scale(_abs_max([oil_z, xle_z]), 0.8, 0.8)
        breadth = 0.5 * float(xle < sp) + 0.4 * float(context.states["copper"].delta_pct(10) >= 0) + 0.4 * float(context.states["gold"].delta_pct(10) > 0)

        return self._build_signal(
            context,
            rule_code="oil_up_energy_lagging",
            title="Crude strength is not transmitting cleanly into energy equities",
            explanation="WTI is lifting faster than energy stocks, which suggests the market is treating the oil move as transient, margin-unfriendly, or disconnected from durable earnings follow-through.",
            category="Commodity transmission",
            related_assets=["WTI", "XLE", "S&P 500"],
            importance=2.2,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "wti_10d_pct": round(oil, 2),
                "xle_10d_pct": round(xle, 2),
                "oil_equity_gap_pct": round(gap, 2),
                "oil_move_zscore": round(_abs_max([oil_z, xle_z]), 2),
            },
        )

    def _long_end_rising_despite_cooling_inflation(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        ten_year = context.states["us10y"].delta(21)
        two_year = context.states["us2y"].delta(21)
        cpi = context.states["cpi_yoy"].delta(1)
        core = context.states["core_cpi_yoy"].delta(1)
        gold = context.states["gold"].delta_pct(21) or 0.0
        ten_z = context.states["us10y"].zscore(21)

        if ten_year <= 0.06 or (cpi + core) >= -0.03:
            return None

        inflation_cooling = max(0.0, -(cpi + core))
        divergence = _scale(ten_year, 0.05, 0.05) + _scale(inflation_cooling, 0.03, 0.03)
        novelty = _scale(abs(ten_z), 0.8, 0.8)
        breadth = 0.5 * float(two_year <= 0.0) + 0.5 * float(gold > 0.0) + 0.4 * float(context.states["dxy"].delta_pct(21) <= 0.0)

        return self._build_signal(
            context,
            rule_code="long_end_rising_softer_inflation",
            title="Long-end yields are backing up even as inflation cools",
            explanation="That mix usually means the bond market is focused less on inflation relief and more on term premium, supply pressure, or a growth/fiscal story that keeps the long end heavy.",
            category="Rates inconsistency",
            related_assets=["US 10Y Treasury", "US 2Y Treasury", "CPI YoY"],
            importance=3.0,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "us10y_1m_change_pct_points": round(ten_year, 2),
                "us2y_1m_change_pct_points": round(two_year, 2),
                "cpi_yoy_1m_change": round(cpi, 2),
                "core_cpi_yoy_1m_change": round(core, 2),
            },
        )

    def _small_caps_lag_risk_sentiment(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        iwm = context.states["iwm"].delta_pct(21) or 0.0
        qqq = context.states["qqq"].delta_pct(21) or 0.0
        sp = context.states["sp500"].delta_pct(21) or 0.0
        vix = context.states["vix"].delta_pct(21) or 0.0
        hy = context.states["hy_spread"].delta(21)
        gap = max(qqq, sp) - iwm
        iwm_z = context.states["iwm"].zscore(21, pct=True)

        if gap <= 5.0 or sp <= 1.0 or hy > 0.08:
            return None

        divergence = _scale(gap, 4.5, 2.5)
        novelty = _scale(abs(iwm_z), 0.6, 0.7)
        breadth = 0.6 * float(vix <= 5.0) + 0.5 * float(hy <= 0.04) + 0.4 * float(context.states["xlf"].delta_pct(21) < 0.0)

        return self._build_signal(
            context,
            rule_code="small_caps_lag_despite_risk_on",
            title="Small caps are still not confirming the risk-on narrative",
            explanation="The market can still look healthy at the index level while financing-sensitive small caps fail to participate. That usually argues for narrow leadership rather than a genuinely broad cyclical upswing.",
            category="Breadth warning",
            related_assets=["IWM", "QQQ", "S&P 500", "VIX"],
            importance=2.8,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "iwm_1m_pct": round(iwm, 2),
                "qqq_1m_pct": round(qqq, 2),
                "sp500_1m_pct": round(sp, 2),
                "leadership_gap_pct": round(gap, 2),
            },
        )

    def _volatility_inconsistent_with_equities(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        sp = context.states["sp500"].delta_pct(5) or 0.0
        vix = context.states["vix"].delta_pct(5) or 0.0
        hy_change = context.states["hy_spread"].delta(5)
        vix_z = context.states["vix"].zscore(5, pct=True)

        if sp <= 0.75 or vix <= 6.0:
            return None

        divergence = _scale(sp, 0.7, 0.8) + _scale(vix, 5.0, 4.0)
        novelty = _scale(abs(vix_z), 0.8, 0.8)
        breadth = 0.6 * float(hy_change > 0.0) + 0.5 * float(context.states["xlf"].delta_pct(21) < 0.0) + 0.4 * float(context.states["iwm"].delta_pct(21) < context.states["qqq"].delta_pct(21))

        return self._build_signal(
            context,
            rule_code="vol_inconsistent_with_index_move",
            title="Volatility is rising underneath a positive index move",
            explanation="When the market grinds higher while implied volatility also rises, it usually means institutions are still paying for protection. That weakens the quality of the headline equity move.",
            category="Volatility divergence",
            related_assets=["S&P 500", "VIX", "High Yield Spreads"],
            importance=3.1,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "sp500_5d_pct": round(sp, 2),
                "vix_5d_pct": round(vix, 2),
                "hy_spread_5d_change": round(hy_change, 2),
                "vix_move_zscore": round(abs(vix_z), 2),
            },
        )

    def _sector_factor_divergence(self, context: AnomalyContext) -> AnomalyItemResponse | None:
        qqq = context.states["qqq"].delta_pct(21) or 0.0
        xlf = context.states["xlf"].delta_pct(21) or 0.0
        iwm = context.states["iwm"].delta_pct(21) or 0.0
        hy_change = context.states["hy_spread"].delta(21)
        gap = qqq - xlf
        xlf_z = context.states["xlf"].zscore(21, pct=True)

        if qqq <= 4.0 or xlf >= 0.0 or gap <= 5.0:
            return None

        divergence = _scale(gap, 4.5, 2.0)
        novelty = _scale(abs(xlf_z), 0.7, 0.7)
        breadth = 0.6 * float(iwm < 0.0) + 0.5 * float(hy_change > 0.0) + 0.4 * float(context.states["vix"].latest >= 18.0)

        return self._build_signal(
            context,
            rule_code="sector_factor_divergence",
            title="Tech leadership is diverging sharply from financials",
            explanation="A market led by long-duration growth while banks and financials struggle is usually a warning that liquidity and credit transmission are not confirming the bullish narrative.",
            category="Sector divergence",
            related_assets=["QQQ", "XLF", "IWM"],
            importance=2.7,
            divergence=divergence,
            novelty=novelty,
            breadth=breadth,
            supporting_metrics={
                "qqq_1m_pct": round(qqq, 2),
                "xlf_1m_pct": round(xlf, 2),
                "iwm_1m_pct": round(iwm, 2),
                "sector_gap_pct": round(gap, 2),
            },
        )
