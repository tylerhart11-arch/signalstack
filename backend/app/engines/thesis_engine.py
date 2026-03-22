from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.thesis import ExposureIdea, SectorIdea, ThesisResult, ThemeSignal


CAUSAL_TERMS = {
    "drive",
    "boost",
    "pressure",
    "support",
    "benefit",
    "tighten",
    "ease",
    "weigh",
    "lead",
    "lag",
}

LONG_HORIZON_TERMS = {"structural", "multi-year", "multi year", "long term", "over years"}
TACTICAL_TERMS = {"near term", "this quarter", "next quarter", "next few months", "short term"}
RELATIVE_VALUE_TERMS = {"relative", "versus", "vs", "outperform", "underperform", "lag"}
DEFENSIVE_TERMS = {"hedge", "protect", "defensive", "downside", "stress"}
BEARISH_TERMS = {"pressure", "underweight", "short", "lag", "worsen", "weaken"}
BULLISH_TERMS = {"benefit", "overweight", "long", "higher", "improve", "stronger"}


@dataclass(frozen=True)
class ThemeDefinition:
    name: str
    theme_family: str
    default_time_horizon: str
    default_expression_style: str
    keywords: dict[str, float]
    match_groups: tuple[tuple[str, ...], ...]
    transmission_channels: tuple[ThemeSignal, ...]
    sectors: tuple[SectorIdea, ...]
    etf_exposures: tuple[ExposureIdea, ...]
    representative_stocks: tuple[ExposureIdea, ...]
    catalysts: tuple[ThemeSignal, ...]
    confirming_signals: tuple[ThemeSignal, ...]
    invalidation_signals: tuple[ThemeSignal, ...]
    related_themes: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


THEME_LIBRARY = [
    ThemeDefinition(
        name="AI infrastructure power squeeze",
        theme_family="Power, Infrastructure, and AI Capacity",
        default_time_horizon="Structural (1-3 years)",
        default_expression_style="Directional long / capex beneficiaries",
        keywords={
            "ai": 2.8,
            "artificial intelligence": 3.0,
            "data center": 2.8,
            "data centers": 2.8,
            "electricity": 2.2,
            "power demand": 2.4,
            "grid": 2.0,
            "cooling": 1.8,
            "load growth": 2.0,
            "hyperscaler": 1.6,
        },
        match_groups=(
            ("ai", "artificial intelligence", "data center", "data centers", "hyperscaler"),
            ("electricity", "power demand", "grid", "cooling", "load growth"),
        ),
        transmission_channels=(
            ThemeSignal(name="Electric load growth", rationale="AI clusters raise baseload power demand."),
            ThemeSignal(name="Grid capex acceleration", rationale="Utilities and transmission operators need faster spend."),
            ThemeSignal(name="Thermal bottlenecks", rationale="Cooling and backup power become key choke points."),
        ),
        sectors=(
            SectorIdea(name="Utilities", stance="Overweight", rationale="Load growth and rate-base expansion improve the setup."),
            SectorIdea(name="Electrical equipment", stance="Overweight", rationale="Transformers, switchgear, and power-management vendors sit in the capex chain."),
            SectorIdea(name="Semiconductors and networking", stance="Selective overweight", rationale="Compute and networking demand remain tied to AI build-out."),
        ),
        etf_exposures=(
            ExposureIdea(name="Utilities Select Sector SPDR", symbol="XLU", stance="Long", rationale="Liquid utility basket tied to demand growth."),
            ExposureIdea(name="First Trust NASDAQ Clean Edge Smart Grid", symbol="GRID", stance="Long", rationale="Targets smart-grid and electrification infrastructure."),
            ExposureIdea(name="VanEck Semiconductor ETF", symbol="SMH", stance="Long", rationale="Captures the chip side of the stack."),
        ),
        representative_stocks=(
            ExposureIdea(name="Constellation Energy", symbol="CEG", stance="Long", rationale="Generation footprint with data-center demand leverage."),
            ExposureIdea(name="Vertiv", symbol="VRT", stance="Long", rationale="Direct exposure to power and cooling systems."),
            ExposureIdea(name="Eaton", symbol="ETN", stance="Long", rationale="Power-management supplier leveraged to grid upgrades."),
        ),
        catalysts=(
            ThemeSignal(name="Utility load-plan revisions", rationale="Utilities explicitly raise medium-term demand assumptions."),
            ThemeSignal(name="Hyperscaler capex guidance", rationale="Cloud platforms keep AI infrastructure budgets elevated."),
            ThemeSignal(name="Transformer backlog", rationale="Equipment lead times confirm real physical scarcity."),
        ),
        confirming_signals=(
            ThemeSignal(name="Power load forecasts move higher", rationale="Utilities and grid operators revise expectations upward."),
            ThemeSignal(name="Copper and equipment orders stay firm", rationale="Input demand validates the build-out."),
            ThemeSignal(name="Power prices remain tight", rationale="Local scarcity is what makes the theme economically relevant."),
        ),
        invalidation_signals=(
            ThemeSignal(name="Hyperscaler capex pauses", rationale="A spending pause breaks the core demand channel."),
            ThemeSignal(name="Utility regulatory pushback", rationale="Rate-case friction can delay monetization."),
            ThemeSignal(name="Power-market looseness", rationale="Fast supply relief weakens the scarcity angle."),
        ),
        related_themes=("Electrification capex", "Power scarcity", "Semis and thermal management"),
        notes=("This works best when the bottleneck is physical power delivery, not just chip supply.",),
    ),
    ThemeDefinition(
        name="Higher-for-longer rates pressure small caps",
        theme_family="Rates, Balance Sheets, and Domestic Cyclicals",
        default_time_horizon="Medium-term (3-12 months)",
        default_expression_style="Relative value / quality over small caps",
        keywords={
            "higher for longer": 3.2,
            "rates": 1.8,
            "yield": 1.6,
            "yields": 1.6,
            "small cap": 2.6,
            "small caps": 2.6,
            "russell": 1.8,
            "refinancing": 2.0,
            "regional banks": 1.6,
        },
        match_groups=(
            ("higher for longer", "rates", "yield", "yields"),
            ("small cap", "small caps", "russell", "refinancing"),
        ),
        transmission_channels=(
            ThemeSignal(name="Higher financing costs", rationale="Smaller companies have less balance-sheet flexibility."),
            ThemeSignal(name="Multiple compression", rationale="Higher discount rates weigh on lower-quality equities."),
            ThemeSignal(name="Domestic-demand sensitivity", rationale="Small caps lean harder on rate-sensitive US cyclicals."),
        ),
        sectors=(
            SectorIdea(name="Small-cap cyclicals", stance="Underweight", rationale="Funding and demand sensitivity both become headwinds."),
            SectorIdea(name="Regional banks", stance="Underweight", rationale="Higher deposit competition and credit stress pressure profitability."),
            SectorIdea(name="Defensive quality", stance="Overweight", rationale="Cash-generative large caps tend to hold up better."),
        ),
        etf_exposures=(
            ExposureIdea(name="iShares Russell 2000 ETF", symbol="IWM", stance="Underweight / Relative short", rationale="Direct expression of small-cap sensitivity."),
            ExposureIdea(name="SPDR S&P Regional Banking ETF", symbol="KRE", stance="Underweight", rationale="Captures tighter-credit and funding stress."),
            ExposureIdea(name="iShares 1-3 Year Treasury Bond ETF", symbol="SHY", stance="Long", rationale="Keeps carry high while limiting duration risk."),
        ),
        representative_stocks=(
            ExposureIdea(name="Zions Bancorporation", symbol="ZION", stance="Underweight", rationale="Regional lender exposed to tighter conditions."),
            ExposureIdea(name="Rocket Companies", symbol="RKT", stance="Underweight", rationale="Housing finance remains rate sensitive."),
            ExposureIdea(name="Monster Beverage", symbol="MNST", stance="Overweight", rationale="Large-cap quality offers a cleaner defensive alternative."),
        ),
        catalysts=(
            ThemeSignal(name="Sticky front-end yields", rationale="2Y yields remain elevated and delay relief."),
            ThemeSignal(name="Refinancing calendar pressure", rationale="Near-term maturities start to bite."),
            ThemeSignal(name="Regional-bank earnings stress", rationale="Deposit costs and provisioning validate the restrictive backdrop."),
        ),
        confirming_signals=(
            ThemeSignal(name="2Y yield stays elevated", rationale="The front end remains restrictive."),
            ThemeSignal(name="Russell 2000 relative weakness persists", rationale="Small caps keep lagging large-cap benchmarks."),
            ThemeSignal(name="Credit spreads widen", rationale="Funding stress confirms that rates are biting."),
        ),
        invalidation_signals=(
            ThemeSignal(name="Front-end rates reprice lower", rationale="A clearer easing path relieves the core pressure point."),
            ThemeSignal(name="Small-cap earnings breadth improves", rationale="Stronger fundamentals could offset financing stress."),
            ThemeSignal(name="Curve steepens on stronger growth", rationale="A healthier growth impulse can rescue cyclicals."),
        ),
        related_themes=("Quality over cyclicals", "Regional-bank stress", "Domestic late-cycle pressure"),
        notes=("Usually best framed as a relative-value thesis rather than a pure crash call.",),
    ),
    ThemeDefinition(
        name="Home energy inflation persists",
        theme_family="Consumer Inflation and Utility Pass-Through",
        default_time_horizon="Medium-term (3-12 months)",
        default_expression_style="Barbell: utilities and efficiency upgrades",
        keywords={
            "home energy": 3.0,
            "utility bills": 2.6,
            "electricity prices": 2.4,
            "power bills": 2.2,
            "natural gas": 1.8,
            "heating": 1.2,
            "energy costs": 1.8,
        },
        match_groups=(
            ("home energy", "utility bills", "electricity prices", "power bills"),
            ("natural gas", "heating", "energy costs"),
        ),
        transmission_channels=(
            ThemeSignal(name="Utility rate pass-through", rationale="Retail customers absorb fuel and infrastructure cost increases."),
            ThemeSignal(name="Efficiency-upgrade demand", rationale="Higher bills pull forward HVAC and retrofit spend."),
            ThemeSignal(name="Real-income squeeze", rationale="Higher utility bills crowd out other household spending."),
        ),
        sectors=(
            SectorIdea(name="Utilities", stance="Overweight", rationale="Rate-base growth and pricing revisions support regulated names."),
            SectorIdea(name="HVAC and efficiency", stance="Overweight", rationale="Customers respond by upgrading equipment and controls."),
            SectorIdea(name="Residential discretionary", stance="Underweight", rationale="Higher utility bills reduce room for other spending."),
        ),
        etf_exposures=(
            ExposureIdea(name="Utilities Select Sector SPDR", symbol="XLU", stance="Long", rationale="Broad listed utility exposure."),
            ExposureIdea(name="First Trust Natural Gas ETF", symbol="FCG", stance="Selective long", rationale="Useful when the thesis is fuel-cost driven."),
            ExposureIdea(name="Invesco Dynamic Building & Construction ETF", symbol="PKB", stance="Selective long", rationale="Captures retrofit and home-system upgrade demand."),
        ),
        representative_stocks=(
            ExposureIdea(name="NRG Energy", symbol="NRG", stance="Long", rationale="Retail and generation exposure benefits when power markets tighten."),
            ExposureIdea(name="Carrier Global", symbol="CARR", stance="Long", rationale="HVAC upgrade demand fits the efficiency response."),
            ExposureIdea(name="Trane Technologies", symbol="TT", stance="Long", rationale="Energy-efficiency retrofits can accelerate when bills stay elevated."),
        ),
        catalysts=(
            ThemeSignal(name="Utility tariff resets", rationale="Regulators approve higher rates or fuel-cost recovery."),
            ThemeSignal(name="Gas and power volatility", rationale="Wholesale energy moves feed through to consumer bills."),
            ThemeSignal(name="Extreme weather", rationale="Demand spikes make bill pressure tangible."),
        ),
        confirming_signals=(
            ThemeSignal(name="Utility CPI components stay firm", rationale="Official inflation baskets keep showing sticky home-energy pressure."),
            ThemeSignal(name="Regional power prices spike", rationale="Wholesale market stress feeds into retail bills."),
            ThemeSignal(name="HVAC order growth improves", rationale="Efficiency demand validates the second-order effect."),
        ),
        invalidation_signals=(
            ThemeSignal(name="Natural gas collapses", rationale="Lower fuel costs ease pass-through pressure."),
            ThemeSignal(name="Weather normalizes", rationale="Milder seasons reduce demand stress."),
            ThemeSignal(name="Policy relief caps bills", rationale="Regulatory intervention can interrupt the pass-through."),
        ),
        related_themes=("Residential squeeze", "Efficiency retrofits", "Power-market tightness"),
    ),
    ThemeDefinition(
        name="Credit stress leads equities",
        theme_family="Credit, Funding Conditions, and Late-Cycle Risk",
        default_time_horizon="Tactical to medium-term (1-9 months)",
        default_expression_style="Defensive / hedge overlay",
        keywords={
            "credit stress": 3.0,
            "credit": 1.6,
            "spreads": 2.0,
            "spread": 1.2,
            "default": 1.8,
            "defaults": 1.8,
            "funding": 1.6,
            "before equities": 2.2,
            "equities react": 2.0,
            "liquidity": 1.4,
        },
        match_groups=(
            ("credit stress", "credit", "spreads", "funding", "liquidity"),
            ("before equities", "equities react", "lead", "worsens"),
        ),
        transmission_channels=(
            ThemeSignal(name="Spread widening", rationale="Lower-quality credit often reacts earlier than equities to funding stress."),
            ThemeSignal(name="Refinancing wall pressure", rationale="Near-term maturities become more dangerous as capital costs rise."),
            ThemeSignal(name="Risk appetite rollover", rationale="Equities can ignore credit warnings until liquidity visibly deteriorates."),
        ),
        sectors=(
            SectorIdea(name="High-yield credit", stance="Underweight", rationale="Usually the earliest liquid market to reflect funding stress."),
            SectorIdea(name="Regional banks and finance", stance="Underweight", rationale="Funding and provisioning become a transmission channel."),
            SectorIdea(name="Consumer defensives", stance="Overweight", rationale="Lower-beta defensives help offset late-cycle stress."),
        ),
        etf_exposures=(
            ExposureIdea(name="iShares iBoxx High Yield Corporate Bond ETF", symbol="HYG", stance="Underweight / Hedge", rationale="Liquid proxy for spread stress."),
            ExposureIdea(name="SPDR S&P Regional Banking ETF", symbol="KRE", stance="Underweight", rationale="Captures a common financial-stress transmission point."),
            ExposureIdea(name="Consumer Staples Select Sector SPDR", symbol="XLP", stance="Long", rationale="Defensive ballast if stress spreads."),
        ),
        representative_stocks=(
            ExposureIdea(name="Ally Financial", symbol="ALLY", stance="Underweight", rationale="Consumer credit sensitivity fits an early-stress view."),
            ExposureIdea(name="Comerica", symbol="CMA", stance="Underweight", rationale="Regional bank with cyclical credit exposure."),
            ExposureIdea(name="Walmart", symbol="WMT", stance="Overweight", rationale="Defensive consumer exposure can outperform in stress."),
        ),
        catalysts=(
            ThemeSignal(name="HY spread breakout", rationale="Credit starts widening faster than equity vol acknowledges."),
            ThemeSignal(name="Tighter loan-officer surveys", rationale="Bank credit supply confirms funding conditions are worsening."),
            ThemeSignal(name="Default and downgrade pickup", rationale="Fundamentals start catching up with the market warning."),
        ),
        confirming_signals=(
            ThemeSignal(name="HY spreads widen ahead of VIX", rationale="Credit moves first while equity vol stays complacent."),
            ThemeSignal(name="Loan officer surveys tighten", rationale="Bank credit supply is an important follow-through signal."),
            ThemeSignal(name="Defaults and downgrades rise", rationale="Fundamental deterioration validates the market signal."),
        ),
        invalidation_signals=(
            ThemeSignal(name="Spreads snap back tighter", rationale="The warning fails if credit quickly heals."),
            ThemeSignal(name="Earnings revisions improve", rationale="Better growth can overwhelm a temporary scare."),
            ThemeSignal(name="Policy backstops arrive early", rationale="Liquidity support can short-circuit the stress transmission."),
        ),
        related_themes=("Funding stress", "Regional-bank pressure", "Late-cycle defensives"),
    ),
    ThemeDefinition(
        name="Commodity reflation broadens",
        theme_family="Nominal Growth and Cyclical Reflation",
        default_time_horizon="Tactical to medium-term (2-9 months)",
        default_expression_style="Directional long / cyclical rotation",
        keywords={
            "reflation": 2.8,
            "commodities": 2.4,
            "oil": 1.8,
            "copper": 1.8,
            "inflationary expansion": 2.2,
            "materials": 1.6,
            "industrials": 1.4,
            "cyclical": 1.4,
        },
        match_groups=(
            ("reflation", "commodities", "oil", "copper"),
            ("materials", "industrials", "cyclical", "inflationary expansion"),
        ),
        transmission_channels=(
            ThemeSignal(name="Input-cost inflation", rationale="Oil and metals strength push costs and inflation expectations higher."),
            ThemeSignal(name="Capex revival", rationale="Commodity-linked capex and industrial activity reaccelerate."),
            ThemeSignal(name="Cyclical leadership", rationale="Materials, energy, and industrials take over equity leadership."),
        ),
        sectors=(
            SectorIdea(name="Energy", stance="Overweight", rationale="Oil beta remains the cleanest expression."),
            SectorIdea(name="Materials", stance="Overweight", rationale="Metals and mining participate in broader reflation."),
            SectorIdea(name="Long-duration defensives", stance="Underweight", rationale="Rates pressure can weigh on bond proxies."),
        ),
        etf_exposures=(
            ExposureIdea(name="Energy Select Sector SPDR", symbol="XLE", stance="Long", rationale="Liquid exposure to oil-linked equities."),
            ExposureIdea(name="Materials Select Sector SPDR", symbol="XLB", stance="Long", rationale="Captures broader reflation leadership."),
            ExposureIdea(name="Invesco DB Commodity Index Tracking Fund", symbol="DBC", stance="Long", rationale="Multi-commodity expression of the macro view."),
        ),
        representative_stocks=(
            ExposureIdea(name="Freeport-McMoRan", symbol="FCX", stance="Long", rationale="Copper sensitivity makes it a clean reflation vehicle."),
            ExposureIdea(name="Exxon Mobil", symbol="XOM", stance="Long", rationale="Large-cap oil exposure with balance-sheet resilience."),
            ExposureIdea(name="Nucor", symbol="NUE", stance="Long", rationale="Industrial metals demand fits a cyclical upturn."),
        ),
        catalysts=(
            ThemeSignal(name="Copper and oil break higher together", rationale="Broad commodity strength matters more than a one-off energy move."),
            ThemeSignal(name="Breakevens widen", rationale="Market inflation expectations confirm reflation."),
            ThemeSignal(name="Industrials leadership improves", rationale="Equity rotation validates the macro shift."),
        ),
        confirming_signals=(
            ThemeSignal(name="Copper and oil both trend higher", rationale="Broad commodity strength is more powerful than a one-off oil move."),
            ThemeSignal(name="Breakevens widen", rationale="Market inflation expectations confirm reflation."),
            ThemeSignal(name="Industrials outperform", rationale="Equity leadership rotates toward cyclicals."),
        ),
        invalidation_signals=(
            ThemeSignal(name="China demand disappoints", rationale="A weak global industrial impulse can break the commodity leg."),
            ThemeSignal(name="Dollar surges", rationale="Tighter global financial conditions often cap commodity upside."),
            ThemeSignal(name="Energy curve softens", rationale="A weaker forward curve undercuts the reflation conviction."),
        ),
        related_themes=("Cyclical rotation", "Nominal growth", "Energy and materials leadership"),
    ),
]


class ThesisEngine:
    def analyze(self, text: str) -> ThesisResult:
        clean_text = text.strip().lower()
        tokens = self._tokenize(clean_text)
        scored_themes: list[tuple[float, ThemeDefinition, list[str]]] = []

        for theme in THEME_LIBRARY:
            score, matched = self._score_theme(clean_text, tokens, theme)
            if score > 0:
                scored_themes.append((score, theme, matched))

        if not scored_themes:
            return self._fallback_result(text)

        scored_themes.sort(key=lambda item: item[0], reverse=True)
        top_score, top_theme, matched = scored_themes[0]
        secondary = [theme.name for score, theme, _ in scored_themes[1:] if score >= max(3.8, top_score * 0.55)][:3]
        confidence = min(0.93, 0.46 + (top_score * 0.055) + (0.04 * len(matched)))

        return ThesisResult(
            interpreted_theme=top_theme.name,
            confidence=round(confidence, 2),
            theme_family=top_theme.theme_family,
            time_horizon=self._infer_time_horizon(clean_text, top_theme),
            expression_style=self._infer_expression_style(clean_text, top_theme),
            matched_keywords=matched[:8],
            secondary_themes=secondary or list(top_theme.related_themes[:2]),
            transmission_channels=list(top_theme.transmission_channels),
            sectors=list(top_theme.sectors),
            etf_exposures=list(top_theme.etf_exposures),
            representative_stocks=list(top_theme.representative_stocks),
            catalysts=list(top_theme.catalysts),
            confirming_signals=list(top_theme.confirming_signals),
            invalidation_signals=list(top_theme.invalidation_signals),
            notes=[
                "Mappings are rules-based for transparency and should be treated as a structured starting point, not portfolio advice.",
                f"Theme family: {top_theme.theme_family}.",
                *top_theme.notes,
            ],
        )

    def _score_theme(self, text: str, tokens: list[str], theme: ThemeDefinition) -> tuple[float, list[str]]:
        matched_terms: list[str] = []
        score = 0.0

        for keyword, weight in theme.keywords.items():
            if " " in keyword:
                if keyword in text:
                    matched_terms.append(keyword)
                    score += weight
            elif keyword in tokens:
                matched_terms.append(keyword)
                score += weight * 0.9

        if any(term in tokens for term in CAUSAL_TERMS):
            score += 0.5

        for group in theme.match_groups:
            if any(term in text for term in group):
                score += 1.5
            else:
                score -= 1.4

        if any(word in text for word in ("higher", "lower", "rising", "falling", "continue", "persist")):
            score += 0.4

        return round(max(0.0, score), 2), list(dict.fromkeys(matched_terms))

    def _infer_time_horizon(self, text: str, theme: ThemeDefinition) -> str:
        if any(term in text for term in LONG_HORIZON_TERMS):
            return "Structural (1-3 years)"
        if any(term in text for term in TACTICAL_TERMS):
            return "Tactical (1-3 months)"
        return theme.default_time_horizon

    def _infer_expression_style(self, text: str, theme: ThemeDefinition) -> str:
        if any(term in text for term in RELATIVE_VALUE_TERMS):
            return "Relative value / pairs"
        if any(term in text for term in DEFENSIVE_TERMS):
            return "Hedge / defensive overlay"
        if any(term in text for term in BEARISH_TERMS):
            return "Directional short / underweight"
        if any(term in text for term in BULLISH_TERMS):
            return "Directional long / overweight"
        return theme.default_expression_style

    def _fallback_result(self, text: str) -> ThesisResult:
        lower_text = text.lower()
        theme_name = "Generic macro translation"
        theme_family = "Unclassified macro idea"
        time_horizon = "Medium-term (3-12 months)"
        expression_style = "Watchlist / benchmark-first"
        channels = [
            ThemeSignal(
                name="Narrative decomposition",
                rationale="SignalStack could not map the idea to a named template, so it translated the thesis into generic macro channels first.",
            )
        ]
        sectors = [SectorIdea(name="Broad market", stance="Watch", rationale="Validate the macro path before narrowing to industries.")]
        etfs = [ExposureIdea(name="SPDR S&P 500 ETF Trust", symbol="SPY", stance="Watch", rationale="Use as a benchmark while refining the thesis.")]
        stocks = [ExposureIdea(name="Market proxy", symbol="SPY", stance="Watch", rationale="No narrower basket scored highly enough yet.")]
        catalysts = [ThemeSignal(name="Clarify the catalyst", rationale="Define what should change first and on what time horizon.")]
        confirming = [ThemeSignal(name="Relative performance", rationale="The assets tied most directly to the thesis should outperform their benchmark.")]
        invalidation = [ThemeSignal(name="Cross-asset contradiction", rationale="If rates, credit, and commodities all disagree, the thesis likely needs refinement.")]
        notes = ["Try adding a catalyst, a transmission phrase such as 'will pressure' or 'will benefit', and a more specific industry or factor."]
        secondary_themes: list[str] = []

        if "inflation" in lower_text or "price" in lower_text:
            theme_name = "Inflation-sensitive macro view"
            theme_family = "Inflation and pricing power"
            channels.append(ThemeSignal(name="Pricing pass-through", rationale="The thesis appears to rely on inflation changing margins or consumer behavior."))
            sectors = [SectorIdea(name="Energy and materials", stance="Watch", rationale="Inflation narratives often transmit through commodity-linked sectors.")]
            catalysts.append(ThemeSignal(name="Inflation surprise data", rationale="CPI and commodity moves should validate the thesis quickly."))
            secondary_themes = ["Commodity sensitivity", "Consumer squeeze"]
        elif "rates" in lower_text or "yield" in lower_text or "fed" in lower_text:
            theme_name = "Rates-sensitive macro view"
            theme_family = "Rates and financial conditions"
            channels.append(ThemeSignal(name="Discount-rate shock", rationale="The thesis appears tied to financing costs and valuation pressure."))
            etfs = [ExposureIdea(name="iShares 1-3 Year Treasury Bond ETF", symbol="SHY", stance="Watch", rationale="Useful anchor for short-duration policy expectations.")]
            secondary_themes = ["Front-end policy", "Balance-sheet sensitivity"]
        elif "credit" in lower_text or "spread" in lower_text:
            theme_name = "Credit-led risk view"
            theme_family = "Funding conditions and credit risk"
            expression_style = "Defensive / hedge overlay"
            channels.append(ThemeSignal(name="Funding conditions", rationale="The idea appears to hinge on spread behavior as an early warning signal."))
            etfs = [ExposureIdea(name="iShares iBoxx High Yield Corporate Bond ETF", symbol="HYG", stance="Watch", rationale="Liquid gauge for the thesis before committing capital.")]
            secondary_themes = ["Funding stress", "Late-cycle risk"]
        elif "commodity" in lower_text or "oil" in lower_text or "copper" in lower_text:
            theme_name = "Commodity-sensitive macro view"
            theme_family = "Nominal growth and commodities"
            channels.append(ThemeSignal(name="Input-cost impulse", rationale="The thesis appears linked to commodity moves feeding through to growth or inflation."))
            etfs = [ExposureIdea(name="Invesco DB Commodity Index Tracking Fund", symbol="DBC", stance="Watch", rationale="Broad commodity benchmark while the view is refined.")]
            secondary_themes = ["Reflation", "Cyclical rotation"]

        return ThesisResult(
            interpreted_theme=theme_name,
            confidence=0.44,
            theme_family=theme_family,
            time_horizon=time_horizon,
            expression_style=expression_style,
            matched_keywords=[],
            secondary_themes=secondary_themes,
            transmission_channels=channels,
            sectors=sectors,
            etf_exposures=etfs,
            representative_stocks=stocks,
            catalysts=catalysts,
            confirming_signals=confirming,
            invalidation_signals=invalidation,
            notes=notes,
        )

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.findall(r"[a-z0-9]+", text) if len(token) > 1]
