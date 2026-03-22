from __future__ import annotations


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def safe_pct_change(current: float, previous: float) -> float | None:
    if abs(previous) < 1e-9:
        return None
    return ((current / previous) - 1.0) * 100
