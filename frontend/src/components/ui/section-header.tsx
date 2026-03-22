import { ReactNode } from "react";

export function SectionHeader({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 border-b border-shell-border/70 pb-5 xl:flex-row xl:items-end xl:justify-between">
      <div className="max-w-3xl">
        <p className="text-[11px] uppercase tracking-[0.26em] text-shell-accent">SignalStack</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-shell-text">{title}</h1>
        <p className="mt-3 text-sm leading-7 text-shell-muted">{description}</p>
      </div>
      {action ? <div className="flex flex-wrap items-center gap-2">{action}</div> : null}
    </div>
  );
}
