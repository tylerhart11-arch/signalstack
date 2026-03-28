import { ReactNode } from "react";

import { Card } from "@/components/ui/card";

export function UnavailablePanel({
  title,
  eyebrow,
  description,
  error,
  action,
}: {
  title: string;
  eyebrow: string;
  description: string;
  error?: string | null;
  action?: ReactNode;
}) {
  return (
    <Card title={title} eyebrow={eyebrow} action={action}>
      <div className="space-y-4">
        <p className="text-sm leading-7 text-shell-muted">{description}</p>
        <div className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.2em] text-shell-muted">Live-only mode</p>
          <p className="mt-2 text-sm leading-6 text-shell-text">
            SignalStack will not render mock, demo, or browser-local fallback content. The panel stays empty until the
            live API is reachable again.
          </p>
        </div>
        {error ? (
          <div className="rounded-[22px] border border-shell-danger/25 bg-shell-danger/8 p-4">
            <p className="text-[11px] uppercase tracking-[0.2em] text-shell-danger">Latest error</p>
            <p className="mt-2 font-mono text-sm leading-6 text-shell-text">{error}</p>
          </div>
        ) : null}
      </div>
    </Card>
  );
}
