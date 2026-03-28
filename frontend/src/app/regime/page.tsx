"use client";

import { useEffect, useState } from "react";

import { DriverList } from "@/components/regime/driver-list";
import { RegimeHero } from "@/components/regime/regime-hero";
import { RegimeHistoryChart } from "@/components/regime/regime-history-chart";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { UnavailablePanel } from "@/components/ui/unavailable-panel";
import { describeApiError, getCurrentRegime, getRegimeHistory } from "@/lib/api";
import { formatTimestamp, metricLabel } from "@/lib/format";
import { RegimeCurrentResponse, RegimeHistoryResponse } from "@/lib/types";

export default function RegimePage() {
  const [current, setCurrent] = useState<RegimeCurrentResponse | null>(null);
  const [history, setHistory] = useState<RegimeHistoryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setError(null);

    try {
      const [currentResponse, historyResponse] = await Promise.all([getCurrentRegime(), getRegimeHistory()]);
      setCurrent(currentResponse);
      setHistory(historyResponse);
    } catch (loadError) {
      setError(describeApiError(loadError));
      setCurrent(null);
      setHistory(null);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  if ((!current || !history) && !error) {
    return (
      <LoadingPanel
        title="Loading regime engine"
        eyebrow="Macro Classification"
        description="Scoring inflation, labor, credit, curve shape, and risk appetite."
      />
    );
  }

  if (!current || !history) {
    return (
      <UnavailablePanel
        title="Regime engine unavailable"
        eyebrow="Macro Classification"
        description="The regime engine requires the full live macro and market input set. Those live inputs are not available yet."
        error={error}
        action={
          <button
            type="button"
            onClick={() => void loadData()}
            className="inline-flex items-center justify-center rounded-full border border-shell-border bg-white/[0.04] px-4 py-2 text-sm font-medium text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10"
          >
            Retry live load
          </button>
        }
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
