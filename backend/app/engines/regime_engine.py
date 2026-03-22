from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.schemas.regime import RegimeCurrentResponse, RegimeDriver
from app.services.overview_service import IndicatorState
from app.utils.math_utils import clamp


REGIME_LABELS = [
    "Disinflationary Growth",
    "Inflationary Expansion",
    "Slowdown",
    "Recession Risk",
    "Liquidity Expansion",
    "Stress / Crisis",
]


@dataclass
class RegimeMetrics:
    cpi_latest: float
    core_cpi_latest: float
    cpi_1m: float
    core_cpi_1m: float
    cpi_3m: float
    core_cpi_3m: float
    unemployment_latest: float
    unemployment_1m: float
    unemployment_3m: float
    slope_latest: float
    slope_1m: float
    hy_latest: float
    hy_1m: float
    ig_1m: float
    sp_1m: float
    qqq_1m: float
    russell_1m: float
    vix_latest: float
    vix_1m: float
    vix_5d: float
    copper_1m: float
    oil_1m: float
    gold_1m: float
    dxy_1m: float
    two_year_1m: float
    ten_year_1m: float

class RegimeEngine:
    def evaluate(
        self,
        states: dict[str, IndicatorState],
        as_of: datetime,
        previous_regime: str | None = None,
    ) -> RegimeCurrentResponse:
        metrics = self._build_metrics(states)
        pillars = self._score_pillars(metrics)
        raw_scores, contributions = self._score_regimes(pillars)
        scaled_scores = {label: round(min(10.0, score * 1.15), 2) for label, score in raw_scores.items()}

        top_regime = max(scaled_scores, key=scaled_scores.get)
        sorted_scores = sorted(scaled_scores.values(), reverse=True)
        spread = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else sorted_scores[0]
        intensity = sum(abs(score) for score in pillars.values()) / max(1, len(pillars))
        confidence = clamp(0.5 + (spread / 14.0) + (intensity / 20.0), 0.48, 0.93)

        top_drivers = sorted(contributions[top_regime], key=lambda item: item.weight, reverse=True)[:5]
        summary = self._build_summary(top_regime, top_drivers)

        return RegimeCurrentResponse(
            as_of=as_of,
            regime=top_regime,
            previous_regime=previous_regime,
            confidence=round(confidence, 2),
            summary=summary,
            drivers=top_drivers,
            supporting_indicators=self._supporting_indicators(states),
            regime_scores=scaled_scores,
            pillar_scores={label: round(score, 2) for label, score in pillars.items()},
        )

    def _build_metrics(self, states: dict[str, IndicatorState]) -> RegimeMetrics:
        return RegimeMetrics(
            cpi_latest=states["cpi_yoy"].latest,
            core_cpi_latest=states["core_cpi_yoy"].latest,
            cpi_1m=states["cpi_yoy"].delta(1),
            core_cpi_1m=states["core_cpi_yoy"].delta(1),
            cpi_3m=states["cpi_yoy"].delta(3),
            core_cpi_3m=states["core_cpi_yoy"].delta(3),
            unemployment_latest=states["unemployment_rate"].latest,
            unemployment_1m=states["unemployment_rate"].delta(1),
            unemployment_3m=states["unemployment_rate"].delta(3),
            slope_latest=states["s2s10s"].latest,
            slope_1m=states["s2s10s"].delta(21),
            hy_latest=states["hy_spread"].latest,
            hy_1m=states["hy_spread"].delta(21),
            ig_1m=states["ig_spread"].delta(21),
            sp_1m=states["sp500"].delta_pct(21) or 0.0,
            qqq_1m=states["qqq"].delta_pct(21) or states["nasdaq100"].delta_pct(21) or 0.0,
            russell_1m=states["russell2000"].delta_pct(21) or 0.0,
            vix_latest=states["vix"].latest,
            vix_1m=states["vix"].delta_pct(21) or 0.0,
            vix_5d=states["vix"].delta_pct(5) or 0.0,
            copper_1m=states["copper"].delta_pct(21) or 0.0,
            oil_1m=states["wti"].delta_pct(21) or 0.0,
            gold_1m=states["gold"].delta_pct(21) or 0.0,
            dxy_1m=states["dxy"].delta_pct(21) or 0.0,
            two_year_1m=states["us2y"].delta(21),
            ten_year_1m=states["us10y"].delta(21),
        )

    def _score_pillars(self, metrics: RegimeMetrics) -> dict[str, float]:
        disinflation = clamp(
            (-metrics.cpi_1m * 14.0)
            + (-metrics.core_cpi_1m * 18.0)
            + (-metrics.cpi_3m * 2.5)
            + max(0.0, 3.2 - metrics.core_cpi_latest) * 0.45,
            -3.0,
            3.0,
        )
        growth = clamp(
            (metrics.sp_1m / 5.0)
            + (metrics.russell_1m / 4.0)
            + (metrics.copper_1m / 4.0)
            - max(0.0, metrics.unemployment_1m) * 16.0
            - max(0.0, metrics.hy_1m) * 4.5,
            -3.0,
            3.0,
        )
        labor = clamp(
            (4.0 - metrics.unemployment_latest) * 1.8
            - metrics.unemployment_1m * 15.0
            - max(0.0, metrics.unemployment_3m) * 5.0,
            -3.0,
            3.0,
        )
        curve = clamp(
            (metrics.slope_1m / 11.0)
            + (metrics.slope_latest / 35.0)
            - max(0.0, -metrics.slope_latest) / 40.0,
            -3.0,
            3.0,
        )
        credit = clamp(
            (-metrics.hy_1m * 5.5)
            + (-metrics.ig_1m * 11.0)
            + max(0.0, 4.0 - metrics.hy_latest) * 0.35
            - max(0.0, metrics.hy_latest - 4.0) * 0.8,
            -3.0,
            3.0,
        )
        risk = clamp(
            (metrics.sp_1m / 4.5)
            + (metrics.qqq_1m / 6.0)
            + (metrics.russell_1m / 4.5)
            - (metrics.vix_1m / 14.0)
            - max(0.0, metrics.vix_latest - 18.0) * 0.32,
            -3.0,
            3.0,
        )
        commodity = clamp(
            (metrics.oil_1m / 6.5)
            + (metrics.copper_1m / 5.0)
            - max(0.0, metrics.gold_1m) / 12.0,
            -3.0,
            3.0,
        )
        liquidity = clamp(
            (-metrics.two_year_1m * 7.5)
            + (-metrics.dxy_1m / 1.8)
            + (metrics.slope_1m / 15.0)
            - max(0.0, metrics.hy_1m) * 3.5,
            -3.0,
            3.0,
        )
        stress = clamp(
            max(0.0, -credit) * 1.15
            + max(0.0, -risk)
            + max(0.0, metrics.vix_latest - 20.0) / 4.0
            + max(0.0, metrics.dxy_1m) / 3.2,
            0.0,
            3.5,
        )

        return {
            "disinflation": disinflation,
            "growth": growth,
            "labor": labor,
            "curve": curve,
            "credit": credit,
            "risk": risk,
            "commodity": commodity,
            "liquidity": liquidity,
            "stress": stress,
        }

    def _score_regimes(self, pillars: dict[str, float]) -> tuple[dict[str, float], dict[str, list[RegimeDriver]]]:
        scores = {label: 0.0 for label in REGIME_LABELS}
        drivers = {label: [] for label in REGIME_LABELS}

        def add(regime: str, label: str, detail: str, amount: float) -> None:
            if amount <= 0:
                return
            scores[regime] += amount
            drivers[regime].append(RegimeDriver(label=label, detail=detail, weight=round(amount, 2)))

        add(
            "Disinflationary Growth",
            "Disinflation is broadening",
            "Headline and core inflation are cooling enough to ease macro pressure without a full collapse in demand.",
            max(0.0, pillars["disinflation"]) * 2.1,
        )
        add(
            "Disinflationary Growth",
            "Growth pulse remains positive",
            "Equities and cyclicals still imply the expansion is bending, not breaking.",
            max(0.0, pillars["growth"]) * 1.5,
        )
        add(
            "Disinflationary Growth",
            "Credit remains supportive",
            "Credit conditions are still calm enough to support a constructive risk backdrop.",
            max(0.0, pillars["credit"]) * 1.1,
        )
        add(
            "Disinflationary Growth",
            "Risk appetite is holding",
            "The tape still supports a growth-without-recession interpretation.",
            max(0.0, pillars["risk"]) * 1.0,
        )

        add(
            "Inflationary Expansion",
            "Inflation pressure is rebuilding",
            "Disinflation is fading and the price pulse is reasserting itself.",
            max(0.0, -pillars["disinflation"]) * 1.9,
        )
        add(
            "Inflationary Expansion",
            "Commodity complex is firm",
            "Oil and copper are reinforcing a hotter nominal growth backdrop.",
            max(0.0, pillars["commodity"]) * 1.2,
        )
        add(
            "Inflationary Expansion",
            "Growth is still running warm",
            "Risk assets and cyclical indicators still point to expansion rather than contraction.",
            max(0.0, pillars["growth"]) * 1.3,
        )
        add(
            "Inflationary Expansion",
            "Risk appetite is constructive",
            "Markets are still rewarding cyclical and pro-growth exposures.",
            max(0.0, pillars["risk"]) * 0.8,
        )

        add(
            "Slowdown",
            "Disinflation is continuing",
            "Price pressure is coming down, but it is doing so alongside softer demand signals.",
            max(0.0, pillars["disinflation"]) * 1.6,
        )
        add(
            "Slowdown",
            "Growth impulse is fading",
            "Breadth, cyclicals, and growth-sensitive assets are cooling from stronger levels.",
            max(0.0, -pillars["growth"]) * 1.6,
        )
        add(
            "Slowdown",
            "Labor is softening",
            "Employment conditions are moving away from clearly resilient territory.",
            max(0.0, -pillars["labor"]) * 1.4,
        )
        add(
            "Slowdown",
            "Curve still signals late cycle",
            "The yield curve is still too compressed to fully clear the slowdown warning.",
            max(0.0, -pillars["curve"]) * 1.0,
        )
        add(
            "Slowdown",
            "Credit is no longer clean",
            "Spread behavior is deteriorating enough to pull conviction away from a benign landing.",
            max(0.0, -pillars["credit"]) * 1.2,
        )

        add(
            "Recession Risk",
            "Credit deterioration is intensifying",
            "Wider spreads are consistent with funding stress moving ahead of broader risk assets.",
            max(0.0, -pillars["credit"]) * 1.8,
        )
        add(
            "Recession Risk",
            "Growth is slipping below trend",
            "Cross-asset growth proxies are fading fast enough to raise recession odds.",
            max(0.0, -pillars["growth"]) * 1.8,
        )
        add(
            "Recession Risk",
            "Labor damage is building",
            "Labor data is no longer resilient enough to anchor a benign macro story.",
            max(0.0, -pillars["labor"]) * 1.8,
        )
        add(
            "Recession Risk",
            "Risk appetite is defensive",
            "Market leadership and volatility are consistent with a more defensive tape.",
            max(0.0, -pillars["risk"]) * 1.2,
        )
        add(
            "Recession Risk",
            "Stress indicators are elevated",
            "Cross-asset stress is high enough that recession risk is becoming harder to dismiss.",
            max(0.0, pillars["stress"] - 1.0) * 0.8,
        )

        add(
            "Liquidity Expansion",
            "Liquidity conditions are easing",
            "Front-end rates and the dollar are moving in a direction that eases financial conditions.",
            max(0.0, pillars["liquidity"]) * 1.9,
        )
        add(
            "Liquidity Expansion",
            "Curve is normalizing",
            "Steepening and less inversion are consistent with easier policy expectations.",
            max(0.0, pillars["curve"]) * 0.9,
        )
        add(
            "Liquidity Expansion",
            "Disinflation supports easier conditions",
            "Cooling inflation gives policymakers more room to ease without losing credibility.",
            max(0.0, pillars["disinflation"]) * 1.2,
        )
        add(
            "Liquidity Expansion",
            "Risk appetite is responding",
            "Market leadership is still consistent with easier liquidity feeding into asset prices.",
            max(0.0, pillars["risk"]) * 0.8,
        )

        add(
            "Stress / Crisis",
            "Stress composite is elevated",
            "Credit, volatility, and dollar behavior are acting like a broader stress regime is taking hold.",
            pillars["stress"] * 2.0,
        )
        add(
            "Stress / Crisis",
            "Credit markets are under pressure",
            "Credit weakness is forceful enough to threaten broader market stability.",
            max(0.0, -pillars["credit"]) * 1.4,
        )
        add(
            "Stress / Crisis",
            "Risk assets are not confirming growth",
            "The market is behaving more like a defensive or hedged tape than a healthy expansion.",
            max(0.0, -pillars["risk"]) * 1.3,
        )
        add(
            "Stress / Crisis",
            "Liquidity is tightening, not easing",
            "The conditions most likely to stabilize markets are not yet improving.",
            max(0.0, -pillars["liquidity"]) * 0.7,
        )

        return scores, drivers

    def _build_summary(self, regime: str, drivers: list[RegimeDriver]) -> str:
        lead_driver = drivers[0].label if drivers else "Cross-asset conditions"
        if regime == "Disinflationary Growth":
            return f"{lead_driver} is keeping the backdrop constructive: inflation is cooling, growth has not fully broken, and credit still supports risk."
        if regime == "Inflationary Expansion":
            return f"{lead_driver} is pushing the tape toward a hotter nominal growth regime where commodities and cyclical leadership matter more than duration relief."
        if regime == "Slowdown":
            return f"{lead_driver} is pulling the market into a late-cycle slowdown: disinflation helps, but breadth and macro confirmation are weakening."
        if regime == "Recession Risk":
            return f"{lead_driver} is pushing the macro backdrop into a more defensive posture where recession hedges and quality balance-sheet exposures deserve more weight."
        if regime == "Liquidity Expansion":
            return f"{lead_driver} is easing financial conditions enough to support a liquidity-led rebound, even if underlying growth remains uneven."
        return f"{lead_driver} is consistent with a cross-asset stress regime where capital preservation matters more than cyclical upside."

    def _supporting_indicators(self, states: dict[str, IndicatorState]) -> dict[str, float]:
        return {
            "cpi_yoy": round(states["cpi_yoy"].latest, 2),
            "core_cpi_yoy": round(states["core_cpi_yoy"].latest, 2),
            "unemployment_rate": round(states["unemployment_rate"].latest, 2),
            "s2s10s_bps": round(states["s2s10s"].latest, 0),
            "hy_spread": round(states["hy_spread"].latest, 2),
            "ig_spread": round(states["ig_spread"].latest, 2),
            "sp500_1m_pct": round(states["sp500"].delta_pct(21) or 0.0, 2),
            "russell2000_1m_pct": round(states["russell2000"].delta_pct(21) or 0.0, 2),
            "vix": round(states["vix"].latest, 2),
            "wti_1m_pct": round(states["wti"].delta_pct(21) or 0.0, 2),
        }
