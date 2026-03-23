import { metricLabel, severityLabel } from "@/lib/format";
import { AnomalyItem } from "@/lib/types";

type SearchField = "title" | "assets" | "category" | "rule" | "metrics" | "explanation";

const FIELD_WEIGHTS: Record<SearchField, number> = {
  title: 14,
  assets: 12,
  category: 10,
  rule: 9,
  metrics: 8,
  explanation: 5,
};

const METRIC_PRIORITY = [
  "rank_score",
  "divergence_score",
  "novelty_score",
  "breadth_score",
  "severity_score",
];

function normalizeSpaced(value: string): string {
  return value
    .toLowerCase()
    .replace(/[_/.-]+/g, " ")
    .replace(/[^a-z0-9%\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeCompact(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function tokenizeQuery(query: string): string[] {
  return normalizeSpaced(query)
    .split(" ")
    .map((token) => token.trim())
    .filter(Boolean);
}

function fieldVariants(value: string): { compact: string; spaced: string } {
  return {
    compact: normalizeCompact(value),
    spaced: normalizeSpaced(value),
  };
}

function scoreMetricKey(key: string): number {
  const priorityIndex = METRIC_PRIORITY.indexOf(key);
  if (priorityIndex >= 0) {
    return priorityIndex;
  }
  if (key.includes("pct") || key.includes("change")) {
    return METRIC_PRIORITY.length;
  }
  if (key.includes("spread") || key.includes("vol") || key.includes("move")) {
    return METRIC_PRIORITY.length + 1;
  }
  return METRIC_PRIORITY.length + 2;
}

function buildFieldMap(item: AnomalyItem): Record<SearchField, { compact: string; spaced: string }> {
  const metricNames = Object.keys(item.supporting_metrics)
    .map((key) => metricLabel(key))
    .join(" ");

  return {
    title: fieldVariants(item.title),
    assets: fieldVariants(item.related_assets.join(" ")),
    category: fieldVariants(item.category),
    rule: fieldVariants(item.rule_code),
    metrics: fieldVariants(metricNames),
    explanation: fieldVariants(item.explanation),
  };
}

function tokenMatchesField(token: string, fieldValue: { compact: string; spaced: string }): boolean {
  const compactToken = normalizeCompact(token);
  return Boolean(fieldValue.spaced.includes(token) || (compactToken && fieldValue.compact.includes(compactToken)));
}

export function scoreAnomalySearch(item: AnomalyItem, query: string): number {
  const tokens = tokenizeQuery(query);
  if (!tokens.length) {
    return 0;
  }

  const fields = buildFieldMap(item);
  const normalizedQuery = normalizeSpaced(query);
  let totalScore = 0;

  for (const token of tokens) {
    let bestFieldScore = 0;

    (Object.entries(fields) as Array<[SearchField, { compact: string; spaced: string }]>).forEach(([field, value]) => {
      if (tokenMatchesField(token, value)) {
        bestFieldScore = Math.max(bestFieldScore, FIELD_WEIGHTS[field]);
      }
    });

    if (!bestFieldScore) {
      return -1;
    }

    totalScore += bestFieldScore;
  }

  if (normalizedQuery && fields.title.spaced.includes(normalizedQuery)) {
    totalScore += 10;
  } else if (normalizedQuery && fields.assets.spaced.includes(normalizedQuery)) {
    totalScore += 8;
  } else if (normalizedQuery && fields.rule.spaced.includes(normalizedQuery)) {
    totalScore += 6;
  }

  totalScore += item.severity / 100;
  return totalScore;
}

export function getPrimaryMetrics(item: AnomalyItem): Array<[string, string | number]> {
  return Object.entries(item.supporting_metrics)
    .sort(([leftKey], [rightKey]) => scoreMetricKey(leftKey) - scoreMetricKey(rightKey))
    .slice(0, 4);
}

export function getSecondaryMetrics(item: AnomalyItem): Array<[string, string | number]> {
  const primaryKeys = new Set(getPrimaryMetrics(item).map(([key]) => key));
  return Object.entries(item.supporting_metrics).filter(([key]) => !primaryKeys.has(key));
}

export function buildAnomalySnippet(explanation: string, maxLength = 180): string {
  if (explanation.length <= maxLength) {
    return explanation;
  }

  return `${explanation.slice(0, maxLength).trimEnd()}...`;
}

export function getQuickAssetChips(items: AnomalyItem[], limit = 5): string[] {
  const counts = new Map<string, number>();

  items.forEach((item) => {
    item.related_assets.forEach((asset) => {
      counts.set(asset, (counts.get(asset) ?? 0) + 1);
    });
  });

  return [...counts.entries()]
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, limit)
    .map(([asset]) => asset);
}

export function buildActiveFilterSummary({
  asset,
  category,
  query,
  severityFloor,
}: {
  asset: string;
  category: string;
  query: string;
  severityFloor: number;
}): string {
  const parts: string[] = [];

  if (query.trim()) {
    parts.push(`Search: "${query.trim()}"`);
  }
  if (severityFloor > 0) {
    parts.push(`Severity: ${severityLabel(severityFloor)}`);
  }
  if (category !== "All") {
    parts.push(`Category: ${category}`);
  }
  if (asset !== "All") {
    parts.push(`Asset: ${asset}`);
  }

  return parts.length ? parts.join(" • ") : "No active filters";
}
