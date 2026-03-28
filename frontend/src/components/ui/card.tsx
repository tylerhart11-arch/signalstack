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
      data-shell-panel="true"
      className={[
        "rounded-[28px] border border-shell-border bg-shell-panel/94 p-5 shadow-panel shadow-black/30 backdrop-blur-xl sm:p-6",
        className ?? "",
      ].join(" ")}
    >
      {title || eyebrow || action ? (
        <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
          <div>
            {eyebrow ? <p className="text-[11px] uppercase tracking-[0.24em] text-shell-muted">{eyebrow}</p> : null}
            {title ? <h2 className="mt-1 text-xl font-semibold tracking-tight text-shell-text">{title}</h2> : null}
          </div>
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}
