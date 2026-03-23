import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { StatPill } from "@/components/ui/stat-pill";
import { RegimeCurrentResponse } from "@/lib/types";

import { ConfidenceMeter } from "./confidence-meter";

export function RegimeHero({ current }: { current: RegimeCurrentResponse }) {
  const sortedScores = Object.entries(current.regime_scores).sort((left, right) => right[1] - left[1]);

  return (
    <Card title="Decision Panel" eyebrow="Current Macro Regime" className="overflow-hidden">
      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-5">
          <div className="flex flex-wrap gap-2">
            <Badge tone="accent">Current state</Badge>
            {current.previous_regime ? <Badge tone="neutral">Prior {current.previous_regime}</Badge> : null}
            <Badge tone="warning">Explainable scoring</Badge>
          </div>

          <div>
            <h3 className="text-[2.2rem] font-semibold tracking-[-0.04em] text-shell-text">{current.regime}</h3>
            <p className="mt-3 max-w-4xl text-sm leading-7 text-shell-muted">{current.summary}</p>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <StatPill label="Top State" value={sortedScores[0]?.[0] ?? "n/a"} />
            <StatPill label="Runner-Up" value={sortedScores[1]?.[0] ?? "n/a"} />
            <StatPill label="As Of" value={new Date(current.as_of).toLocaleDateString("en-US", { month: "short", day: "numeric" })} />
          </div>

          <ConfidenceMeter value={current.confidence} />
        </div>

        <div className="rounded-[24px] border border-shell-border bg-white/[0.03] p-5">
          <p className="text-[11px] uppercase tracking-[0.22em] text-shell-muted">Regime scoreboard</p>
          <div className="mt-4 space-y-4">
            {sortedScores.slice(0, 5).map(([label, value]) => {
              const width = Math.max(12, Math.min(100, value * 11));
              return (
                <div key={label}>
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <span className="text-sm text-shell-text">{label}</span>
                    <span className="font-mono text-sm text-shell-muted">{value.toFixed(1)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-white/[0.05]">
                    <div className="h-2 rounded-full bg-gradient-to-r from-shell-accent to-shell-accentSoft" style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Card>
  );
}
