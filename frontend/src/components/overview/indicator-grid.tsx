import { IndicatorOverview } from "@/lib/types";

import { Card } from "@/components/ui/card";

import { IndicatorCard } from "./indicator-card";

export function IndicatorGrid({ indicators }: { indicators: IndicatorOverview[] }) {
  if (!indicators.length) {
    return (
      <Card title="No indicators match the current filters" eyebrow="Overview">
        <p className="text-sm leading-7 text-shell-muted">
          Try a different category or broaden the search terms to bring the market tape back into view.
        </p>
      </Card>
    );
  }

  const grouped = indicators.reduce<Record<string, IndicatorOverview[]>>((accumulator, indicator) => {
    accumulator[indicator.category] = [...(accumulator[indicator.category] ?? []), indicator];
    return accumulator;
  }, {});

  return (
    <div className="space-y-8">
      {Object.entries(grouped).map(([category, items]) => (
        <section key={category} className="space-y-4" id={`overview-${category.toLowerCase().replaceAll(" ", "-")}`}>
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold tracking-[-0.02em] text-shell-text">{category}</h2>
              <p className="mt-1 text-sm text-shell-muted">Signals grouped for quick scan and interpretation.</p>
            </div>
            <span className="rounded-full border border-shell-border bg-white/[0.03] px-3 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-shell-muted">
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
