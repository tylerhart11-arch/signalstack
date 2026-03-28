import { Card } from "@/components/ui/card";
import { AnomalyItem } from "@/lib/types";

import { AnomalyFeedItem } from "./anomaly-feed-item";

export function AnomalyFeedList({
  items,
  hasActiveFilters,
  totalCount,
}: {
  items: AnomalyItem[];
  hasActiveFilters: boolean;
  totalCount: number;
}) {
  if (!items.length) {
    return (
      <Card title={hasActiveFilters ? "No anomalies match the current search" : "No anomalies detected"} eyebrow="Feed">
        <p className="text-sm leading-7 text-shell-muted">
          {hasActiveFilters
            ? `The page still has ${totalCount} anomaly ${totalCount === 1 ? "item" : "items"} available, but none match the current search and filter state. Try resetting the search, severity, category, or asset lens.`
            : "The scanner did not find any threshold breaches in the current window. That usually means the live tape is internally consistent."}
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <AnomalyFeedItem key={`${item.rule_code}-${item.detected_at}`} item={item} rank={index + 1} />
      ))}
    </div>
  );
}
