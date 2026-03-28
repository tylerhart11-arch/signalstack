import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_test_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "signalstack_automation.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["SIGNALSTACK_REFRESH_ON_STARTUP"] = "false"
    os.environ["SIGNALSTACK_BACKGROUND_REFRESH_ENABLED"] = "false"

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

    from app.data.mappers.indicator_mapper import INDICATOR_MAP
    from app.data.providers.demo_provider import generate_demo_history

    def fake_load_live_history(self, effective_date):
        history = {
            code: list(points)
            for code, points in generate_demo_history(
                effective_date,
                periods=self.settings.market_lookback_days,
            ).items()
            if code in INDICATOR_MAP and INDICATOR_MAP[code].provider != "derived"
        }
        sources = {code: f"live-{INDICATOR_MAP[code].provider}" for code in history}
        self._build_derived_series(history, sources)
        return history, sources

    refresh_module.DataRefreshService._load_live_history = fake_load_live_history
    refresh_module.Base.metadata.create_all(bind=refresh_module.engine)
    refresh_module.refresh_application_data(settings=config_module.get_settings())

    import app.main as main_module

    importlib.reload(main_module)
    return TestClient(main_module.app)


def test_refresh_status_and_alert_routes_work_end_to_end(tmp_path: Path) -> None:
    with build_test_client(tmp_path) as client:
        status_response = client.get("/api/system/refresh-status")
        assert status_response.status_code == 200
        status_payload = status_response.json()
        assert status_payload["mode"] == "live-only"
        assert status_payload["last_success_at"] is not None
        assert status_payload["source_summary"] == "live"
        assert status_payload["provider_statuses"]

        config_response = client.get("/api/alerts/config")
        assert config_response.status_code == 200
        config_payload = config_response.json()
        assert config_payload["regime_change_enabled"] is True
        assert config_payload["anomaly_severity_threshold"] == 75

        update_response = client.put(
            "/api/alerts/config",
            json={
                "regime_change_enabled": False,
                "anomaly_severity_threshold": 80,
                "digest_cadence": "both",
            },
        )
        assert update_response.status_code == 200
        updated_payload = update_response.json()
        assert updated_payload["regime_change_enabled"] is False
        assert updated_payload["anomaly_severity_threshold"] == 80
        assert updated_payload["digest_cadence"] == "both"

        digest_response = client.post("/api/alerts/run-digest")
        assert digest_response.status_code == 200
        digest_payload = digest_response.json()
        assert digest_payload["event_type"] == "digest"
        assert digest_payload["cadence"] == "manual"

        history_response = client.get("/api/alerts/history")
        assert history_response.status_code == 200
        history_payload = history_response.json()
        assert any(item["event_type"] == "digest" for item in history_payload["items"])
        assert any(item["event_type"] == "anomaly" for item in history_payload["items"])
