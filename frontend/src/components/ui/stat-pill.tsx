export function StatPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-shell-border bg-black/15 px-3 py-2">
      <p className="text-[10px] uppercase tracking-[0.2em] text-shell-muted">{label}</p>
      <p className="mt-1 font-mono text-sm text-shell-text">{value}</p>
    </div>
  );
}
