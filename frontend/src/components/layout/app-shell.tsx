"use client";

import { PropsWithChildren, useState } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: PropsWithChildren) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-shell-bg text-shell-text">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(90,200,250,0.12),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(125,224,212,0.08),_transparent_20%)]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.05]" data-shell-grid="true" />
      <div className="relative mx-auto flex min-h-screen max-w-[1740px] gap-4 px-3 py-3 sm:px-4 lg:px-6 lg:py-6">
        <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
        <div className="flex min-h-[calc(100vh-24px)] flex-1 flex-col rounded-[32px] border border-shell-border bg-shell-frame/88 shadow-shell backdrop-blur-xl lg:min-h-[calc(100vh-48px)]">
          <Topbar onOpenNav={() => setMobileOpen(true)} />
          <main className="flex-1 px-4 pb-6 pt-4 sm:px-6 lg:px-8 lg:pb-8 lg:pt-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
