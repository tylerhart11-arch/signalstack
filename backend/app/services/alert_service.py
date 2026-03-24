from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.alert_config import AlertConfig
from app.models.alert_event import AlertEvent
from app.models.refresh_run import RefreshRun
from app.models.regime_history import RegimeHistory
from app.schemas.alerts import AlertConfigResponse, AlertConfigUpdate, AlertEventResponse, AlertHistoryResponse
from app.services.anomaly_service import AnomalyService
from app.services.regime_service import RegimeService
from app.services.system_service import SystemService
from app.utils.dates import utc_now


class AlertService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.market_timezone = ZoneInfo(self.settings.market_timezone)
        self.anomaly_service = AnomalyService()
        self.regime_service = RegimeService()
        self.system_service = SystemService(self.settings)

    def get_config(self, session: Session) -> AlertConfigResponse:
        config = self._ensure_config(session)
        session.commit()
        session.refresh(config)
        return self._serialize_config(config)

    def update_config(self, session: Session, payload: AlertConfigUpdate) -> AlertConfigResponse:
        config = self._ensure_config(session)
        config.regime_change_enabled = payload.regime_change_enabled
        config.anomaly_severity_threshold = payload.anomaly_severity_threshold
        config.digest_cadence = payload.digest_cadence
        session.add(config)
        session.commit()
        session.refresh(config)
        return self._serialize_config(config)

    def list_history(self, session: Session, limit: int = 40) -> AlertHistoryResponse:
        rows = session.execute(
            select(AlertEvent).order_by(AlertEvent.created_at.desc(), AlertEvent.id.desc()).limit(limit)
        ).scalars().all()
        return AlertHistoryResponse(items=[self._serialize_event(row) for row in rows])

    def run_manual_digest(self, session: Session) -> AlertEventResponse:
        event = self._create_digest_event(
            session=session,
            cadence="manual",
            event_key=f"digest:manual:{utc_now().isoformat()}",
        )
        session.commit()
        session.refresh(event)
        return self._serialize_event(event)

    def process_refresh_cycle(self, session: Session, refresh_run: RefreshRun) -> None:
        config = self._ensure_config(session)
        self._record_regime_change(session=session, config=config)
        self._record_anomaly_alerts(session=session, config=config)

        for cadence in self._due_digest_cadences(config=config, completed_at=refresh_run.completed_at):
            local_date = refresh_run.completed_at.astimezone(self.market_timezone).date().isoformat()
            self._create_digest_event(
                session=session,
                cadence=cadence,
                event_key=f"digest:{cadence}:{local_date}",
            )

    def _ensure_config(self, session: Session) -> AlertConfig:
        config = session.get(AlertConfig, 1)
        if config is None:
            config = AlertConfig(id=1)
            session.add(config)
            session.flush()
        return config

    def _record_regime_change(self, session: Session, config: AlertConfig) -> None:
        if not config.regime_change_enabled:
            return

        history = session.execute(select(RegimeHistory).order_by(RegimeHistory.as_of.desc()).limit(2)).scalars().all()
        if len(history) < 2 or history[0].regime == history[1].regime:
            return

        current, previous = history[0], history[1]
        confidence_pct = round(current.confidence * 100)
        event_key = f"regime:{previous.regime}:{current.regime}:{current.as_of.isoformat()}"
        self._create_event_if_missing(
            session=session,
            event_key=event_key,
            event_type="regime_change",
            title=f"Regime shift: {current.regime}",
            message=(
                f"SignalStack moved from {previous.regime} to {current.regime} at {current.as_of.date().isoformat()} "
                f"with {confidence_pct}% confidence. {current.summary}"
            ),
            severity=max(55, confidence_pct),
            cadence=None,
            payload={
                "current_regime": current.regime,
                "previous_regime": previous.regime,
                "confidence": current.confidence,
                "as_of": current.as_of.isoformat(),
            },
        )

    def _record_anomaly_alerts(self, session: Session, config: AlertConfig) -> None:
        anomalies = self.anomaly_service.list_current(session=session, limit=20)
        for item in anomalies.items:
            if item.severity < config.anomaly_severity_threshold:
                continue

            event_key = f"anomaly:{item.rule_code}:{item.detected_at.isoformat()}"
            assets = ", ".join(item.related_assets[:3]) if item.related_assets else "cross-asset tape"
            self._create_event_if_missing(
                session=session,
                event_key=event_key,
                event_type="anomaly",
                title=item.title,
                message=f"{item.explanation} Focus assets: {assets}.",
                severity=item.severity,
                cadence=None,
                payload={
                    "rule_code": item.rule_code,
                    "detected_at": item.detected_at.isoformat(),
                    "related_assets": item.related_assets,
                },
            )

    def _due_digest_cadences(self, *, config: AlertConfig, completed_at: datetime | None) -> list[str]:
        if completed_at is None or config.digest_cadence == "manual":
            return []

        local_completed = completed_at.astimezone(self.market_timezone)
        open_due = self._is_near_boundary(
            local_completed,
            hour=self.settings.market_open_hour,
            minute=self.settings.market_open_minute,
        )
        close_due = self._is_near_boundary(
            local_completed,
            hour=self.settings.market_close_hour,
            minute=self.settings.market_close_minute,
        )

        due: list[str] = []
        if config.digest_cadence in {"market_open", "both"} and open_due:
            due.append("market_open")
        if config.digest_cadence in {"market_close", "both"} and close_due:
            due.append("market_close")
        return due

    def _is_near_boundary(self, completed_at: datetime, *, hour: int, minute: int) -> bool:
        boundary = completed_at.replace(hour=hour, minute=minute, second=0, microsecond=0)
        delta = completed_at - boundary
        return timedelta(0) <= delta <= timedelta(minutes=10)

    def _create_digest_event(self, session: Session, *, cadence: str, event_key: str) -> AlertEvent:
        existing = session.execute(select(AlertEvent).where(AlertEvent.event_key == event_key)).scalars().first()
        if existing is not None:
            return existing

        current = self.regime_service.get_current(session=session)
        anomalies = self.anomaly_service.list_current(session=session, limit=3)
        refresh_status = self.system_service.get_refresh_status(session=session)

        anomaly_titles = [f"{item.title} ({item.severity})" for item in anomalies.items[:3]]
        stale_names = [item.name for item in refresh_status.stale_indicators[:3]]
        cadence_label = {
            "manual": "Manual digest",
            "market_open": "Open digest",
            "market_close": "Close digest",
        }.get(cadence, "Digest")
        anomaly_line = (
            f"Top anomalies: {', '.join(anomaly_titles)}."
            if anomaly_titles
            else "No active anomaly alerts cleared the configured threshold."
        )
        stale_line = (
            f"Stale indicators to review: {', '.join(stale_names)}."
            if stale_names
            else "No stale indicators were detected in the current snapshot."
        )
        message = (
            f"{current.regime} is the active regime at {round(current.confidence * 100)}% confidence. {current.summary} "
            f"{anomaly_line} Data status is {refresh_status.status} ({refresh_status.source_summary}); "
            f"next scheduled refresh {refresh_status.next_scheduled_refresh.isoformat()}. {stale_line}"
        )

        event = AlertEvent(
            event_type="digest",
            title=f"{cadence_label}: {current.regime}",
            message=message,
            severity=None,
            cadence=cadence,
            event_key=event_key,
            payload={
                "regime": current.regime,
                "confidence": current.confidence,
                "source_summary": refresh_status.source_summary,
                "system_status": refresh_status.status,
                "top_anomalies": anomaly_titles,
                "stale_indicators": stale_names,
            },
        )
        session.add(event)
        session.flush()
        return event

    def _create_event_if_missing(
        self,
        *,
        session: Session,
        event_key: str,
        event_type: str,
        title: str,
        message: str,
        severity: int | None,
        cadence: str | None,
        payload: dict,
    ) -> AlertEvent | None:
        existing = session.execute(select(AlertEvent).where(AlertEvent.event_key == event_key)).scalars().first()
        if existing is not None:
            return None

        event = AlertEvent(
            event_type=event_type,
            title=title,
            message=message,
            severity=severity,
            cadence=cadence,
            event_key=event_key,
            payload=payload,
        )
        session.add(event)
        session.flush()
        return event

    def _serialize_config(self, config: AlertConfig) -> AlertConfigResponse:
        return AlertConfigResponse(
            regime_change_enabled=config.regime_change_enabled,
            anomaly_severity_threshold=config.anomaly_severity_threshold,
            digest_cadence=config.digest_cadence,
            updated_at=config.updated_at,
        )

    def _serialize_event(self, event: AlertEvent) -> AlertEventResponse:
        return AlertEventResponse(
            id=event.id,
            event_type=event.event_type,
            title=event.title,
            message=event.message,
            severity=event.severity,
            cadence=event.cadence,
            payload=event.payload or {},
            created_at=event.created_at,
        )
