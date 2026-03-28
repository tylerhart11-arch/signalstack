"use client";

import { useEffect, useState } from "react";

import { StaleDataBanner } from "@/components/system/stale-data-banner";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/ui/loading-panel";
import { SectionHeader } from "@/components/ui/section-header";
import { getAlertConfig, getAlertHistory, getRefreshStatus, runDigest, updateAlertConfig } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { AlertConfig, AlertEvent, RefreshStatusResponse } from "@/lib/types";

type SystemPageState = {
  config: AlertConfig;
  history: AlertEvent[];
  status: RefreshStatusResponse;
};

export default function SystemPage() {
  const [data, setData] = useState<SystemPageState | null>(null);
  const [saving, setSaving] = useState(false);
  const [runningDigest, setRunningDigest] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  useEffect(() => {
    async function bootstrap() {
      const [status, config, history] = await Promise.all([
        getRefreshStatus(),
        getAlertConfig(),
        getAlertHistory(),
      ]);
      setData({ status, config, history: history.items });
    }

    void bootstrap();
  }, []);

  if (!data) {
    return (
      <LoadingPanel
        title="Loading system desk"
        eyebrow="Automation"
        description="Checking refresh health, alert thresholds, and the latest digest history."
      />
    );
  }

  const statusTone =
    data.status.status === "fresh"
      ? "positive"
      : data.status.status === "stale"
        ? "negative"
        : data.status.status === "demo"
          ? "neutral"
          : "warning";

  async function handleSave() {
    if (!data) {
      return;
    }

    setSaving(true);
    setNote(null);

    try {
      const updated = await updateAlertConfig(data.config);
      setData((current) => (current ? { ...current, config: updated } : current));
      setNote("Alert settings saved.");
    } finally {
      setSaving(false);
    }
  }

  async function handleRunDigest() {
    setRunningDigest(true);
    setNote(null);

    try {
      const digest = await runDigest();
      const status = await getRefreshStatus();
      setData((current) =>
        current
          ? {
              ...current,
              status,
              history: [digest, ...current.history].slice(0, 25),
            }
          : current,
      );
      setNote("Manual digest generated.");
    } finally {
      setRunningDigest(false);
    }
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="System Desk"
        description="Single-user automation controls for refresh health, alert thresholds, and generated open/close summaries. This keeps the platform local-first while still surfacing the information that matters."
        action={
          <>
            <Badge tone={statusTone}>{data.status.status}</Badge>
            <Badge tone="accent">Updated {formatTimestamp(data.status.last_success_at)}</Badge>
            <Badge tone="neutral">{data.status.source_summary}</Badge>
          </>
        }
      />

      <StaleDataBanner status={data.status} />

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card title="Refresh Health" eyebrow="Observability">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Last successful refresh</p>
              <p className="mt-2 text-lg font-semibold text-shell-text">{formatTimestamp(data.status.last_success_at)}</p>
            </div>
            <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Next scheduled refresh</p>
              <p className="mt-2 text-lg font-semibold text-shell-text">{formatTimestamp(data.status.next_scheduled_refresh)}</p>
            </div>
            <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Recent alerts</p>
              <p className="mt-2 text-lg font-semibold text-shell-text">{data.status.recent_alert_count}</p>
            </div>
            <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Last digest</p>
              <p className="mt-2 text-lg font-semibold text-shell-text">{formatTimestamp(data.status.last_digest_at)}</p>
            </div>
          </div>

          <div className="mt-5 space-y-3">
            {data.status.provider_statuses.map((provider) => (
              <div key={provider.provider} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">{provider.provider}</p>
                    <p className="mt-1 text-base font-semibold text-shell-text">{provider.status}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge tone="positive">{provider.live_count} live</Badge>
                    <Badge tone="warning">{provider.fallback_count + provider.mixed_count} degraded</Badge>
                    <Badge tone="neutral">{provider.demo_count} demo</Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-6">
          <Card title="Alert Settings" eyebrow="Single-user controls">
            <div className="space-y-5">
              <label className="flex items-center justify-between gap-4 rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <div>
                  <p className="text-sm font-semibold text-shell-text">Regime-change alerts</p>
                  <p className="mt-1 text-sm leading-6 text-shell-muted">
                    Create a history item when the active macro regime changes.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={data.config.regime_change_enabled}
                  onChange={(event) =>
                    setData((current) =>
                      current
                        ? {
                            ...current,
                            config: {
                              ...current.config,
                              regime_change_enabled: event.target.checked,
                            },
                          }
                        : current,
                    )
                  }
                  className="h-5 w-5 rounded border-shell-border bg-transparent accent-shell-accentSoft"
                />
              </label>

              <label className="block rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <p className="text-sm font-semibold text-shell-text">Anomaly severity threshold</p>
                <p className="mt-1 text-sm leading-6 text-shell-muted">
                  Only log anomaly alerts at or above this severity score.
                </p>
                <div className="mt-4 flex items-center gap-3">
                  <input
                    type="range"
                    min={0}
                    max={100}
                    value={data.config.anomaly_severity_threshold}
                    onChange={(event) =>
                      setData((current) =>
                        current
                          ? {
                              ...current,
                              config: {
                                ...current.config,
                                anomaly_severity_threshold: Number(event.target.value),
                              },
                            }
                          : current,
                      )
                    }
                    className="w-full accent-shell-accent"
                  />
                  <Badge tone="accent">{data.config.anomaly_severity_threshold}</Badge>
                </div>
              </label>

              <label className="block rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                <p className="text-sm font-semibold text-shell-text">Digest cadence</p>
                <p className="mt-1 text-sm leading-6 text-shell-muted">
                  Choose when SignalStack should generate the daily summary automatically.
                </p>
                <select
                  value={data.config.digest_cadence}
                  onChange={(event) =>
                    setData((current) =>
                      current
                        ? {
                            ...current,
                            config: {
                              ...current.config,
                              digest_cadence: event.target.value as AlertConfig["digest_cadence"],
                            },
                          }
                        : current,
                    )
                  }
                  className="mt-4 w-full rounded-[18px] border border-shell-border bg-shell-frame px-4 py-3 text-sm text-shell-text outline-none"
                >
                  <option value="manual">Manual only</option>
                  <option value="market_open">At market open</option>
                  <option value="market_close">At market close</option>
                  <option value="both">Open and close</option>
                </select>
              </label>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => void handleSave()}
                  disabled={saving}
                  className="rounded-full border border-shell-accent/30 bg-shell-accent/10 px-4 py-2 text-sm font-medium text-shell-accent transition hover:bg-shell-accent/15 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {saving ? "Saving..." : "Save settings"}
                </button>
                <button
                  type="button"
                  onClick={() => void handleRunDigest()}
                  disabled={runningDigest}
                  className="rounded-full border border-shell-border bg-white/[0.04] px-4 py-2 text-sm font-medium text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {runningDigest ? "Running digest..." : "Run manual digest"}
                </button>
              </div>

              {note ? <p className="text-sm text-shell-muted">{note}</p> : null}
            </div>
          </Card>

          <Card title="Alert & Digest History" eyebrow="Recent generated items">
            <div className="space-y-3">
              {data.history.length ? (
                data.history.map((event) => (
                  <div key={event.id} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge
                        tone={
                          event.event_type === "digest"
                            ? "accent"
                            : event.event_type === "regime_change"
                              ? "warning"
                              : "negative"
                        }
                      >
                        {event.event_type.replaceAll("_", " ")}
                      </Badge>
                      {event.severity ? <Badge tone="neutral">Severity {event.severity}</Badge> : null}
                      <Badge tone="neutral">{formatTimestamp(event.created_at)}</Badge>
                    </div>
                    <h3 className="mt-3 text-sm font-semibold text-shell-text">{event.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-shell-muted">{event.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-shell-muted">No alert or digest history has been generated yet.</p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
