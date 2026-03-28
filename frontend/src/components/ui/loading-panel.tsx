import { Card } from "@/components/ui/card";

export function LoadingPanel({
  title,
  eyebrow,
  description,
}: {
  title: string;
  eyebrow: string;
  description: string;
}) {
  return (
    <Card title={title} eyebrow={eyebrow}>
      <div className="space-y-4 animate-pulse">
        <p className="text-sm text-shell-muted">{description}</p>
        <div className="grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="h-20 rounded-[22px] border border-shell-border bg-shell-panelSoft/85" />
          ))}
        </div>
        <div className="h-56 rounded-[24px] border border-shell-border bg-shell-panelSoft/85" />
      </div>
    </Card>
  );
}
