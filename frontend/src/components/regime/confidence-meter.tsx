export function ConfidenceMeter({ value }: { value: number }) {
  const width = Math.max(8, Math.min(100, value * 100));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.18em] text-shell-muted">
        <span>Confidence</span>
        <span>{Math.round(value * 100)}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/5">
        <div className="h-2 rounded-full bg-gradient-to-r from-shell-accent via-shell-accentSoft to-shell-success" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
