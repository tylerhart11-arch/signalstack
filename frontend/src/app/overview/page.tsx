"use client";

import { useEffect, useState } from "react";

import { IndicatorGrid } from "@/components/overview/indicator-grid";
import { MarketSummary } from "@/components/overview/market-summary";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { getOverview } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { OverviewResponse } from "@/lib/types";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewResponse | null>(null);

  useEffect(() => {
    void getOverview().then(setData);
  }, []);

  if (!data) {
    return (
      <Card title="Loading overview" eyebrow="Market Dashboard">
        <p className="text-sm text-shell-muted">Pulling the latest cross-asset snapshot and fallback context.</p>
      </Card>
    );
  }

  const sources = Array.from(new Set(data.indicators.map((indicator) => indicator.source)));

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Market Overview"
        description="Fast-scanning dashboard for the macro and market indicators that drive a top-down process. Each panel shows the latest level, trend direction, and a practical interpretation label."
        action={
          <>
            <Badge tone="accent">Updated {formatTimestamp(data.as_of)}</Badge>
            {sources.map((source) => (
              <Badge
                key={source}
                tone={source.includes("live") ? "positive" : source.includes("fallback") || source.includes("mock") ? "warning" : "neutral"}
              >
                {source}
              </Badge>
            ))}
          </>
        }
      />

      <MarketSummary data={data} />
      <IndicatorGrid indicators={data.indicators} />
    </div>
  );
}
