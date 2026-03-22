"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navigation } from "@/lib/constants";

function isActive(pathname: string, href: string): boolean {
  if (href === "/overview") {
    return pathname === "/" || pathname === "/overview";
  }
  return pathname.startsWith(href);
}

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-[290px] shrink-0 border-r border-shell-border/80 bg-shell-panel/70 px-6 py-7 backdrop-blur lg:flex lg:flex-col">
      <div className="mb-8 rounded-3xl border border-shell-border bg-black/20 p-5">
        <p className="text-[11px] uppercase tracking-[0.28em] text-shell-accent">SignalStack</p>
        <h1 className="mt-2 text-2xl font-semibold text-shell-text">Personal Market Intelligence</h1>
        <p className="mt-3 text-sm leading-6 text-shell-muted">
          Market dashboard, regime logic, anomaly ranking, and thesis translation in one local-first analyst workflow.
        </p>
      </div>

      <nav className="space-y-2">
        {navigation.map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={[
                "block rounded-2xl border px-4 py-3 transition",
                active
                  ? "border-shell-accent/35 bg-shell-accent/10 text-shell-text"
                  : "border-transparent bg-transparent text-shell-muted hover:border-shell-border hover:bg-white/5 hover:text-shell-text",
              ].join(" ")}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-semibold">{item.label}</span>
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                  {item.shortLabel}
                </span>
              </div>
              <p className="mt-1 text-xs leading-5 text-shell-muted">{item.description}</p>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-3xl border border-shell-border bg-black/20 p-4">
        <p className="text-[11px] uppercase tracking-[0.25em] text-shell-muted">Terminal Notes</p>
        <p className="mt-2 text-sm leading-6 text-shell-muted">
          Live providers are optional. If FRED or Yahoo are unavailable, SignalStack falls back to realistic seeded market states.
        </p>
      </div>
    </aside>
  );
}
