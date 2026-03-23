"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { getAnomalies, getCurrentRegime, getOverview, getSavedTheses } from "@/lib/api";
import { formatTimestamp, severityLabel } from "@/lib/format";
import { thesisSamples } from "@/lib/constants";
import { AnomalyResponse, OverviewResponse, RegimeCurrentResponse, SavedThesisResponse } from "@/lib/types";

type HomeData = {
  anomalies: AnomalyResponse;
  overview: OverviewResponse;
  regime: RegimeCurrentResponse;
  saved: SavedThesisResponse[];
};

const actionLinkClass =
  "inline-flex items-center justify-center rounded-full border border-shell-border bg-white/[0.04] px-4 py-2 text-sm font-medium text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10";

export default function HomePage() {
  const [data, setData] = useState<HomeData | null>(null);

  useEffect(() => {
    async function bootstrap() {
      const [overview, regime, anomalies, saved] = await Promise.all([
        getOverview(),
        getCurrentRegime(),
        getAnomalies(),
        getSavedTheses(),
      ]);

      setData({ overview, regime, anomalies, saved });
    }

    void bootstrap();
  }, []);

  if (!data) {
    return (
      <LoadingPanel
        title="Loading command center"
        eyebrow="SignalStack Home"
        description="Pulling the cross-module market pulse, anomaly tape, and recent thesis context."
      />
    );
  }

  const overviewSources = Array.from(new Set(data.overview.indicators.map((indicator) => indicator.source)));
  const topAnomaly = data.anomalies.items[0];
  const recentThesis = data.saved[0];
  const summaryItems = [
    { label: "Risk tone", value: data.overview.summary.risk_tone },
    { label: "Inflation", value: data.overview.summary.inflation_tone },
    { label: "Growth", value: data.overview.summary.growth_tone },
    { label: "Rates", value: data.overview.summary.rates_tone },
  ];

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Market Command Center"
        description="A cleaner daily landing page for the current market state. Start here for the pulse, then step into the module that deserves deeper work."
        action={
          <>
            <Badge tone="accent">Updated {formatTimestamp(data.overview.as_of)}</Badge>
            {overviewSources.slice(0, 2).map((source) => (
              <Badge key={source} tone={source.includes("live") ? "positive" : "warning"}>
                {source}
              </Badge>
            ))}
          </>
        }
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card title="Today&apos;s Market Pulse" eyebrow="Daily starting point">
          <div className="space-y-6">
            <p className="max-w-3xl text-sm leading-7 text-shell-muted">
              The macro backdrop still looks mixed rather than fully risk-on. Use this command center to identify where the signal is strongest before diving into a full module.
            </p>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {summaryItems.map((item) => (
                <div key={item.label} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4 shadow-inset">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">{item.label}</p>
                  <p className="mt-2 text-lg font-semibold tracking-[-0.02em] text-shell-text">{item.value}</p>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              <Link href="/overview" className={actionLinkClass}>
                Open overview
              </Link>
              <Link href="/regime" className={actionLinkClass}>
                Review regime
              </Link>
              <Link href="/feed" className={actionLinkClass}>
                Scan anomalies
              </Link>
            </div>
          </div>
        </Card>

        <Card title={data.regime.regime} eyebrow="Current regime">
          <div className="space-y-5">
            <div className="flex flex-wrap gap-2">
              <Badge tone="accent">Confidence {Math.round(data.regime.confidence * 100)}%</Badge>
              {data.regime.previous_regime ? <Badge tone="neutral">Prior {data.regime.previous_regime}</Badge> : null}
            </div>
            <p className="text-sm leading-7 text-shell-muted">{data.regime.summary}</p>
            <div className="space-y-3">
              {data.regime.drivers.slice(0, 3).map((driver) => (
                <div key={driver.label} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-sm font-semibold text-shell-text">{driver.label}</h3>
                    <Badge tone="neutral">Weight {driver.weight.toFixed(1)}</Badge>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-shell-muted">{driver.detail}</p>
                </div>
              ))}
            </div>
            <Link href="/regime" className={actionLinkClass}>
              Open regime module
            </Link>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card title={topAnomaly?.title ?? "No active anomalies"} eyebrow="Anomaly spotlight">
          {topAnomaly ? (
            <div className="space-y-5">
              <div className="flex flex-wrap gap-2">
                <Badge tone="negative">
                  {severityLabel(topAnomaly.severity)} {topAnomaly.severity}
                </Badge>
                {topAnomaly.related_assets.slice(0, 3).map((asset) => (
                  <Badge key={asset} tone="neutral">
                    {asset}
                  </Badge>
                ))}
              </div>
              <p className="text-sm leading-7 text-shell-muted">{topAnomaly.explanation}</p>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">
                  Detected {formatTimestamp(topAnomaly.detected_at)}
                </span>
                <Link href="/feed" className={actionLinkClass}>
                  Open anomalies
                </Link>
              </div>
            </div>
          ) : (
            <p className="text-sm leading-7 text-shell-muted">
              The scanner did not find any threshold breaches in the current window.
            </p>
          )}
        </Card>

        <Card title="Thesis Desk" eyebrow="Next idea to work">
          <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="space-y-4">
              <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Most recent saved thesis</p>
                <h3 className="mt-2 text-lg font-semibold text-shell-text">
                  {recentThesis?.interpreted_theme ?? "No saved thesis yet"}
                </h3>
                <p className="mt-2 text-sm leading-6 text-shell-muted">
                  {recentThesis?.input_text ??
                    "Start with one of the sample prompts or write your own macro view in plain English."}
                </p>
                {recentThesis ? (
                  <p className="mt-3 text-[11px] uppercase tracking-[0.2em] text-shell-muted">
                    Saved {formatTimestamp(recentThesis.created_at)}
                  </p>
                ) : null}
              </div>
              <Link href="/thesis" className={actionLinkClass}>
                Open thesis builder
              </Link>
            </div>

            <div className="space-y-2">
              {thesisSamples.map((sample) => (
                <div key={sample} className="rounded-[20px] border border-shell-border bg-white/[0.03] px-4 py-3 text-sm text-shell-muted">
                  {sample}
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
