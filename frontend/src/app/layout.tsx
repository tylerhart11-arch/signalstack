import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";

import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "SignalStack",
  description: "Personal market intelligence terminal for macro regimes, cross-asset anomalies, and thesis translation.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
