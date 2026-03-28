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
    <div className="animate-fade-up flex flex-col gap-4 border-b border-shell-border/70 pb-6 xl:flex-row xl:items-end xl:justify-between">
      <div className="max-w-3xl">
        <p className="text-[11px] uppercase tracking-[0.28em] text-shell-accent">SignalStack</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.03em] text-shell-text sm:text-[2.15rem]">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-shell-muted sm:text-[15px]">{description}</p>
      </div>
      {action ? <div className="flex flex-wrap items-center gap-2 xl:justify-end">{action}</div> : null}
    </div>
  );
}
