"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/lib/constants";

export function Topbar() {
  const pathname = usePathname();
  const active = navigation.find((item) => pathname.startsWith(item.href) || (pathname === "/" && item.href === "/overview"));

  return (
    <>
      <div className="hidden border-b border-shell-border/70 bg-black/25 px-8 py-3 font-mono text-[11px] uppercase tracking-[0.2em] text-shell-muted lg:flex lg:items-center lg:justify-between">
        <div className="flex items-center gap-6">
          <span className="text-shell-accent">Module {active?.shortLabel ?? "Overview"}</span>
          <span>Regime Engine Online</span>
          <span>Anomaly Scanner Ready</span>
          <span>Demo Fallback Enabled</span>
        </div>
        <span>Local-First Analyst Workflow</span>
      </div>

      <div className="sticky top-0 z-20 border-b border-shell-border/70 bg-shell-bg/92 px-4 py-4 backdrop-blur lg:hidden">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.24em] text-shell-accent">SignalStack</p>
            <p className="text-base font-semibold text-shell-text">{active?.label ?? "Overview"}</p>
          </div>
          <span className="rounded-full border border-shell-success/30 bg-shell-success/10 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-shell-success">
            Ready
          </span>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "whitespace-nowrap rounded-full border px-3 py-2 text-xs",
                pathname.startsWith(item.href) || (pathname === "/" && item.href === "/overview")
                  ? "border-shell-accent/35 bg-shell-accent/10 text-shell-text"
                  : "border-shell-border text-shell-muted",
              ].join(" ")}
            >
              {item.shortLabel}
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
