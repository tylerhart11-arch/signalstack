import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { StatPill } from "@/components/ui/stat-pill";
import { formatIndicatorChange, formatIndicatorValue, formatTimestamp } from "@/lib/format";
import { IndicatorOverview } from "@/lib/types";

import { MiniSparkline } from "./mini-sparkline";

// These indicators have inverse semantics: rising = bad (stress/risk-off)
const RISING_IS_NEGATIVE = new Set(["vix", "hy_spread", "ig_spread", "cpi_yoy", "core_cpi_yoy", "unemployment_rate"]);

function toneFromDirection(direction: string, code: string): "positive" | "warning" | "negative" {
  const inverse = RISING_IS_NEGATIVE.has(code);
  if (direction === "rising") {
    return inverse ? "negative" : "positive";
  }
  if (direction === "falling") {
    return inverse ? "positive" : "negative";
  }
  return "warning";
}

export function IndicatorCard({ indicator }: { indicator: IndicatorOverview }) {
  const rangePosition = indicator.range_position_3m ?? 50;
  const historyContext = indicator.history_context ?? {};

  return (
    <Card
      title={indicator.name}
      eyebrow={indicator.category}
      action={<Badge tone={toneFromDirection(indicator.trend_1m_direction, indicator.code)}>{indicator.interpretation}</Badge>}
    >
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="font-mono text-[2rem] font-semibold tracking-[-0.03em] text-shell-text">{formatIndicatorValue(indicator)}</p>
            <p className="mt-1 text-sm text-shell-muted">{formatIndicatorChange(indicator)} recent change</p>
          </div>
          <div className="rounded-[18px] border border-shell-border bg-white/[0.03] px-3 py-2 text-right">
            <p className="text-[10px] uppercase tracking-[0.18em] text-shell-muted">3M range</p>
            <p className="font-mono text-lg text-shell-text">{rangePosition.toFixed(0)}%</p>
          </div>
        </div>

        <MiniSparkline values={indicator.sparkline} />

        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          <StatPill label="1M Trend" value={indicator.trend_1m_direction} />
          <StatPill label="3M Trend" value={indicator.trend_3m_direction} />
          <StatPill label="Source" value={indicator.source} />
          <StatPill label="Updated" value={formatTimestamp(indicator.last_updated)} />
        </div>

        <div className="grid gap-2 sm:grid-cols-3">
          <StatPill label="3M Low" value={String(historyContext.three_month_low ?? "n/a")} />
          <StatPill label="3M High" value={String(historyContext.three_month_high ?? "n/a")} />
          <StatPill label="Move z-score" value={String(historyContext.move_zscore ?? "n/a")} />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between text-[10px] uppercase tracking-[0.18em] text-shell-muted">
            <span>Range context</span>
            <span>{rangePosition.toFixed(0)}%</span>
          </div>
          <div className="relative h-2 rounded-full bg-white/[0.05]">
            <div
              className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-shell-accent/30 via-shell-accent to-shell-accentSoft/70"
              style={{ width: `${rangePosition}%` }}
            />
            <div
              className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border border-shell-frame bg-shell-text"
              style={{ left: `calc(${rangePosition}% - 6px)` }}
            />
          </div>
        </div>

        <div className="rounded-[20px] border border-shell-border bg-white/[0.03] px-4 py-3">
          <p className="text-[10px] uppercase tracking-[0.18em] text-shell-muted">Desk read</p>
          <p className="mt-2 text-sm leading-6 text-shell-muted">{indicator.interpretation}</p>
        </div>
      </div>
    </Card>
  );
}
