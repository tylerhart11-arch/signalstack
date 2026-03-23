export function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-shell-border bg-white/[0.03] px-4 py-3 shadow-inset">
      <p className="text-[10px] uppercase tracking-[0.2em] text-shell-muted">{label}</p>
      <p className="mt-1 font-mono text-sm font-medium text-shell-text">{value}</p>
    </div>
  );
}
