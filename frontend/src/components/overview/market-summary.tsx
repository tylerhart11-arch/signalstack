import { Card } from "@/components/ui/card";
import { OverviewResponse } from "@/lib/types";

export function MarketSummary({ data }: { data: OverviewResponse }) {
  const items = [
    { label: "Risk Tone", value: data.summary.risk_tone, note: "Equities, breadth, and volatility backdrop." },
    { label: "Inflation", value: data.summary.inflation_tone, note: "Headline and core inflation pulse." },
    { label: "Growth", value: data.summary.growth_tone, note: "Labor, small caps, and cyclical proxies." },
    { label: "Rates", value: data.summary.rates_tone, note: "Front-end yields and curve context." },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <Card key={item.label} title={item.value} eyebrow={item.label} className="overflow-hidden">
          <p className="text-sm leading-6 text-shell-muted">{item.note}</p>
        </Card>
      ))}
    </div>
  );
}
