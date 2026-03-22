from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.anomaly_item import AnomalyItem
from app.schemas.anomaly import AnomalyItemResponse, AnomalyResponse


class AnomalyService:
    def list_current(self, session: Session, limit: int = 20) -> AnomalyResponse:
        rows = session.execute(
            select(AnomalyItem).order_by(AnomalyItem.detected_at.desc(), AnomalyItem.severity.desc()).limit(limit * 3)
        ).scalars().all()

        deduped: dict[str, AnomalyItem] = {}
        for item in rows:
            existing = deduped.get(item.rule_code)
            if existing is None or item.severity > existing.severity:
                deduped[item.rule_code] = item

        items = sorted(deduped.values(), key=lambda item: (item.severity, item.detected_at), reverse=True)[:limit]
        return AnomalyResponse(
            as_of=max((item.detected_at for item in items), default=None),
            items=[
                AnomalyItemResponse(
                    id=item.id,
                    detected_at=item.detected_at,
                    rule_code=item.rule_code,
                    title=item.title,
                    explanation=item.explanation,
                    category=item.category,
                    severity=item.severity,
                    related_assets=item.related_assets,
                    supporting_metrics=item.supporting_metrics,
                )
                for item in items
            ],
        )
