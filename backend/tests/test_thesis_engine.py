import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engines.thesis_engine import ThesisEngine


def test_thesis_engine_matches_ai_theme() -> None:
    engine = ThesisEngine()
    result = engine.analyze("AI data centers will drive electricity demand higher.")
    assert result.interpreted_theme == "AI infrastructure power squeeze"
    assert result.etf_exposures
    assert result.confirming_signals
