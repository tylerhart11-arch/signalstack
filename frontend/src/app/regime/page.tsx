"use client";

import { useEffect, useState } from "react";

import { DriverList } from "@/components/regime/driver-list";
import { RegimeHero } from "@/components/regime/regime-hero";
import { RegimeHistoryChart } from "@/components/regime/regime-history-chart";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { getCurrentRegime, getRegimeHistory } from "@/lib/api";
import { formatTimestamp, metricLabel } from "@/lib/format";
import { RegimeCurrentResponse, RegimeHistoryResponse } from "@/lib/types";

export default function RegimePage() {
  const [current, setCurrent] = useState<RegimeCurrentResponse | null>(null);
  const [history, setHistory] = useState<RegimeHistoryResponse | null>(null);

  useEffect(() => {
    void Promise.all([getCurrentRegime(), getRegimeHistory()]).then(([currentResponse, historyResponse]) => {
      setCurrent(currentResponse);
      setHistory(historyResponse);
    });
  }, []);

  if (!current || !history) {
    return (
      <LoadingPanel
        title="Loading regime engine"
        eyebrow="Macro Classification"
        description="Scoring inflation, labor, credit, curve shape, and risk appetite."
      />
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Macro Regime"
        description="Rules-based macro classification across inflation, labor, curve shape, credit, liquidity, and risk appetite. The display is built to show not just the label, but why the label is winning."
        action={
          <>
            <Badge tone="accent">As of {formatTimestamp(current.as_of)}</Badge>
            <Badge tone="neutral">{history.items.length} observations</Badge>
          </>
        }
      />

      <RegimeHero current={current} />
      <DriverList current={current} />

      <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
        <Card title="Supporting Indicators" eyebrow="Cross-Asset Context">
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(current.supporting_indicators).map(([label, value]) => (
              <div key={label} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">{metricLabel(label)}</p>
                <p className="mt-2 font-mono text-2xl text-shell-text">{value}</p>
              </div>
            ))}
          </div>
        </Card>

        <RegimeHistoryChart items={history.items} />
      </div>
    </div>
  );
}
