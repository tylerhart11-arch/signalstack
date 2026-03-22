import { IndicatorOverview } from "@/lib/types";

import { IndicatorCard } from "./indicator-card";

export function IndicatorGrid({ indicators }: { indicators: IndicatorOverview[] }) {
  const grouped = indicators.reduce<Record<string, IndicatorOverview[]>>((accumulator, indicator) => {
    accumulator[indicator.category] = [...(accumulator[indicator.category] ?? []), indicator];
    return accumulator;
  }, {});

  return (
    <div className="space-y-8">
      {Object.entries(grouped).map(([category, items]) => (
        <section key={category} className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-xl font-semibold text-shell-text">{category}</h2>
            <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-shell-muted">
              {items.length} tracked
            </span>
          </div>
          <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
            {items.map((indicator) => (
              <IndicatorCard key={indicator.code} indicator={indicator} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
