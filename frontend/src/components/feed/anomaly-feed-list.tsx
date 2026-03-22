import { Card } from "@/components/ui/card";
import { AnomalyResponse } from "@/lib/types";

import { AnomalyFeedItem } from "./anomaly-feed-item";

export function AnomalyFeedList({ data }: { data: AnomalyResponse }) {
  if (!data.items.length) {
    return (
      <Card title="No anomalies detected" eyebrow="Feed">
        <p className="text-sm leading-7 text-shell-muted">
          The scanner did not find any threshold breaches in the current window. That usually means the live or demo tape is internally consistent.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {data.items.map((item, index) => (
        <AnomalyFeedItem key={`${item.rule_code}-${item.detected_at}`} item={item} rank={index + 1} />
      ))}
    </div>
  );
}
