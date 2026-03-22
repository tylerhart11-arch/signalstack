import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { StatPill } from "@/components/ui/stat-pill";
import { RegimeCurrentResponse } from "@/lib/types";

import { ConfidenceMeter } from "./confidence-meter";

export function RegimeHero({ current }: { current: RegimeCurrentResponse }) {
  const sortedScores = Object.entries(current.regime_scores).sort((left, right) => right[1] - left[1]);

  return (
    <Card title={current.regime} eyebrow="Current Macro Regime">
      <div className="space-y-5">
        <p className="max-w-4xl text-sm leading-7 text-shell-muted">{current.summary}</p>

        <div className="flex flex-wrap gap-2">
          {current.previous_regime ? <Badge tone="neutral">Prior {current.previous_regime}</Badge> : null}
          <Badge tone="accent">Rules-based</Badge>
          <Badge tone="warning">Explainable scoring</Badge>
        </div>

        <div className="grid gap-3 md:grid-cols-3">
          <StatPill label="Top State" value={sortedScores[0]?.[0] ?? "n/a"} />
          <StatPill label="Runner-Up" value={sortedScores[1]?.[0] ?? "n/a"} />
          <StatPill label="As Of" value={new Date(current.as_of).toLocaleDateString("en-US", { month: "short", day: "numeric" })} />
        </div>

        <ConfidenceMeter value={current.confidence} />
      </div>
    </Card>
  );
}
