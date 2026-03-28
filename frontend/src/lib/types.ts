export interface IndicatorOverview {
  code: string;
  name: string;
  category: string;
  unit: string;
  latest_value: number;
  change: number;
  change_pct?: number | null;
  trend_1m: number;
  trend_1m_direction: string;
  trend_3m: number;
  trend_3m_direction: string;
  interpretation: string;
  last_updated: string;
  sparkline: number[];
  source: string;
  range_position_3m?: number | null;
  history_context?: Record<string, number | string> | null;
}

export interface OverviewSummary {
  risk_tone: string;
  inflation_tone: string;
  growth_tone: string;
  rates_tone: string;
}

export interface OverviewResponse {
  as_of: string;
  summary: OverviewSummary;
  indicators: IndicatorOverview[];
}

export interface StaleIndicator {
  code: string;
  name: string;
  last_updated: string;
  age_days: number;
  source: string;
  max_staleness_days: number;
}

export interface ProviderStatus {
  provider: string;
  status: string;
  expected_count: number;
  indicator_count: number;
  live_count: number;
  stale_count: number;
}

export interface RefreshStatusResponse {
  mode: string;
  status: string;
  last_success_at?: string | null;
  latest_indicator_at?: string | null;
  source_summary: string;
  next_scheduled_refresh: string;
  stale_indicators: StaleIndicator[];
  provider_statuses: ProviderStatus[];
  last_digest_at?: string | null;
  recent_alert_count: number;
}

export interface RegimeDriver {
  label: string;
  detail: string;
  weight: number;
}

export interface RegimeCurrentResponse {
  as_of: string;
  regime: string;
  previous_regime?: string | null;
  confidence: number;
  summary: string;
  drivers: RegimeDriver[];
  supporting_indicators: Record<string, number>;
  regime_scores: Record<string, number>;
  pillar_scores: Record<string, number>;
}

export interface RegimeHistoryEntry {
  as_of: string;
  regime: string;
  confidence: number;
  summary: string;
}

export interface RegimeHistoryResponse {
  items: RegimeHistoryEntry[];
}

export interface AnomalyItem {
  id?: number | null;
  detected_at: string;
  rule_code: string;
  title: string;
  explanation: string;
  category: string;
  severity: number;
  related_assets: string[];
  supporting_metrics: Record<string, string | number>;
}

export interface AnomalyResponse {
  as_of?: string | null;
  items: AnomalyItem[];
}

export interface ThemeSignal {
  name: string;
  rationale: string;
}

export interface ExposureIdea {
  name: string;
  symbol?: string | null;
  stance: string;
  rationale: string;
}

export interface SectorIdea {
  name: string;
  stance: string;
  rationale: string;
}

export interface ThesisResult {
  interpreted_theme: string;
  confidence: number;
  theme_family?: string | null;
  time_horizon?: string | null;
  expression_style?: string | null;
  matched_keywords: string[];
  secondary_themes?: string[];
  transmission_channels: ThemeSignal[];
  sectors: SectorIdea[];
  etf_exposures: ExposureIdea[];
  representative_stocks: ExposureIdea[];
  catalysts?: ThemeSignal[];
  confirming_signals: ThemeSignal[];
  invalidation_signals: ThemeSignal[];
  notes: string[];
}

export interface SavedThesisResponse {
  id: number;
  input_text: string;
  interpreted_theme: string;
  result: ThesisResult;
  created_at: string;
}

export interface AlertConfig {
  regime_change_enabled: boolean;
  anomaly_severity_threshold: number;
  digest_cadence: "manual" | "market_open" | "market_close" | "both";
  updated_at?: string | null;
}

export interface AlertEvent {
  id: number;
  event_type: string;
  title: string;
  message: string;
  severity?: number | null;
  cadence?: string | null;
  payload: Record<string, string | number | string[]>;
  created_at: string;
}

export interface AlertHistoryResponse {
  items: AlertEvent[];
}

export interface NavigationItem {
  href: string;
  label: string;
  shortLabel: string;
  description: string;
}
