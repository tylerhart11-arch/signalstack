import { Badge } from "@/components/ui/badge";
import { severityLabel } from "@/lib/format";

export function SeverityBadge({ severity }: { severity: number }) {
  const tone = severity >= 80 ? "negative" : severity >= 65 ? "warning" : "accent";
  return <Badge tone={tone}>{severityLabel(severity)} {severity}</Badge>;
}
