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
        <div className="grid gap-3 sm:grid-cols-5">
          {items.map((item) => (
            <div key={`${item.as_of}-${item.regime}`} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-3">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: regimeColor[item.regime] ?? "#8BA5BD" }} />
                <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-shell-muted">
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
              <p className="mt-3 text-sm font-semibold text-shell-text">{item.regime}</p>
              <div className="mt-3 h-2 rounded-full bg-white/[0.05]">
                <div
                  className="h-2 rounded-full"
                  style={{
                    width: `${(item.confidence / maxConfidence) * 100}%`,
                    backgroundColor: regimeColor[item.regime] ?? "#8BA5BD",
                  }}
                />
              </div>
              <span className="mt-3 block font-mono text-[10px] uppercase tracking-[0.16em] text-shell-muted">
                {new Date(item.as_of).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </div>
          ))}
        </div>

        <div className="space-y-3">
          {items.map((item) => (
            <div key={`${item.as_of}-${item.regime}-detail`} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
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
