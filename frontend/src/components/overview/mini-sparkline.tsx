export function MiniSparkline({ values }: { values: number[] }) {
  if (!values.length) {
    return <div className="h-14 rounded-2xl border border-dashed border-shell-border bg-black/10" />;
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min || 1;
  const points = values
    .map((value, index) => {
      const x = (index / Math.max(1, values.length - 1)) * 100;
      const y = 100 - ((value - min) / spread) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="h-14 overflow-hidden rounded-2xl border border-shell-border bg-black/10 p-2">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="h-full w-full">
        <polyline fill="none" stroke="rgba(59,200,255,0.95)" strokeWidth="3" points={points} />
      </svg>
    </div>
  );
}
