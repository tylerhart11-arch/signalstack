import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_health_endpoint_reports_database_status(tmp_path: Path) -> None:
    db_path = tmp_path / "signalstack_health.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["SIGNALSTACK_USE_DEMO_DATA"] = "true"
    os.environ["SIGNALSTACK_REFRESH_ON_STARTUP"] = "true"

    import app.core.config as config_module

    config_module.get_settings.cache_clear()

    import app.core.database as database_module

    importlib.reload(database_module)
    import app.models.indicator_snapshot as indicator_snapshot_module
    import app.models.regime_history as regime_history_module
    import app.models.anomaly_item as anomaly_item_module
    import app.models.saved_thesis as saved_thesis_module
    import app.models.alert_config as alert_config_module
    import app.models.alert_event as alert_event_module
    import app.models.refresh_run as refresh_run_module

    importlib.reload(indicator_snapshot_module)
    importlib.reload(regime_history_module)
    importlib.reload(anomaly_item_module)
    importlib.reload(saved_thesis_module)
    importlib.reload(alert_config_module)
    importlib.reload(alert_event_module)
    importlib.reload(refresh_run_module)
    import app.data.refresh as refresh_module

    importlib.reload(refresh_module)
    import app.main as main_module

    importlib.reload(main_module)

    with TestClient(main_module.app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["database"] == "connected"
        assert payload["indicator_snapshots"] > 0
