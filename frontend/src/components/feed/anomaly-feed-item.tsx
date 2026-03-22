import { SeverityBadge } from "@/components/feed/severity-badge";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatMetricValue, formatTimestamp, metricLabel } from "@/lib/format";
import { AnomalyItem } from "@/lib/types";

export function AnomalyFeedItem({ item, rank }: { item: AnomalyItem; rank: number }) {
  return (
    <Card title={item.title} eyebrow={item.category} action={<SeverityBadge severity={item.severity} />}>
      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">Priority {rank}</Badge>
            {item.related_assets.map((asset) => (
              <Badge key={asset} tone="neutral">
                {asset}
              </Badge>
            ))}
          </div>

          <p className="text-sm leading-7 text-shell-muted">{item.explanation}</p>

          <div>
            <div className="mb-2 flex items-center justify-between text-[11px] uppercase tracking-[0.18em] text-shell-muted">
              <span>Severity Ladder</span>
              <span>{item.severity}/100</span>
            </div>
            <div className="h-2 rounded-full bg-white/5">
              <div className="h-2 rounded-full bg-gradient-to-r from-shell-accent via-shell-warn to-shell-danger" style={{ width: `${Math.max(8, item.severity)}%` }} />
            </div>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          {Object.entries(item.supporting_metrics).map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-shell-border bg-black/10 p-4">
              <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">{metricLabel(label)}</p>
              <p className="mt-2 font-mono text-lg text-shell-text">{formatMetricValue(value)}</p>
            </div>
          ))}
        </div>
      </div>

      <p className="mt-4 text-[11px] uppercase tracking-[0.18em] text-shell-muted">Detected {formatTimestamp(item.detected_at)}</p>
    </Card>
  );
}
