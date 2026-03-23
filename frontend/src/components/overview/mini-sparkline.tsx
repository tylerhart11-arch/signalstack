export function MiniSparkline({ values }: { values: number[] }) {
  if (!values.length) {
    return <div className="h-20 rounded-[22px] border border-dashed border-shell-border bg-white/[0.03]" />;
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

  const last = values[values.length - 1];
  const lastX = 100;
  const lastY = 100 - ((last - min) / spread) * 100;
  const areaPoints = `0,100 ${points} 100,100`;

  return (
    <div className="h-20 overflow-hidden rounded-[22px] border border-shell-border bg-white/[0.03] p-3">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="h-full w-full">
        <polygon fill="rgba(90, 200, 250, 0.08)" points={areaPoints} />
        <polyline fill="none" stroke="rgba(90, 200, 250, 0.95)" strokeWidth="3" points={points} />
        <circle cx={lastX} cy={lastY} r="4" fill="rgba(125, 224, 212, 0.95)" />
      </svg>
    </div>
  );
}
