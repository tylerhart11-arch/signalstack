from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.data.mappers.indicator_mapper import INDICATOR_DEFINITIONS
from app.data.freshness import max_staleness_days, source_mode
from app.models.alert_event import AlertEvent
from app.models.refresh_run import RefreshRun
from app.schemas.system import ProviderStatusResponse, RefreshStatusResponse, StaleIndicatorResponse
from app.services.overview_service import OverviewService
from app.utils.dates import coerce_utc_datetime, utc_now


class SystemService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.overview_service = OverviewService()

    def get_refresh_status(self, session: Session) -> RefreshStatusResponse:
        from app.data.scheduler import next_refresh_at

        states = self.overview_service.build_indicator_states(session=session)
        now = utc_now()
        latest_success = session.execute(
            select(RefreshRun).where(RefreshRun.status == "success").order_by(RefreshRun.completed_at.desc(), RefreshRun.id.desc())
        ).scalars().first()

        expected_counts: dict[str, int] = defaultdict(int)
        for definition in INDICATOR_DEFINITIONS:
            expected_counts[definition.provider] += 1

        provider_buckets: dict[str, dict[str, int]] = defaultdict(
            lambda: {
                "expected_count": 0,
                "indicator_count": 0,
                "live_count": 0,
                "stale_count": 0,
            }
        )
        for provider, expected_count in expected_counts.items():
            provider_buckets[provider]["expected_count"] = expected_count
        stale_indicators: list[StaleIndicatorResponse] = []
        latest_indicator_at = max((state.last_updated for state in states.values()), default=None)

        for code, state in states.items():
            threshold = max_staleness_days(code)
            age_days = max(0, (now.date() - state.last_updated.date()).days)
            is_stale = age_days > threshold
            bucket = provider_buckets[state.definition.provider]
            bucket["indicator_count"] += 1
            mode = source_mode(state.source)
            if mode == "live":
                bucket["live_count"] += 1
            if is_stale:
                bucket["stale_count"] += 1
                stale_indicators.append(
                    StaleIndicatorResponse(
                        code=code,
                        name=state.definition.name,
                        last_updated=state.last_updated,
                        age_days=age_days,
                        source=state.source,
                        max_staleness_days=threshold,
                    )
                )

        provider_statuses = [
            ProviderStatusResponse(
                provider=provider,
                status=self._provider_status(bucket),
                expected_count=bucket["expected_count"],
                indicator_count=bucket["indicator_count"],
                live_count=bucket["live_count"],
                stale_count=bucket["stale_count"],
            )
            for provider, bucket in sorted(provider_buckets.items())
        ]

        last_digest_at = session.scalar(select(func.max(AlertEvent.created_at)).where(AlertEvent.event_type == "digest"))
        recent_alert_count = session.scalar(
            select(func.count(AlertEvent.id)).where(
                AlertEvent.created_at >= now - timedelta(hours=24),
                AlertEvent.event_type != "digest",
            )
        ) or 0

        derived_source_summary = self._derive_source_summary(provider_statuses)
        last_live_refresh = (
            latest_success
            if latest_success is not None and latest_success.source_summary in {"live", "partial-live"}
            else None
        )

        return RefreshStatusResponse(
            mode="live-only",
            status=self._overall_status(provider_statuses=provider_statuses, stale_indicators=stale_indicators),
            last_success_at=self._normalize_optional_datetime(last_live_refresh.completed_at)
            if last_live_refresh is not None
            else latest_indicator_at,
            latest_indicator_at=self._normalize_optional_datetime(last_live_refresh.latest_indicator_at)
            if last_live_refresh is not None
            else latest_indicator_at,
            source_summary=last_live_refresh.source_summary if last_live_refresh is not None else derived_source_summary,
            next_scheduled_refresh=next_refresh_at(now, self.settings),
            stale_indicators=sorted(stale_indicators, key=lambda item: (item.age_days, item.name), reverse=True),
            provider_statuses=provider_statuses,
            last_digest_at=self._normalize_optional_datetime(last_digest_at),
            recent_alert_count=int(recent_alert_count),
        )

    def _normalize_optional_datetime(self, value):
        if value is None:
            return None
        return coerce_utc_datetime(value)

    def _provider_status(self, bucket: dict[str, int]) -> str:
        if bucket["live_count"] == 0:
            return "unavailable"
        if bucket["stale_count"] > 0:
            return "stale"
        if bucket["live_count"] < bucket["expected_count"]:
            return "partial-live"
        if bucket["live_count"] == bucket["expected_count"]:
            return "live"
        return "unavailable"

    def _derive_source_summary(self, provider_statuses: list[ProviderStatusResponse]) -> str:
        if not provider_statuses:
            return "no-live-data"
        statuses = {item.status for item in provider_statuses}
        if statuses == {"live"}:
            return "live"
        if statuses == {"unavailable"}:
            return "no-live-data"
        if "stale" in statuses:
            return "stale-live"
        if "partial-live" in statuses or "unavailable" in statuses:
            return "partial-live"
        if "stale" in statuses:
            return "stale"
        return "unknown"

    def _overall_status(
        self,
        *,
        provider_statuses: list[ProviderStatusResponse],
        stale_indicators: list[StaleIndicatorResponse],
    ) -> str:
        if stale_indicators:
            return "stale"
        if provider_statuses and all(item.status == "unavailable" for item in provider_statuses):
            return "unavailable"
        if any(item.status in {"partial-live", "unavailable"} for item in provider_statuses):
            return "degraded"
        if provider_statuses and all(item.status == "live" for item in provider_statuses):
            return "fresh"
        return "unavailable"
