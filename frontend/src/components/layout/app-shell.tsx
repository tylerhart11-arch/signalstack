"use client";

import { PropsWithChildren } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-shell-bg text-shell-text">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,200,255,0.14),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(45,212,191,0.1),_transparent_25%)]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.08] [background-image:linear-gradient(rgba(148,163,184,0.16)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.16)_1px,transparent_1px)] [background-size:40px_40px]" />
      <div className="relative mx-auto flex min-h-screen max-w-[1650px] lg:flex-row">
        <Sidebar />
        <div className="flex min-h-screen flex-1 flex-col">
          <Topbar />
          <main className="flex-1 px-4 py-5 sm:px-6 lg:px-8 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
