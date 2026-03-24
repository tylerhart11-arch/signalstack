import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_test_modules(tmp_path: Path):
    db_path = tmp_path / "signalstack_refresh_flow.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["SIGNALSTACK_USE_DEMO_DATA"] = "true"
    os.environ["SIGNALSTACK_REFRESH_ON_STARTUP"] = "false"
    os.environ["SIGNALSTACK_BACKGROUND_REFRESH_ENABLED"] = "false"

    for module_name in [name for name in sys.modules if name == "app" or name.startswith("app.")]:
        sys.modules.pop(module_name)

    import app.core.config as config_module

    config_module.get_settings.cache_clear()

    import app.core.database as database_module
    import app.models.indicator_snapshot as indicator_snapshot_module
    import app.models.regime_history as regime_history_module
    import app.models.anomaly_item as anomaly_item_module
    import app.models.saved_thesis as saved_thesis_module
    import app.models.alert_config as alert_config_module
    import app.models.alert_event as alert_event_module
    import app.models.refresh_run as refresh_run_module
    import app.data.refresh as refresh_module
    import app.main as main_module

    return {
        "config": config_module,
        "database": database_module,
        "refresh": refresh_module,
        "main": main_module,
        "indicator_snapshot": indicator_snapshot_module,
        "refresh_run": refresh_run_module,
        "regime_history": regime_history_module,
        "anomaly_item": anomaly_item_module,
        "saved_thesis": saved_thesis_module,
        "alert_config": alert_config_module,
        "alert_event": alert_event_module,
    }


def test_refresh_application_data_can_run_twice_without_duplicate_snapshot_failures(tmp_path: Path) -> None:
    modules = load_test_modules(tmp_path)
    config_module = modules["config"]
    database_module = modules["database"]
    refresh_module = modules["refresh"]
    indicator_snapshot_module = modules["indicator_snapshot"]
    refresh_run_module = modules["refresh_run"]

    refresh_module.Base.metadata.create_all(bind=refresh_module.engine)
    settings = config_module.get_settings()

    assert refresh_module.refresh_application_data(settings=settings) == "demo"
    assert refresh_module.refresh_application_data(settings=settings) == "demo"

    with database_module.SessionLocal() as session:
        snapshot_count = session.scalar(select(func.count(indicator_snapshot_module.IndicatorSnapshot.id))) or 0
        distinct_snapshot_count = session.scalar(
            select(func.count()).select_from(
                select(
                    indicator_snapshot_module.IndicatorSnapshot.indicator_code,
                    indicator_snapshot_module.IndicatorSnapshot.timestamp,
                )
                .distinct()
                .subquery()
            )
        )
        refresh_statuses = session.execute(
            select(refresh_run_module.RefreshRun.status).order_by(refresh_run_module.RefreshRun.id)
        ).scalars().all()

    assert snapshot_count > 0
    assert snapshot_count == distinct_snapshot_count
    assert refresh_statuses == ["success", "success"]


def test_hydrate_derived_tables_skips_early_anchor_dates_without_full_macro_history(tmp_path: Path) -> None:
    modules = load_test_modules(tmp_path)
    config_module = modules["config"]
    database_module = modules["database"]
    refresh_module = modules["refresh"]
    regime_history_module = modules["regime_history"]

    from app.data.providers.demo_provider import SeriesPoint, generate_demo_history

    refresh_module.Base.metadata.create_all(bind=refresh_module.engine)
    settings = config_module.get_settings()
    service = refresh_module.DataRefreshService(settings=settings)
    history = generate_demo_history(datetime(2026, 3, 24, tzinfo=UTC), periods=40)
    fred_backed_codes = {
        "cpi_yoy",
        "core_cpi_yoy",
        "unemployment_rate",
        "fed_funds_rate",
        "hy_spread",
        "ig_spread",
        "us2y",
        "us10y",
        "s2s10s",
    }

    for code, points in list(history.items()):
        if code in fred_backed_codes:
            continue

        start = points[0].timestamp
        prefix = [
            SeriesPoint(timestamp=start - timedelta(days=offset), value=points[0].value)
            for offset in range(8, 0, -1)
        ]
        history[code] = prefix + points

    sources = service._build_demo_source_map(history)

    with database_module.SessionLocal() as session:
        service._persist_history(session=session, history=history, sources=sources)
        refresh_module.hydrate_derived_tables(session=session)
        regime_count = session.scalar(select(func.count(regime_history_module.RegimeHistory.id))) or 0

    assert regime_count > 0


def test_local_network_frontend_origin_is_allowed_for_preflight(tmp_path: Path) -> None:
    modules = load_test_modules(tmp_path)
    main_module = modules["main"]

    with TestClient(main_module.app) as client:
        response = client.options(
            "/api/overview",
            headers={
                "Origin": "http://192.168.120.221:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://192.168.120.221:3000"
