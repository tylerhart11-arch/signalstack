"use client";

import { useDeferredValue, useEffect, useState } from "react";

import { AnomalyFeedList } from "@/components/feed/anomaly-feed-list";
import {
  buildActiveFilterSummary,
  getQuickAssetChips,
  scoreAnomalySearch,
} from "@/components/feed/anomaly-utils";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { getAnomalies } from "@/lib/api";
import { formatTimestamp, severityLabel } from "@/lib/format";
import { AnomalyResponse } from "@/lib/types";

export default function FeedPage() {
  const [data, setData] = useState<AnomalyResponse | null>(null);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("All");
  const [activeAsset, setActiveAsset] = useState("All");
  const [severityFloor, setSeverityFloor] = useState(0);
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    void getAnomalies().then(setData);
  }, []);

  if (!data) {
    return (
      <LoadingPanel
        title="Loading anomaly feed"
        eyebrow="Curiosity Scanner"
        description="Ranking cross-asset divergences and novelty signals."
      />
    );
  }

  const categories = ["All", ...Array.from(new Set(data.items.map((item) => item.category)))];
  const quickAssets = ["All", ...getQuickAssetChips(data.items)];
  const severityOptions = [
    { label: "All", value: 0 },
    { label: "Elevated+", value: 45 },
    { label: "High+", value: 65 },
    { label: "Critical", value: 80 },
  ];
  const searchedItems = data.items
    .map((item) => ({
      item,
      score: scoreAnomalySearch(item, deferredSearch),
    }))
    .filter(({ score }) => (deferredSearch.trim() ? score >= 0 : true));
  const filteredItems = searchedItems
    .filter(({ item }) => {
      const matchesCategory = activeCategory === "All" || item.category === activeCategory;
      const matchesAsset = activeAsset === "All" || item.related_assets.includes(activeAsset);
      const matchesSeverity = item.severity >= severityFloor;
      return matchesCategory && matchesAsset && matchesSeverity;
    })
    .sort((left, right) => {
      if (deferredSearch.trim()) {
        return right.score - left.score || right.item.severity - left.item.severity;
      }
      return right.item.severity - left.item.severity;
    })
    .map(({ item }) => item);
  const topVisible = [...filteredItems].sort((left, right) => right.severity - left.severity)[0];
  const hasActiveFilters = Boolean(
    deferredSearch.trim() || activeCategory !== "All" || activeAsset !== "All" || severityFloor > 0,
  );
  const activeFilterSummary = buildActiveFilterSummary({
    query: deferredSearch,
    category: activeCategory,
    asset: activeAsset,
    severityFloor,
  });

  function resetFilters() {
    setSearch("");
    setActiveCategory("All");
    setActiveAsset("All");
    setSeverityFloor(0);
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Anomalies"
        description="Daily anomaly tape for unusual cross-asset behavior. Signals are ranked by divergence, novelty, breadth, and practical market importance."
        action={
          <>
            <Badge tone="accent">Feed time {formatTimestamp(data.as_of)}</Badge>
            <Badge tone="neutral">{filteredItems.length} visible</Badge>
          </>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-[24px] border border-shell-border bg-white/[0.03] p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Visible anomalies</p>
            <p className="mt-3 font-mono text-[2rem] font-medium tracking-[-0.04em] text-shell-text">
              {filteredItems.length}
              <span className="ml-2 text-base text-shell-muted">/ {data.items.length}</span>
            </p>
          </div>

          <div className="rounded-[24px] border border-shell-border bg-white/[0.03] p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Highest severity</p>
            <p className="mt-3 text-lg font-semibold text-shell-text">
              {topVisible ? `${severityLabel(topVisible.severity)} ${topVisible.severity}` : "None visible"}
            </p>
            {topVisible ? <p className="mt-2 text-sm text-shell-muted">{topVisible.title}</p> : null}
          </div>

          <div className="rounded-[24px] border border-shell-border bg-white/[0.03] p-4 sm:col-span-3 xl:col-span-1">
            <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Active lens</p>
            <p className="mt-3 text-sm leading-6 text-shell-muted">{activeFilterSummary}</p>
          </div>
        </div>

        <div className="sticky top-[86px] z-10 rounded-[24px] border border-shell-border bg-shell-frame/92 p-3 backdrop-blur-xl">
          <div className="flex flex-col gap-3">
            <label className="flex min-w-0 items-center gap-3 rounded-[18px] border border-shell-border bg-white/[0.04] px-4 py-3">
              <span className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">Search</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Title, asset, rule, category, or metric"
                className="min-w-0 flex-1 bg-transparent text-sm text-shell-text outline-none placeholder:text-shell-muted"
              />
            </label>

            <div className="flex flex-wrap items-center gap-2">
              {severityOptions.map((option) => (
                <button
                  key={option.label}
                  type="button"
                  onClick={() => setSeverityFloor(option.value)}
                  className={[
                    "rounded-full border px-4 py-2 text-xs uppercase tracking-[0.18em] transition",
                    severityFloor === option.value
                      ? "border-shell-accent/30 bg-shell-accent/10 text-shell-accent"
                      : "border-shell-border bg-white/[0.03] text-shell-muted hover:border-shell-borderStrong hover:text-shell-text",
                  ].join(" ")}
                >
                  {option.label}
                </button>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-2">
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

            <div className="flex flex-wrap items-center gap-2">
              {quickAssets.map((asset) => (
                <button
                  key={asset}
                  type="button"
                  onClick={() => setActiveAsset(asset)}
                  className={[
                    "rounded-full border px-4 py-2 text-xs uppercase tracking-[0.18em] transition",
                    activeAsset === asset
                      ? "border-shell-accentSoft/30 bg-shell-accentSoft/10 text-shell-accentSoft"
                      : "border-shell-border bg-white/[0.03] text-shell-muted hover:border-shell-borderStrong hover:text-shell-text",
                  ].join(" ")}
                >
                  {asset}
                </button>
              ))}
            </div>

            <div className="flex items-center justify-between gap-3">
              <p className="text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                Smart search checks titles, assets, rule codes, categories, and metric labels.
              </p>
              <button
                type="button"
                onClick={resetFilters}
                disabled={!hasActiveFilters}
                className="rounded-full border border-shell-border bg-white/[0.03] px-4 py-2 text-xs uppercase tracking-[0.18em] text-shell-muted transition hover:border-shell-accent/30 hover:text-shell-text disabled:cursor-not-allowed disabled:opacity-50"
              >
                Reset filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <AnomalyFeedList items={filteredItems} totalCount={data.items.length} hasActiveFilters={hasActiveFilters} />
    </div>
  );
}
