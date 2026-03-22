import { ReactNode } from "react";

export function Card({
  title,
  eyebrow,
  action,
  children,
  className,
}: {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={[
        "rounded-3xl border border-shell-border bg-shell-panel/85 p-5 shadow-panel backdrop-blur",
        className ?? "",
      ].join(" ")}
    >
      {title || eyebrow || action ? (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            {eyebrow ? <p className="text-[11px] uppercase tracking-[0.24em] text-shell-muted">{eyebrow}</p> : null}
            {title ? <h2 className="mt-1 text-lg font-semibold text-shell-text">{title}</h2> : null}
          </div>
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}
