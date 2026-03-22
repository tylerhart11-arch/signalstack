import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { metricLabel } from "@/lib/format";
import { RegimeCurrentResponse } from "@/lib/types";

export function DriverList({ current }: { current: RegimeCurrentResponse }) {
  const pillars = Object.entries(current.pillar_scores).sort((left, right) => Math.abs(right[1]) - Math.abs(left[1]));

  return (
    <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
      <Card title="Top Drivers" eyebrow="Why This Regime Is Winning">
        <div className="space-y-4">
          {current.drivers.map((driver) => (
            <div key={driver.label} className="rounded-2xl border border-shell-border bg-black/10 p-4">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-sm font-semibold text-shell-text">{driver.label}</h3>
                <Badge tone="neutral">Weight {driver.weight.toFixed(1)}</Badge>
              </div>
              <p className="mt-2 text-sm leading-6 text-shell-muted">{driver.detail}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Pillar Scoreboard" eyebrow="Underlying Inputs">
        <div className="space-y-4">
          {pillars.map(([label, score]) => {
            const width = Math.min(100, Math.abs(score) * 30);
            const left = score >= 0 ? 50 : Math.max(0, 50 - width);
            return (
              <div key={label}>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <span className="text-sm capitalize text-shell-text">{metricLabel(label)}</span>
                  <span className="font-mono text-sm text-shell-muted">{score.toFixed(2)}</span>
                </div>
                <div className="relative h-2 rounded-full bg-white/5">
                  <div className="absolute inset-y-0 left-1/2 w-px bg-shell-border" />
                  <div
                    className={[
                      "absolute inset-y-0 rounded-full",
                      score >= 0 ? "bg-gradient-to-r from-shell-accent to-shell-accentSoft" : "bg-gradient-to-r from-shell-danger to-shell-warn",
                    ].join(" ")}
                    style={{ left: `${left}%`, width: `${width}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
