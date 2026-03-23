"use client";

import { useState } from "react";

import { SeverityBadge } from "@/components/feed/severity-badge";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatMetricValue, formatTimestamp, metricLabel } from "@/lib/format";
import { AnomalyItem } from "@/lib/types";

import { buildAnomalySnippet, getPrimaryMetrics, getSecondaryMetrics } from "./anomaly-utils";

export function AnomalyFeedItem({ item, rank }: { item: AnomalyItem; rank: number }) {
  const [expanded, setExpanded] = useState(false);
  const primaryMetrics = getPrimaryMetrics(item);
  const secondaryMetrics = getSecondaryMetrics(item);

  return (
    <Card
      title={item.title}
      eyebrow={item.category}
      action={
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">Priority {rank}</Badge>
          <SeverityBadge severity={item.severity} />
        </div>
      }
      className="overflow-hidden"
    >
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          {item.related_assets.map((asset) => (
            <Badge key={asset} tone="neutral">
              {asset}
            </Badge>
          ))}
        </div>

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.95fr)]">
          <div className="space-y-4">
            <p className="text-sm leading-7 text-shell-muted">{buildAnomalySnippet(item.explanation)}</p>

            <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <div className="mb-2 flex items-center justify-between text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                <span>Severity Ladder</span>
                <span>{item.severity}/100</span>
              </div>
              <div className="h-2 rounded-full bg-white/[0.05]">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-shell-accent via-shell-warn to-shell-danger"
                  style={{ width: `${Math.max(8, item.severity)}%` }}
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                Detected {formatTimestamp(item.detected_at)}
              </p>
              {secondaryMetrics.length ? (
                <button
                  type="button"
                  onClick={() => setExpanded((current) => !current)}
                  className="rounded-full border border-shell-border bg-white/[0.03] px-4 py-2 text-xs uppercase tracking-[0.18em] text-shell-muted transition hover:border-shell-accent/30 hover:text-shell-text"
                >
                  {expanded ? "Hide detail metrics" : `Show ${secondaryMetrics.length} more metrics`}
                </button>
              ) : null}
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {primaryMetrics.map(([label, value]) => (
              <div key={label} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">{metricLabel(label)}</p>
                <p className="mt-3 font-mono text-[1.7rem] font-medium tracking-[-0.04em] text-shell-text">
                  {formatMetricValue(value)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {expanded && secondaryMetrics.length ? (
          <div className="rounded-[24px] border border-shell-border bg-white/[0.025] p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">Expanded Detail</p>
                <p className="mt-1 text-sm text-shell-muted">Additional metrics and rule metadata for this anomaly.</p>
              </div>
              <Badge tone="neutral">{item.rule_code}</Badge>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {secondaryMetrics.map(([label, value]) => (
                <div key={label} className="rounded-[20px] border border-shell-border bg-white/[0.03] p-4">
                  <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">{metricLabel(label)}</p>
                  <p className="mt-2 font-mono text-lg text-shell-text">{formatMetricValue(value)}</p>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
