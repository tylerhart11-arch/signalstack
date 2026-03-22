import { Card } from "@/components/ui/card";
import { RegimeHistoryEntry } from "@/lib/types";

const regimeColor: Record<string, string> = {
  "Disinflationary Growth": "#3BC8FF",
  "Inflationary Expansion": "#F59E0B",
  Slowdown: "#F97373",
  "Recession Risk": "#EF4444",
  "Liquidity Expansion": "#2DD4BF",
  "Stress / Crisis": "#FB7185",
};

export function RegimeHistoryChart({ items }: { items: RegimeHistoryEntry[] }) {
  const maxConfidence = Math.max(...items.map((item) => item.confidence), 1);

  return (
    <Card title="Regime History" eyebrow="Historical Context">
      <div className="space-y-5">
        <div className="flex h-40 items-end gap-3">
          {items.map((item) => (
            <div key={`${item.as_of}-${item.regime}`} className="flex flex-1 flex-col items-center gap-2">
              <div className="w-full rounded-t-2xl" style={{ height: `${(item.confidence / maxConfidence) * 100}%`, backgroundColor: regimeColor[item.regime] ?? "#8BA5BD" }} />
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-shell-muted">
                {new Date(item.as_of).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          {items.map((item) => (
            <div key={`${item.as_of}-${item.regime}-detail`} className="rounded-2xl border border-shell-border bg-black/10 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: regimeColor[item.regime] ?? "#8BA5BD" }} />
                <p className="text-sm font-semibold text-shell-text">{item.regime}</p>
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-shell-muted">
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-shell-muted">{item.summary}</p>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
