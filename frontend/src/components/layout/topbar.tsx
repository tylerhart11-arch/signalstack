"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { getRefreshStatus } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { navigation } from "@/lib/constants";
import { RefreshStatusResponse } from "@/lib/types";

export function Topbar({ onOpenNav }: { onOpenNav: () => void }) {
  const pathname = usePathname();
  const [status, setStatus] = useState<RefreshStatusResponse | null>(null);
  const active =
    navigation.find((item) => {
      if (item.href === "/") {
        return pathname === "/";
      }
      return pathname === item.href || pathname.startsWith(`${item.href}/`);
    }) ?? navigation[0];

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      const response = await getRefreshStatus();
      if (!cancelled) {
        setStatus(response);
      }
    }

    void loadStatus();
    const interval = window.setInterval(() => {
      void loadStatus();
    }, 60_000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  const systemTone =
    status?.status === "fresh"
      ? "positive"
      : status?.status === "degraded" || status?.status === "mixed"
        ? "warning"
        : status?.status === "stale"
          ? "negative"
          : "neutral";
  const systemLabel = status ? status.status.replaceAll("_", " ") : "loading";

  return (
    <div className="sticky top-0 z-20 flex items-center justify-between gap-4 rounded-t-[32px] border-b border-shell-border bg-shell-frame/96 px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenNav}
          className="rounded-full border border-shell-border bg-shell-panelSoft/90 px-3 py-2 text-xs font-medium uppercase tracking-[0.18em] text-shell-muted lg:hidden"
        >
          Menu
        </button>
        <div>
          <p className="text-[11px] uppercase tracking-[0.24em] text-shell-accent">Active Module</p>
          <div className="mt-1 flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold tracking-[-0.02em] text-shell-text">{active.label}</h2>
            <p className="hidden text-sm text-shell-muted sm:block">{active.description}</p>
          </div>
        </div>
      </div>
      <div className="hidden items-center gap-3 lg:flex">
        <Badge tone={systemTone}>{systemLabel}</Badge>
        <Badge tone="neutral">{status?.mode ?? "local-first"}</Badge>
        <Badge tone={status?.stale_indicators.length ? "negative" : "neutral"}>
          {status?.stale_indicators.length ? `${status.stale_indicators.length} stale` : "No stale series"}
        </Badge>
        <Badge tone="accent">
          {status?.last_success_at ? `Updated ${formatTimestamp(status.last_success_at)}` : "Refresh pending"}
        </Badge>
        <Link
          href="/system"
          className="inline-flex items-center rounded-full border border-shell-border bg-shell-panelSoft/85 px-3 py-1.5 text-[11px] font-medium uppercase tracking-[0.16em] text-shell-text transition hover:border-shell-accent/30 hover:bg-shell-accent/10 hover:text-shell-accent"
        >
          System desk
        </Link>
      </div>
    </div>
  );
}
