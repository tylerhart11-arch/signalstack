import { IndicatorOverview } from "@/lib/types";

export function formatTimestamp(value?: string | null): string {
  if (!value) {
    return "Unavailable";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatIndicatorValue(indicator: IndicatorOverview): string {
  const value = indicator.latest_value;

  if (indicator.unit === "%") {
    return `${value.toFixed(2)}%`;
  }
  if (indicator.unit === "bps") {
    return `${value.toFixed(0)} bps`;
  }
  if (indicator.unit === "usd") {
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  }
  return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export function formatIndicatorChange(indicator: IndicatorOverview): string {
  const sign = indicator.change >= 0 ? "+" : "";

  if (indicator.unit === "%") {
    return `${sign}${(indicator.change * 100).toFixed(0)} bps`;
  }
  if (indicator.unit === "bps") {
    return `${sign}${indicator.change.toFixed(0)} bps`;
  }
  if (indicator.change_pct !== null && indicator.change_pct !== undefined) {
    return `${indicator.change_pct >= 0 ? "+" : ""}${indicator.change_pct.toFixed(2)}%`;
  }
  return `${sign}${indicator.change.toFixed(2)}`;
}

export function formatMetricValue(value: number | string): string {
  if (typeof value === "string") {
    return value;
  }
  if (Math.abs(value) >= 1000) {
    return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }
  if (Math.abs(value) >= 100) {
    return value.toFixed(1);
  }
  return value.toFixed(2);
}

export function scoreTone(value: number): "positive" | "warning" | "negative" {
  if (value >= 0.72) {
    return "positive";
  }
  if (value >= 0.55) {
    return "warning";
  }
  return "negative";
}

export function severityLabel(severity: number): string {
  if (severity >= 80) {
    return "Critical";
  }
  if (severity >= 65) {
    return "High";
  }
  if (severity >= 45) {
    return "Elevated";
  }
  return "Watch";
}

export function metricLabel(label: string): string {
  return label.replaceAll("_", " ");
}
