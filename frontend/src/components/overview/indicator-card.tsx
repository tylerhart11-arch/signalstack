import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { StatPill } from "@/components/ui/stat-pill";
import { formatIndicatorChange, formatIndicatorValue } from "@/lib/format";
import { IndicatorOverview } from "@/lib/types";

import { MiniSparkline } from "./mini-sparkline";

function toneFromDirection(direction: string): "positive" | "warning" | "negative" {
  if (direction === "rising") {
    return "positive";
  }
  if (direction === "falling") {
    return "negative";
  }
  return "warning";
}

export function IndicatorCard({ indicator }: { indicator: IndicatorOverview }) {
  const rangePosition = indicator.range_position_3m ?? 50;

  return (
    <Card
      title={indicator.name}
      eyebrow={indicator.category}
      action={<Badge tone={toneFromDirection(indicator.trend_1m_direction)}>{indicator.interpretation}</Badge>}
    >
      <div className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="font-mono text-3xl font-semibold text-shell-text">{formatIndicatorValue(indicator)}</p>
            <p className="mt-1 text-sm text-shell-muted">{formatIndicatorChange(indicator)} recent change</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-[0.18em] text-shell-muted">3M range</p>
            <p className="font-mono text-lg text-shell-text">{rangePosition.toFixed(0)}%</p>
          </div>
        </div>

        <MiniSparkline values={indicator.sparkline} />

        <div className="grid gap-2 sm:grid-cols-3">
          <StatPill label="1M Trend" value={indicator.trend_1m_direction} />
          <StatPill label="3M Trend" value={indicator.trend_3m_direction} />
          <StatPill label="Source" value={indicator.source} />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-[0.18em] text-shell-muted">
            <span>3M Range Context</span>
            <span>{rangePosition.toFixed(0)}%</span>
          </div>
          <div className="relative h-2 rounded-full bg-white/5">
            <div className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-shell-accent/20 via-shell-accent to-shell-accentSoft/70" style={{ width: `${rangePosition}%` }} />
            <div className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border border-shell-bg bg-shell-text" style={{ left: `calc(${rangePosition}% - 6px)` }} />
          </div>
        </div>
      </div>
    </Card>
  );
}
