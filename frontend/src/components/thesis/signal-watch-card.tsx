import { Card } from "@/components/ui/card";
import { ThemeSignal } from "@/lib/types";

export function SignalWatchCard({
  title,
  eyebrow,
  items,
  emptyLabel,
}: {
  title: string;
  eyebrow: string;
  items: ThemeSignal[];
  emptyLabel: string;
}) {
  return (
    <Card title={title} eyebrow={eyebrow}>
      <div className="space-y-3">
        {items.length ? (
          items.map((item) => (
            <div key={`${title}-${item.name}`} className="rounded-[22px] border border-shell-border bg-white/[0.03] p-4">
              <h3 className="text-sm font-semibold text-shell-text">{item.name}</h3>
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
