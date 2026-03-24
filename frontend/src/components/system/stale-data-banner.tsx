import { Badge } from "@/components/ui/badge";
import { RefreshStatusResponse } from "@/lib/types";

export function StaleDataBanner({ status }: { status: RefreshStatusResponse }) {
  if (!status.stale_indicators.length) {
    return null;
  }

  const staleNames = status.stale_indicators.slice(0, 3).map((item) => item.name);

  return (
    <div className="rounded-[24px] border border-shell-danger/35 bg-shell-danger/10 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="negative">Stale data warning</Badge>
        <Badge tone="neutral">{status.stale_indicators.length} indicators flagged</Badge>
      </div>
      <p className="mt-3 text-sm leading-6 text-shell-muted">
        Some series are older than their expected update window. Review {staleNames.join(", ")}
        {status.stale_indicators.length > staleNames.length ? ", and additional flagged series." : "."}
      </p>
    </div>
  );
}
