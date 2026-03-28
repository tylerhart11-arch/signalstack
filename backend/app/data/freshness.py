from __future__ import annotations


MONTHLY_MACRO_SERIES_CODES = {"cpi_yoy", "core_cpi_yoy", "unemployment_rate", "fed_funds_rate"}


def max_staleness_days(indicator_code: str) -> int:
    return 75 if indicator_code in MONTHLY_MACRO_SERIES_CODES else 10


def source_mode(source: str) -> str:
    normalized = source.lower()
    if normalized.startswith("live"):
        return "live"
    if "fallback" in normalized:
        return "fallback"
    if normalized.startswith("mixed"):
        return "mixed"
    if normalized.startswith("demo") or normalized == "mock":
        return "demo"
    return "unknown"
