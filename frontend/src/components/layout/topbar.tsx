"use client";

import { usePathname } from "next/navigation";

import { navigation } from "@/lib/constants";

export function Topbar({ onOpenNav }: { onOpenNav: () => void }) {
  const pathname = usePathname();
  const active =
    navigation.find((item) => {
      if (item.href === "/") {
        return pathname === "/";
      }
      return pathname === item.href || pathname.startsWith(`${item.href}/`);
    }) ?? navigation[0];

  return (
    <div className="sticky top-0 z-20 flex items-center justify-between gap-4 rounded-t-[32px] border-b border-shell-border bg-shell-frame/92 px-4 py-4 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenNav}
          className="rounded-full border border-shell-border bg-white/[0.03] px-3 py-2 text-xs font-medium uppercase tracking-[0.18em] text-shell-muted lg:hidden"
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
        <span className="rounded-full border border-shell-success/30 bg-shell-success/10 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-shell-success">
          Ready
        </span>
        <span className="rounded-full border border-shell-border px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-shell-muted">
          Local-first
        </span>
        <span className="rounded-full border border-shell-accent/25 bg-shell-accent/10 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-shell-accent">
          Premium dashboard refresh
        </span>
      </div>
    </div>
  );
}
