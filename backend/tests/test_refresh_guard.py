import importlib
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_modules(tmp_path: Path):
    db_path = tmp_path / "signalstack_refresh_guard.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["SIGNALSTACK_REFRESH_ON_STARTUP"] = "false"
    os.environ["SIGNALSTACK_BACKGROUND_REFRESH_ENABLED"] = "false"

    import app.core.config as config_module

    config_module.get_settings.cache_clear()

    import app.core.database as database_module

    importlib.reload(database_module)

    import app.models.refresh_run as refresh_run_module

    importlib.reload(refresh_run_module)

    import app.data.refresh as refresh_module

    importlib.reload(refresh_module)

    import app.data.refresh_guard as refresh_guard_module

    importlib.reload(refresh_guard_module)

    refresh_module.Base.metadata.create_all(bind=refresh_module.engine)

    return {
        "config": config_module,
        "database": database_module,
        "refresh": refresh_module,
        "refresh_guard": refresh_guard_module,
        "refresh_run": refresh_run_module,
    }


def test_ensure_daily_refresh_runs_when_no_successful_refresh_exists(tmp_path: Path) -> None:
    modules = load_modules(tmp_path)
    refresh_guard_module = modules["refresh_guard"]
    database_module = modules["database"]

    called = {"count": 0}

    def fake_refresh_application_data(settings):
        called["count"] += 1
        return "live"

    refresh_guard_module.refresh_application_data = fake_refresh_application_data

    with database_module.SessionLocal() as session:
        refresh_guard_module.ensure_daily_refresh(
            session=session,
            now=datetime(2026, 4, 1, 14, 0, tzinfo=UTC),
        )

    assert called["count"] == 1


def test_ensure_daily_refresh_runs_when_last_success_was_previous_market_day(tmp_path: Path) -> None:
    modules = load_modules(tmp_path)
    refresh_guard_module = modules["refresh_guard"]
    database_module = modules["database"]
    refresh_run_module = modules["refresh_run"]

    called = {"count": 0}

    def fake_refresh_application_data(settings):
        called["count"] += 1
        return "live"

    refresh_guard_module.refresh_application_data = fake_refresh_application_data

    with database_module.SessionLocal() as session:
        session.add(
            refresh_run_module.RefreshRun(
                started_at=datetime(2026, 3, 31, 11, 0, tzinfo=UTC),
                completed_at=datetime(2026, 3, 31, 11, 5, tzinfo=UTC),
                status="success",
                source_summary="live",
            )
        )
        session.commit()

        refresh_guard_module.ensure_daily_refresh(
            session=session,
            now=datetime(2026, 4, 1, 14, 0, tzinfo=UTC),
        )

    assert called["count"] == 1


def test_ensure_daily_refresh_skips_when_last_success_is_same_market_day(tmp_path: Path) -> None:
    modules = load_modules(tmp_path)
    refresh_guard_module = modules["refresh_guard"]
    database_module = modules["database"]
    refresh_run_module = modules["refresh_run"]

    called = {"count": 0}

    def fake_refresh_application_data(settings):
        called["count"] += 1
        return "live"

    refresh_guard_module.refresh_application_data = fake_refresh_application_data

    with database_module.SessionLocal() as session:
        session.add(
            refresh_run_module.RefreshRun(
                started_at=datetime(2026, 4, 1, 10, 0, tzinfo=UTC),
                completed_at=datetime(2026, 4, 1, 10, 2, tzinfo=UTC),
                status="success",
                source_summary="live",
            )
        )
        session.commit()

        refresh_guard_module.ensure_daily_refresh(
            session=session,
            now=datetime(2026, 4, 1, 18, 0, tzinfo=UTC),
        )

        success_runs = session.execute(select(refresh_run_module.RefreshRun)).scalars().all()

    assert called["count"] == 0
    assert len(success_runs) == 1
