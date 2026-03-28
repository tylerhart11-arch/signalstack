import { Badge } from "@/components/ui/badge";
import { RefreshStatusResponse } from "@/lib/types";

export function StaleDataBanner({ status }: { status: RefreshStatusResponse }) {
  if (!status.stale_indicators.length) {
    return null;
  }

  const staleNames = status.stale_indicators.slice(0, 3).map((item) => item.name);

  return (
    <div className="rounded-[24px] border border-shell-danger/35 bg-[linear-gradient(135deg,rgba(251,113,133,0.14),rgba(11,13,16,0.9))] p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone="negative">Stale data warning</Badge>
        <Badge tone="neutral">{status.stale_indicators.length} indicators flagged</Badge>
      </div>
      <p className="mt-3 text-sm leading-6 text-shell-text">
        Some series are older than their expected update window. Review {staleNames.join(", ")}
        {status.stale_indicators.length > staleNames.length ? ", and additional flagged series." : "."}
      </p>
    </div>
  );
}
