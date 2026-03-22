from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    name: str
    category: str
    unit: str
    provider: str
    provider_id: str | None = None
    featured: bool = True
    trend_metric: str = "pct"
    direction_threshold: float = 0.5
    change_window: int = 5
    trend_1m_window: int = 21
    trend_3m_window: int = 63
    sparkline_points: int = 30
    display_precision: int = 2
    transform: str | None = None


INDICATOR_DEFINITIONS = [
    IndicatorDefinition("sp500", "S&P 500", "Equities", "index", "yahoo", "^GSPC", True, "pct", 0.4, 5, 21, 63, 30, 0),
    IndicatorDefinition("nasdaq100", "Nasdaq 100", "Equities", "index", "yahoo", "^NDX", True, "pct", 0.5, 5, 21, 63, 30, 0),
    IndicatorDefinition("russell2000", "Russell 2000", "Equities", "index", "yahoo", "^RUT", True, "pct", 0.6, 5, 21, 63, 30, 0),
    IndicatorDefinition("vix", "VIX", "Risk", "index", "yahoo", "^VIX", True, "pct", 1.5, 5, 21, 63, 30, 2),
    IndicatorDefinition("us2y", "US 2Y Treasury", "Rates", "%", "fred", "DGS2", True, "absolute", 0.06, 5, 21, 63, 30, 2),
    IndicatorDefinition("us10y", "US 10Y Treasury", "Rates", "%", "fred", "DGS10", True, "absolute", 0.06, 5, 21, 63, 30, 2),
    IndicatorDefinition("s2s10s", "2s10s Slope", "Rates", "bps", "derived", None, True, "absolute", 5.0, 5, 21, 63, 30, 0),
    IndicatorDefinition("hy_spread", "High Yield Spread Proxy", "Credit", "%", "fred", "BAMLH0A0HYM2", True, "absolute", 0.08, 5, 21, 63, 30, 2),
    IndicatorDefinition("ig_spread", "Investment Grade Spread Proxy", "Credit", "%", "fred", "BAMLC0A0CM", True, "absolute", 0.04, 5, 21, 63, 30, 2),
    IndicatorDefinition("dxy", "DXY Proxy", "FX", "index", "yahoo", "DX-Y.NYB", True, "pct", 0.35, 5, 21, 63, 30, 2),
    IndicatorDefinition("wti", "WTI Crude", "Commodities", "usd", "yahoo", "CL=F", True, "pct", 1.2, 5, 21, 63, 30, 2),
    IndicatorDefinition("gold", "Gold", "Commodities", "usd", "yahoo", "GC=F", True, "pct", 0.8, 5, 21, 63, 30, 2),
    IndicatorDefinition("copper", "Copper", "Commodities", "usd", "yahoo", "HG=F", True, "pct", 0.9, 5, 21, 63, 30, 2),
    IndicatorDefinition("cpi_yoy", "CPI YoY", "Inflation", "%", "fred", "CPIAUCSL", True, "absolute", 0.08, 1, 1, 3, 24, 2, "yoy"),
    IndicatorDefinition("core_cpi_yoy", "Core CPI YoY", "Inflation", "%", "fred", "CPILFESL", True, "absolute", 0.06, 1, 1, 3, 24, 2, "yoy"),
    IndicatorDefinition("unemployment_rate", "Unemployment Rate", "Labor", "%", "fred", "UNRATE", True, "absolute", 0.05, 1, 1, 3, 24, 2),
    IndicatorDefinition("fed_funds_rate", "Fed Funds Rate", "Policy", "%", "fred", "FEDFUNDS", True, "absolute", 0.05, 1, 1, 3, 24, 2),
    IndicatorDefinition("hyg", "HYG ETF", "Credit", "usd", "yahoo", "HYG", False, "pct", 0.5, 5, 21, 63, 30, 2),
    IndicatorDefinition("lqd", "LQD ETF", "Credit", "usd", "yahoo", "LQD", False, "pct", 0.4, 5, 21, 63, 30, 2),
    IndicatorDefinition("xle", "Energy Select Sector SPDR", "Sectors", "usd", "yahoo", "XLE", False, "pct", 0.6, 5, 21, 63, 30, 2),
    IndicatorDefinition("qqq", "Invesco QQQ", "Equities", "usd", "yahoo", "QQQ", False, "pct", 0.5, 5, 21, 63, 30, 2),
    IndicatorDefinition("iwm", "iShares Russell 2000 ETF", "Equities", "usd", "yahoo", "IWM", False, "pct", 0.6, 5, 21, 63, 30, 2),
    IndicatorDefinition("xlf", "Financial Select Sector SPDR", "Sectors", "usd", "yahoo", "XLF", False, "pct", 0.5, 5, 21, 63, 30, 2),
]

INDICATOR_MAP = {definition.code: definition for definition in INDICATOR_DEFINITIONS}
FEATURED_INDICATORS = [definition.code for definition in INDICATOR_DEFINITIONS if definition.featured]
