"use client";

import { useMemo, useState } from "react";

import { IndicatorGrid } from "@/components/overview/indicator-grid";
import { MarketSummary } from "@/components/overview/market-summary";
import { StaleDataBanner } from "@/components/system/stale-data-banner";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { UnavailablePanel } from "@/components/ui/unavailable-panel";
import { getOverview, getRefreshStatus } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { useLivePageData } from "@/lib/use-live-page-data";
import { OverviewResponse, RefreshStatusResponse } from "@/lib/types";

export default function OverviewPage() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");

  const loader = useMemo(
    () => async (): Promise<{ overview: OverviewResponse; status: RefreshStatusResponse }> => {
      const [overview, status] = await Promise.all([getOverview(), getRefreshStatus()]);
      return { overview, status };
    },
    [],
  );

  const { data: payload, error, loadData } = useLivePageData(loader);
  const data = payload?.overview ?? null;
  const refreshStatus = payload?.status ?? null;

  if ((!data || !refreshStatus) && !error) {
    return (
      <LoadingPanel
        title="Loading market overview"
        eyebrow="Market Dashboard"
        description="Pulling the latest cross-asset snapshot and live refresh status."
      />
    );
  }

  if (!data || !refreshStatus) {
    return (
      <UnavailablePanel
        title="Market overview unavailable"
        eyebrow="Market Dashboard"
        description="The overview page only renders live market data. The latest request did not complete successfully."
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

  const refreshTone =
    refreshStatus.status === "fresh"
      ? "positive"
      : refreshStatus.status === "stale"
        ? "negative"
        : refreshStatus.status === "degraded"
          ? "warning"
          : "neutral";

  const sources = Array.from(new Set(data.indicators.map((indicator) => indicator.source)));
  const categories = ["All", ...Array.from(new Set(data.indicators.map((indicator) => indicator.category)))];
  const normalizedSearch = search.trim().toLowerCase();
  const filteredIndicators = data.indicators.filter((indicator) => {
    const matchesCategory = activeCategory === "All" || indicator.category === activeCategory;
    const matchesSearch =
      !normalizedSearch ||
      indicator.name.toLowerCase().includes(normalizedSearch) ||
      indicator.code.toLowerCase().includes(normalizedSearch) ||
      indicator.interpretation.toLowerCase().includes(normalizedSearch);

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Market Overview"
        description="Fast-scanning dashboard for the macro and market indicators that drive a top-down process. Each panel shows the latest level, trend direction, and a practical interpretation label."
        action={
          <>
            <Badge tone="accent">Updated {formatTimestamp(data.as_of)}</Badge>
            <Badge tone={refreshTone}>{refreshStatus.status}</Badge>
            {sources.map((source) => (
              <Badge key={source} tone={source.includes("live") ? "positive" : "warning"}>
                {source}
              </Badge>
            ))}
            <Badge tone="neutral">{refreshStatus.source_summary}</Badge>
            <Badge tone="neutral">{filteredIndicators.length} visible</Badge>
          </>
        }
      />

      <StaleDataBanner status={refreshStatus} />

      <MarketSummary data={data} />

      <div className="sticky top-[86px] z-10 rounded-[24px] border border-shell-border bg-shell-frame/92 p-3 backdrop-blur-xl">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <label className="flex min-w-0 flex-1 items-center gap-3 rounded-[18px] border border-shell-border bg-white/[0.04] px-4 py-3">
            <span className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">Search</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Ticker, series, or interpretation"
              className="min-w-0 flex-1 bg-transparent text-sm text-shell-text outline-none placeholder:text-shell-muted"
            />
          </label>

          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category}
                type="button"
                onClick={() => setActiveCategory(category)}
                className={[
                  "rounded-full border px-4 py-2 text-xs uppercase tracking-[0.18em] transition",
                  activeCategory === category
                    ? "border-shell-accent/30 bg-shell-accent/10 text-shell-accent"
                    : "border-shell-border bg-white/[0.03] text-shell-muted hover:border-shell-borderStrong hover:text-shell-text",
                ].join(" ")}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </div>

      <IndicatorGrid indicators={filteredIndicators} />
    </div>
  );
}
