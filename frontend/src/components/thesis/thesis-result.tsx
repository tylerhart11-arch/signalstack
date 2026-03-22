import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { StatPill } from "@/components/ui/stat-pill";
import { ThesisResult as ThesisResultType } from "@/lib/types";

import { ExposureCard } from "./exposure-card";
import { SignalWatchCard } from "./signal-watch-card";

export function ThesisResult({ result }: { result: ThesisResultType }) {
  return (
    <div className="space-y-6">
      <Card title={result.interpreted_theme} eyebrow="Parsed Theme">
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            <StatPill label="Theme Family" value={result.theme_family ?? "Not classified"} />
            <StatPill label="Time Horizon" value={result.time_horizon ?? "Not classified"} />
            <StatPill label="Expression Style" value={result.expression_style ?? "Not classified"} />
          </div>

          <div className="flex flex-wrap gap-2">
            {result.matched_keywords.length ? (
              result.matched_keywords.map((keyword) => (
                <Badge key={keyword} tone="accent">
                  {keyword}
                </Badge>
              ))
            ) : (
              <Badge tone="neutral">No direct keyword hit</Badge>
            )}
            {result.secondary_themes?.map((theme) => (
              <Badge key={theme} tone="warning">
                {theme}
              </Badge>
            ))}
          </div>

          <p className="text-sm leading-7 text-shell-muted">
            SignalStack maps the thesis into causal channels first, then into sectors, ETF expressions, and representative names to watch.
          </p>
        </div>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <SignalWatchCard title="Transmission Channels" eyebrow="Causal Map" items={result.transmission_channels} emptyLabel="No channels were mapped." />
        <ExposureCard title="Affected Sectors" eyebrow="Sector Map" items={result.sectors} emptyLabel="No sector translation yet." />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <ExposureCard title="ETF Exposures" eyebrow="Liquid Vehicles" items={result.etf_exposures} emptyLabel="No ETF ideas available." />
        <ExposureCard title="Representative Stocks" eyebrow="Single-Name Examples" items={result.representative_stocks} emptyLabel="No representative stocks available." />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <SignalWatchCard title="Catalysts To Watch" eyebrow="Catalysts" items={result.catalysts ?? []} emptyLabel="No catalysts mapped yet." />
        <SignalWatchCard title="Confirming Signals" eyebrow="Validation" items={result.confirming_signals} emptyLabel="No confirming signals mapped yet." />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <SignalWatchCard title="Invalidation Risks" eyebrow="What Breaks It" items={result.invalidation_signals} emptyLabel="No invalidation signals mapped yet." />
        <Card title="Notes" eyebrow="MVP Logic">
          <div className="space-y-3">
            {result.notes.map((note) => (
              <div key={note} className="rounded-2xl border border-shell-border bg-black/10 px-4 py-3 text-sm leading-6 text-shell-muted">
                {note}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
