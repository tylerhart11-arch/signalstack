"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/lib/constants";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function Sidebar({
  mobileOpen,
  setMobileOpen,
}: {
  mobileOpen: boolean;
  setMobileOpen: (value: boolean) => void;
}) {
  const pathname = usePathname();

  return (
    <>
      <div
        className={[
          "fixed inset-0 z-30 bg-[#02060c]/72 backdrop-blur-sm transition duration-200 lg:hidden",
          mobileOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0",
        ].join(" ")}
        onClick={() => setMobileOpen(false)}
      />

      <aside
        className={[
          "fixed inset-y-3 left-3 z-40 flex w-[320px] flex-col rounded-[30px] border border-shell-border bg-shell-panel/95 p-5 shadow-shell transition duration-200 backdrop-blur-xl lg:sticky lg:top-6 lg:z-10 lg:h-[calc(100vh-48px)] lg:w-[280px] lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-[108%] lg:translate-x-0",
        ].join(" ")}
      >
        <div className="mb-6 flex items-start justify-between gap-4">
          <div className="space-y-3">
            <div className="inline-flex rounded-full border border-shell-accent/20 bg-shell-accent/10 px-3 py-1 text-[11px] uppercase tracking-[0.28em] text-shell-accent">
              SignalStack
            </div>
            <div>
              <h1 className="text-[1.8rem] font-semibold tracking-[-0.03em] text-shell-text">Market Command</h1>
              <p className="mt-2 text-sm leading-6 text-shell-muted">
                Premium cross-asset intelligence for macro context, anomaly detection, and thesis translation.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setMobileOpen(false)}
            className="rounded-full border border-shell-border bg-white/[0.03] px-3 py-2 text-xs uppercase tracking-[0.18em] text-shell-muted lg:hidden"
          >
            Close
          </button>
        </div>

        <nav className="space-y-2">
          {navigation.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={[
                  "block rounded-[24px] border px-4 py-3 transition",
                  active
                    ? "border-shell-borderStrong bg-white/[0.06] shadow-inset"
                    : "border-transparent bg-transparent text-shell-muted hover:border-shell-border hover:bg-white/[0.03] hover:text-shell-text",
                ].join(" ")}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm font-semibold text-shell-text">{item.label}</span>
                  <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                    {item.shortLabel}
                  </span>
                </div>
                <p className="mt-1 text-xs leading-5 text-shell-muted">{item.description}</p>
              </Link>
            );
          })}
        </nav>

        <div className="mt-6 rounded-[24px] border border-shell-border bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.25em] text-shell-muted">Market Status</p>
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between gap-3 text-sm text-shell-muted">
              <span>Mode</span>
              <span className="rounded-full border border-shell-border px-2 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-shell-text">
                Local-first
              </span>
            </div>
            <div className="flex items-center justify-between gap-3 text-sm text-shell-muted">
              <span>Data fallback</span>
              <span className="rounded-full border border-shell-warn/30 bg-shell-warn/10 px-2 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-shell-warn">
                Enabled
              </span>
            </div>
            <p className="text-sm leading-6 text-shell-muted">
              Live providers are optional. SignalStack continues to render a realistic analyst workflow when providers are unavailable.
            </p>
          </div>
        </div>

        <div className="mt-auto rounded-[24px] border border-shell-border bg-gradient-to-br from-shell-accent/8 via-transparent to-shell-accentSoft/10 p-4">
          <p className="text-[11px] uppercase tracking-[0.25em] text-shell-muted">Workflow</p>
          <p className="mt-2 text-sm leading-6 text-shell-muted">
            Start at Home for the daily pulse, then move into Overview, Regime, Anomalies, or Thesis when a signal deserves depth.
          </p>
        </div>
      </aside>
    </>
  );
}
