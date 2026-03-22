import { ReactNode } from "react";

type Tone = "neutral" | "accent" | "positive" | "warning" | "negative";

const toneClasses: Record<Tone, string> = {
  neutral: "border-shell-border bg-white/5 text-shell-muted",
  accent: "border-shell-accent/30 bg-shell-accent/10 text-shell-accent",
  positive: "border-shell-success/30 bg-shell-success/10 text-shell-success",
  warning: "border-shell-warn/30 bg-shell-warn/10 text-shell-warn",
  negative: "border-shell-danger/30 bg-shell-danger/10 text-shell-danger",
};

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return (
    <span
      className={[
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-medium uppercase tracking-[0.16em]",
        toneClasses[tone],
      ].join(" ")}
    >
      {children}
    </span>
  );
}
