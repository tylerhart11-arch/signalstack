from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, date, datetime

import pandas as pd


@dataclass(frozen=True)
class SeriesPoint:
    timestamp: datetime
    value: float


def _smooth_series(start: float, end: float, length: int, amplitude: float, cycles: float = 2.0) -> list[float]:
    values: list[float] = []
    if length <= 1:
        return [round(end, 4)]
    for index in range(length):
        progress = index / (length - 1)
        base = start + (end - start) * progress
        wave = math.sin(progress * math.pi * cycles) * amplitude
        secondary = math.cos(progress * math.pi * (cycles + 0.7)) * amplitude * 0.35
        values.append(round(base + wave + secondary, 4))
    return values


def _macro_step_series(start: float, end: float, length: int, steps: int, amplitude: float) -> list[float]:
    anchors = _smooth_series(start, end, steps, amplitude * 0.35, cycles=1.4)
    bucket_size = max(1, length // max(1, steps - 1))
    values: list[float] = []
    for index in range(length):
        anchor_index = min(len(anchors) - 1, index // bucket_size)
        drift = math.sin(index / 9) * amplitude
        values.append(round(anchors[anchor_index] + drift, 4))
    return values


def _apply_tail_shift(values: list[float], window: int, total_shift: float, mode: str = "absolute") -> list[float]:
    if not values:
        return values

    adjusted = values[:]
    window = max(1, min(window, len(adjusted)))
    start_index = len(adjusted) - window

    for offset, index in enumerate(range(start_index, len(adjusted))):
        progress = (offset + 1) / window
        if mode == "pct":
            adjusted[index] = round(adjusted[index] * (1 + total_shift * progress), 4)
        else:
            adjusted[index] = round(adjusted[index] + total_shift * progress, 4)

    return adjusted


def generate_demo_history(as_of: date | datetime, periods: int = 160) -> dict[str, list[SeriesPoint]]:
    end_date = as_of.date() if isinstance(as_of, datetime) else as_of
    dates = pd.bdate_range(end=end_date, periods=periods)
    date_list = [timestamp.to_pydatetime().replace(tzinfo=UTC) for timestamp in dates]
    length = len(date_list)

    market_specs = {
        "sp500": (5005.0, 5325.0, 48.0),
        "nasdaq100": (17350.0, 18890.0, 180.0),
        "russell2000": (2205.0, 2142.0, 28.0),
        "vix": (16.8, 18.6, 1.8),
        "us2y": (4.92, 4.46, 0.06),
        "us10y": (4.54, 4.17, 0.05),
        "hy_spread": (3.62, 4.18, 0.08),
        "ig_spread": (1.08, 1.28, 0.04),
        "dxy": (105.2, 103.3, 0.45),
        "wti": (73.5, 79.6, 1.4),
        "gold": (2140.0, 2298.0, 18.0),
        "copper": (4.02, 4.46, 0.06),
        "hyg": (79.2, 77.4, 0.35),
        "lqd": (109.5, 108.7, 0.25),
        "xle": (86.0, 88.8, 1.2),
        "qqq": (435.0, 468.0, 4.5),
        "iwm": (216.0, 207.0, 2.8),
        "xlf": (42.8, 41.7, 0.75),
    }

    macro_specs = {
        "cpi_yoy": (3.55, 2.93, 0.03),
        "core_cpi_yoy": (3.92, 3.18, 0.03),
        "unemployment_rate": (3.78, 4.09, 0.015),
        "fed_funds_rate": (5.38, 5.13, 0.01),
    }

    history: dict[str, list[SeriesPoint]] = {}

    for code, (start, end, amplitude) in market_specs.items():
        values = _smooth_series(start, end, length, amplitude)
        history[code] = [SeriesPoint(timestamp=timestamp, value=value) for timestamp, value in zip(date_list, values, strict=True)]

    for code, (start, end, amplitude) in macro_specs.items():
        values = _macro_step_series(start, end, length, steps=8, amplitude=amplitude)
        history[code] = [SeriesPoint(timestamp=timestamp, value=value) for timestamp, value in zip(date_list, values, strict=True)]

    # Add a deliberate late-cycle macro pattern so the MVP surfaces meaningful
    # cross-asset divergences on first boot instead of empty anomaly feeds.
    shock_plan = {
        "sp500": (5, 0.018, "pct"),
        "vix": (5, 0.12, "pct"),
        "hy_spread": (5, 0.18, "absolute"),
        "ig_spread": (5, 0.05, "absolute"),
        "wti": (10, 0.055, "pct"),
        "xle": (10, 0.004, "pct"),
        "us10y": (21, 0.14, "absolute"),
        "us2y": (21, -0.02, "absolute"),
        "cpi_yoy": (3, -0.08, "absolute"),
        "core_cpi_yoy": (3, -0.04, "absolute"),
        "qqq": (21, 0.055, "pct"),
        "iwm": (21, -0.02, "pct"),
        "xlf": (21, -0.025, "pct"),
    }

    for code, (window, total_shift, mode) in shock_plan.items():
        adjusted_values = _apply_tail_shift([point.value for point in history[code]], window, total_shift, mode)
        history[code] = [
            SeriesPoint(timestamp=timestamp, value=value)
            for timestamp, value in zip(date_list, adjusted_values, strict=True)
        ]

    history["s2s10s"] = [
        SeriesPoint(timestamp=timestamp, value=round((ten_year.value - two_year.value) * 100, 2))
        for timestamp, two_year, ten_year in zip(
            date_list,
            history["us2y"],
            history["us10y"],
            strict=True,
        )
    ]

    return history
