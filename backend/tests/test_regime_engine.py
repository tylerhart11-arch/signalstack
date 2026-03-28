import sys
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.mappers.indicator_mapper import INDICATOR_MAP
from app.data.providers.demo_provider import generate_demo_history
from app.engines.regime_engine import RegimeEngine
from app.services.overview_service import IndicatorState, SnapshotRecord


def test_regime_engine_returns_supported_label() -> None:
    history = generate_demo_history(datetime.now(UTC), periods=120)
    states = {
        code: IndicatorState(
            definition=INDICATOR_MAP[code],
            history=[SnapshotRecord(timestamp=point.timestamp, value=point.value) for point in points],
            source="live-test",
        )
        for code, points in history.items()
        if code in INDICATOR_MAP
    }
    engine = RegimeEngine()
    result = engine.evaluate(states=states, as_of=states["sp500"].last_updated)
    assert result.regime in {
        "Disinflationary Growth",
        "Inflationary Expansion",
        "Slowdown",
        "Recession Risk",
        "Liquidity Expansion",
        "Stress / Crisis",
    }
    assert 0.45 <= result.confidence <= 0.93
