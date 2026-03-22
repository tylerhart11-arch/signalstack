import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ExposureIdea, SectorIdea } from "@/lib/types";

type Item = ExposureIdea | SectorIdea;

export function ExposureCard({
  title,
  eyebrow,
  items,
  emptyLabel,
}: {
  title: string;
  eyebrow: string;
  items: Item[];
  emptyLabel: string;
}) {
  return (
    <Card title={title} eyebrow={eyebrow}>
      <div className="space-y-3">
        {items.length ? (
          items.map((item) => (
            <div key={`${title}-${item.name}-${"symbol" in item ? item.symbol ?? "" : ""}`} className="rounded-2xl border border-shell-border bg-black/10 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-sm font-semibold text-shell-text">{item.name}</h3>
                {"symbol" in item && item.symbol ? <Badge tone="accent">{item.symbol}</Badge> : null}
                <Badge tone="neutral">{item.stance}</Badge>
              </div>
              <p className="mt-2 text-sm leading-6 text-shell-muted">{item.rationale}</p>
            </div>
          ))
        ) : (
          <p className="text-sm text-shell-muted">{emptyLabel}</p>
        )}
      </div>
    </Card>
  );
}
