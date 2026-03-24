import {
  AlertConfig,
  AlertEvent,
  AlertHistoryResponse,
  AnomalyResponse,
  OverviewResponse,
  RefreshStatusResponse,
  RegimeCurrentResponse,
  RegimeHistoryResponse,
  SavedThesisResponse,
  ThesisResult,
} from "@/lib/types";

function spark(start: number, end: number, count = 18, wobble = 0.05): number[] {
  return Array.from({ length: count }, (_, index) => {
    const progress = index / Math.max(1, count - 1);
    const base = start + (end - start) * progress;
    const wave = Math.sin(index / 2.1) * (Math.abs(end - start) || start || 1) * wobble;
    return Number((base + wave).toFixed(2));
  });
}

function decorateOverview(data: OverviewResponse): OverviewResponse {
  return {
    ...data,
    indicators: data.indicators.map((indicator) => {
      const low = Math.min(...indicator.sparkline);
      const high = Math.max(...indicator.sparkline);
      const range = high - low || 1;
      const rangePosition = ((indicator.latest_value - low) / range) * 100;

      return {
        ...indicator,
        range_position_3m: Number(Math.max(0, Math.min(100, rangePosition)).toFixed(1)),
        history_context: {
          three_month_low: Number(low.toFixed(2)),
          three_month_high: Number(high.toFixed(2)),
          move_zscore: Number(((indicator.change_pct ?? indicator.change) / 2.2).toFixed(2)),
        },
      };
    }),
  };
}

function buildMockOverview(): OverviewResponse {
  return decorateOverview({
    as_of: new Date().toISOString(),
    summary: {
      risk_tone: "constructive but narrow",
      inflation_tone: "disinflation intact",
      growth_tone: "late-cycle softening",
      rates_tone: "easing with steepening",
    },
    indicators: [
      { code: "sp500", name: "S&P 500", category: "Equities", unit: "index", latest_value: 5325, change: 51, change_pct: 0.97, trend_1m: 3.9, trend_1m_direction: "rising", trend_3m: 6.7, trend_3m_direction: "rising", interpretation: "uptrend intact", last_updated: new Date().toISOString(), sparkline: spark(5120, 5325, 22, 0.03), source: "mock" },
      { code: "nasdaq100", name: "Nasdaq 100", category: "Equities", unit: "index", latest_value: 18890, change: 284, change_pct: 1.53, trend_1m: 6.2, trend_1m_direction: "rising", trend_3m: 9.8, trend_3m_direction: "rising", interpretation: "uptrend intact", last_updated: new Date().toISOString(), sparkline: spark(17650, 18890, 22, 0.025), source: "mock" },
      { code: "russell2000", name: "Russell 2000", category: "Equities", unit: "index", latest_value: 2142, change: -9, change_pct: -0.42, trend_1m: -2.1, trend_1m_direction: "falling", trend_3m: -1.4, trend_3m_direction: "falling", interpretation: "financing stress", last_updated: new Date().toISOString(), sparkline: spark(2190, 2142, 22, 0.04), source: "mock" },
      { code: "vix", name: "VIX", category: "Risk", unit: "index", latest_value: 18.6, change: 0.8, change_pct: 4.2, trend_1m: 9.1, trend_1m_direction: "rising", trend_3m: 3.3, trend_3m_direction: "rising", interpretation: "hedging demand", last_updated: new Date().toISOString(), sparkline: spark(16.1, 18.6, 22, 0.08), source: "mock" },
      { code: "us2y", name: "US 2Y Treasury", category: "Rates", unit: "%", latest_value: 4.46, change: -0.03, change_pct: -0.67, trend_1m: -18, trend_1m_direction: "falling", trend_3m: -39, trend_3m_direction: "falling", interpretation: "restrictive but easing", last_updated: new Date().toISOString(), sparkline: spark(4.78, 4.46, 22, 0.01), source: "mock" },
      { code: "us10y", name: "US 10Y Treasury", category: "Rates", unit: "%", latest_value: 4.17, change: -0.02, change_pct: -0.41, trend_1m: -15, trend_1m_direction: "falling", trend_3m: -27, trend_3m_direction: "falling", interpretation: "duration relief", last_updated: new Date().toISOString(), sparkline: spark(4.38, 4.17, 22, 0.01), source: "mock" },
      { code: "s2s10s", name: "2s10s Slope", category: "Rates", unit: "bps", latest_value: -29, change: 2, change_pct: 6.5, trend_1m: 12, trend_1m_direction: "rising", trend_3m: 16, trend_3m_direction: "rising", interpretation: "de-inverting", last_updated: new Date().toISOString(), sparkline: spark(-45, -29, 22, 0.05), source: "mock" },
      { code: "hy_spread", name: "High Yield Spread Proxy", category: "Credit", unit: "%", latest_value: 4.18, change: 0.05, change_pct: 1.21, trend_1m: 27, trend_1m_direction: "rising", trend_3m: 49, trend_3m_direction: "rising", interpretation: "spread stress building", last_updated: new Date().toISOString(), sparkline: spark(3.72, 4.18, 22, 0.03), source: "mock" },
      { code: "ig_spread", name: "Investment Grade Spread Proxy", category: "Credit", unit: "%", latest_value: 1.28, change: 0.01, change_pct: 0.83, trend_1m: 11, trend_1m_direction: "rising", trend_3m: 19, trend_3m_direction: "rising", interpretation: "credit caution", last_updated: new Date().toISOString(), sparkline: spark(1.12, 1.28, 22, 0.03), source: "mock" },
      { code: "dxy", name: "DXY Proxy", category: "FX", unit: "index", latest_value: 103.3, change: -0.4, change_pct: -0.38, trend_1m: -1.9, trend_1m_direction: "falling", trend_3m: -2.2, trend_3m_direction: "falling", interpretation: "conditions easing", last_updated: new Date().toISOString(), sparkline: spark(105.1, 103.3, 22, 0.01), source: "mock" },
      { code: "wti", name: "WTI Crude", category: "Commodities", unit: "usd", latest_value: 79.6, change: 1.2, change_pct: 1.53, trend_1m: 5.9, trend_1m_direction: "rising", trend_3m: 8.4, trend_3m_direction: "rising", interpretation: "reflation bid", last_updated: new Date().toISOString(), sparkline: spark(74.2, 79.6, 22, 0.03), source: "mock" },
      { code: "gold", name: "Gold", category: "Commodities", unit: "usd", latest_value: 2298, change: 18, change_pct: 0.79, trend_1m: 3.3, trend_1m_direction: "rising", trend_3m: 7.2, trend_3m_direction: "rising", interpretation: "macro hedge bid", last_updated: new Date().toISOString(), sparkline: spark(2195, 2298, 22, 0.02), source: "mock" },
      { code: "copper", name: "Copper", category: "Commodities", unit: "usd", latest_value: 4.46, change: 0.03, change_pct: 0.73, trend_1m: 4.8, trend_1m_direction: "rising", trend_3m: 9.1, trend_3m_direction: "rising", interpretation: "cyclical pulse", last_updated: new Date().toISOString(), sparkline: spark(4.1, 4.46, 22, 0.02), source: "mock" },
      { code: "cpi_yoy", name: "CPI YoY", category: "Inflation", unit: "%", latest_value: 2.93, change: -0.03, change_pct: -1.01, trend_1m: -0.1, trend_1m_direction: "falling", trend_3m: -0.31, trend_3m_direction: "falling", interpretation: "cooling toward target", last_updated: new Date().toISOString(), sparkline: spark(3.42, 2.93, 18, 0.01), source: "mock" },
      { code: "core_cpi_yoy", name: "Core CPI YoY", category: "Inflation", unit: "%", latest_value: 3.18, change: -0.02, change_pct: -0.62, trend_1m: -0.07, trend_1m_direction: "falling", trend_3m: -0.24, trend_3m_direction: "falling", interpretation: "disinflation intact", last_updated: new Date().toISOString(), sparkline: spark(3.76, 3.18, 18, 0.01), source: "mock" },
      { code: "unemployment_rate", name: "Unemployment Rate", category: "Labor", unit: "%", latest_value: 4.09, change: 0.03, change_pct: 0.74, trend_1m: 0.08, trend_1m_direction: "rising", trend_3m: 0.21, trend_3m_direction: "rising", interpretation: "labor softening", last_updated: new Date().toISOString(), sparkline: spark(3.82, 4.09, 18, 0.01), source: "mock" },
      { code: "fed_funds_rate", name: "Fed Funds Rate", category: "Policy", unit: "%", latest_value: 5.13, change: 0, change_pct: 0, trend_1m: -13, trend_1m_direction: "falling", trend_3m: -25, trend_3m_direction: "falling", interpretation: "restrictive but easing", last_updated: new Date().toISOString(), sparkline: spark(5.38, 5.13, 18, 0.005), source: "mock" },
    ],
  });
}

function buildMockRegimeCurrent(): RegimeCurrentResponse {
  return {
    as_of: new Date().toISOString(),
    regime: "Slowdown",
    previous_regime: "Disinflationary Growth",
    confidence: 0.74,
    summary:
      "Disinflation is helping, but breadth, small caps, and credit are not fully confirming the headline equity tape. The setup still looks late-cycle rather than cleanly expansionary.",
    drivers: [
      { label: "Credit is no longer clean", detail: "HY and IG spreads are drifting wider, which reduces confidence in a broad-based risk-on regime.", weight: 2.6 },
      { label: "Labor is softening", detail: "Unemployment has moved off the lows and now supports a slower-growth interpretation.", weight: 2.1 },
      { label: "Disinflation is still helping", detail: "Cooling headline and core inflation prevent the regime from tipping fully into crisis.", weight: 1.9 },
      { label: "Breadth remains narrow", detail: "Large-cap growth leadership is stronger than small-cap or financial participation.", weight: 1.7 },
    ],
    supporting_indicators: {
      cpi_yoy: 2.93,
      core_cpi_yoy: 3.18,
      unemployment_rate: 4.09,
      s2s10s_bps: -29,
      hy_spread: 4.18,
      ig_spread: 1.28,
      sp500_1m_pct: 3.9,
      russell2000_1m_pct: -2.1,
      vix: 18.6,
      wti_1m_pct: 5.9,
    },
    regime_scores: {
      "Disinflationary Growth": 6.1,
      "Inflationary Expansion": 2.8,
      Slowdown: 7.8,
      "Recession Risk": 5.9,
      "Liquidity Expansion": 4.6,
      "Stress / Crisis": 4.3,
    },
    pillar_scores: {
      disinflation: 1.8,
      growth: -0.9,
      labor: -0.8,
      curve: -0.3,
      credit: -1.1,
      risk: 0.4,
      commodity: 0.5,
      liquidity: 0.6,
      stress: 1.1,
    },
  };
}

function buildMockRegimeHistory(): RegimeHistoryResponse {
  const day = 1000 * 60 * 60 * 24;
  return {
    items: [
      { as_of: new Date(Date.now() - day * 28).toISOString(), regime: "Disinflationary Growth", confidence: 0.68, summary: "Cooling inflation and still-supportive equities kept the backdrop constructive." },
      { as_of: new Date(Date.now() - day * 21).toISOString(), regime: "Disinflationary Growth", confidence: 0.67, summary: "Large-cap strength still offset weaker breadth." },
      { as_of: new Date(Date.now() - day * 14).toISOString(), regime: "Slowdown", confidence: 0.7, summary: "Credit softening and labor drift started to matter more." },
      { as_of: new Date(Date.now() - day * 7).toISOString(), regime: "Slowdown", confidence: 0.73, summary: "Cross-asset confirmation weakened even as inflation continued to cool." },
      { as_of: new Date().toISOString(), regime: "Slowdown", confidence: 0.74, summary: "The current state remains late-cycle with mixed confirmation." },
    ],
  };
}

function buildMockAnomalies(): AnomalyResponse {
  return {
    as_of: new Date().toISOString(),
    items: [
      {
        id: 1,
        detected_at: new Date().toISOString(),
        rule_code: "equities_up_credit_worse",
        title: "Equity tape is outrunning credit confirmation",
        explanation:
          "Stocks are still grinding higher, but both high-yield and investment-grade spreads are widening. That usually signals narrow leadership rather than a healthy broad-risk backdrop.",
        category: "Cross-asset divergence",
        severity: 84,
        related_assets: ["S&P 500", "High Yield Spreads", "Investment Grade Spreads"],
        supporting_metrics: { sp500_5d_pct: 1.42, hy_spread_5d_change: 0.16, ig_spread_5d_change: 0.04, rank_score: 84, divergence_score: 2.3, novelty_score: 1.7, breadth_score: 1.2 },
      },
      {
        id: 2,
        detected_at: new Date(Date.now() - 1000 * 60 * 40).toISOString(),
        rule_code: "vol_inconsistent_with_index_move",
        title: "Volatility is rising underneath a positive index move",
        explanation:
          "The S&P 500 is up, but implied volatility is climbing too. That usually means institutions still want protection despite the positive headline move.",
        category: "Volatility divergence",
        severity: 79,
        related_assets: ["S&P 500", "VIX", "High Yield Spreads"],
        supporting_metrics: { sp500_5d_pct: 2.1, vix_5d_pct: 13.6, hy_spread_5d_change: 0.08, rank_score: 79, divergence_score: 2.0, novelty_score: 1.5, breadth_score: 1.1 },
      },
      {
        id: 3,
        detected_at: new Date(Date.now() - 1000 * 60 * 70).toISOString(),
        rule_code: "small_caps_lag_despite_risk_on",
        title: "Small caps are not confirming the risk-on narrative",
        explanation:
          "Large-cap growth is still carrying the tape, but small-cap underperformance suggests the move is narrow and financing-sensitive companies are not participating.",
        category: "Breadth warning",
        severity: 73,
        related_assets: ["IWM", "QQQ", "VIX"],
        supporting_metrics: { iwm_1m_pct: -2.4, qqq_1m_pct: 6.3, sp500_1m_pct: 3.9, rank_score: 73, divergence_score: 1.9, novelty_score: 1.2, breadth_score: 1.0 },
      },
    ],
  };
}

function buildCreditStressResult(): ThesisResult {
  return {
    interpreted_theme: "Credit stress leads equities",
    confidence: 0.8,
    theme_family: "Credit, Funding Conditions, and Late-Cycle Risk",
    time_horizon: "Tactical to medium-term (1-9 months)",
    expression_style: "Defensive / hedge overlay",
    matched_keywords: ["credit stress", "spreads"],
    secondary_themes: ["Funding stress", "Late-cycle defensives"],
    transmission_channels: [
      { name: "Spread widening", rationale: "Lower-quality credit usually reacts earlier than equities to tighter funding conditions." },
      { name: "Refinancing wall pressure", rationale: "As spreads widen, companies with weaker balance sheets lose room to roll debt cheaply." },
    ],
    sectors: [
      { name: "High-yield credit", stance: "Underweight", rationale: "Usually the first liquid market to register funding stress." },
      { name: "Regional banks and finance", stance: "Underweight", rationale: "Banks and funding-sensitive lenders can amplify the stress signal." },
    ],
    etf_exposures: [
      { name: "iShares iBoxx High Yield Corporate Bond ETF", symbol: "HYG", stance: "Underweight / Hedge", rationale: "Liquid proxy for spread stress." },
      { name: "Consumer Staples Select Sector SPDR", symbol: "XLP", stance: "Long", rationale: "Useful defensive ballast if stress spreads." },
    ],
    representative_stocks: [
      { name: "Ally Financial", symbol: "ALLY", stance: "Underweight", rationale: "Consumer credit sensitivity fits an early-stress view." },
      { name: "Walmart", symbol: "WMT", stance: "Overweight", rationale: "Defensive consumer exposure can hold up better if stress broadens." },
    ],
    catalysts: [{ name: "HY spread breakout", rationale: "Credit begins widening faster than equity volatility acknowledges." }],
    confirming_signals: [{ name: "HY spreads widen ahead of VIX", rationale: "Credit moves first while the equity market stays relatively calm." }],
    invalidation_signals: [{ name: "Spreads reverse tighter", rationale: "The warning signal fails if credit heals quickly." }],
    notes: ["Fallback result generated locally because the backend was unavailable."],
  };
}

function buildGenericResult(input: string): ThesisResult {
  return {
    interpreted_theme: "Generic macro translation",
    confidence: 0.44,
    theme_family: "Unclassified macro idea",
    time_horizon: "Medium-term (3-12 months)",
    expression_style: "Watchlist / benchmark-first",
    matched_keywords: [],
    secondary_themes: [],
    transmission_channels: [
      {
        name: "Narrative decomposition",
        rationale: `SignalStack could not map "${input}" to a named template, so it translated the idea into a benchmark-first watchlist.`,
      },
    ],
    sectors: [{ name: "Broad market", stance: "Watch", rationale: "Validate the macro path before narrowing into sub-industries." }],
    etf_exposures: [{ name: "SPDR S&P 500 ETF Trust", symbol: "SPY", stance: "Watch", rationale: "Useful benchmark while refining the thesis." }],
    representative_stocks: [{ name: "Market proxy", symbol: "SPY", stance: "Watch", rationale: "No narrower basket scored highly enough yet." }],
    catalysts: [{ name: "Clarify the catalyst", rationale: "Define what should change first and on what time horizon." }],
    confirming_signals: [{ name: "Relative performance", rationale: "The assets tied most directly to the thesis should begin to outperform their benchmark." }],
    invalidation_signals: [{ name: "Cross-asset contradiction", rationale: "If rates, credit, and commodities all disagree, the thesis likely needs revision." }],
    notes: ["Try adding a clearer catalyst, a time horizon, and an industry or factor that should move first."],
  };
}

function mockAnalyzeThesis(input: string): ThesisResult {
  const lower = input.toLowerCase();

  if (lower.includes("ai") || lower.includes("data center") || lower.includes("electricity")) {
    return {
      interpreted_theme: "AI infrastructure power squeeze",
      confidence: 0.83,
      theme_family: "Power, Infrastructure, and AI Capacity",
      time_horizon: "Structural (1-3 years)",
      expression_style: "Directional long / capex beneficiaries",
      matched_keywords: ["ai", "data center", "electricity"],
      secondary_themes: ["Electrification capex", "Power scarcity"],
      transmission_channels: [
        { name: "Electric load growth", rationale: "AI clusters raise baseload electricity demand and shorten spare-capacity windows." },
        { name: "Grid capex acceleration", rationale: "Utilities and transmission providers may need faster investment cycles to serve hyperscale demand." },
        { name: "Thermal bottlenecks", rationale: "Cooling and backup power become important choke points." },
      ],
      sectors: [
        { name: "Utilities", stance: "Overweight", rationale: "Load growth and rate-base expansion can support regulated earnings." },
        { name: "Electrical equipment", stance: "Overweight", rationale: "Switchgear, transformers, and power-management vendors sit directly in the capex path." },
      ],
      etf_exposures: [
        { name: "Utilities Select Sector SPDR", symbol: "XLU", stance: "Long", rationale: "Broad utility exposure tied to higher power demand." },
        { name: "VanEck Semiconductor ETF", symbol: "SMH", stance: "Long", rationale: "Captures the compute side of the AI build-out." },
      ],
      representative_stocks: [
        { name: "Constellation Energy", symbol: "CEG", stance: "Long", rationale: "Generation footprint with data-center demand leverage." },
        { name: "Vertiv", symbol: "VRT", stance: "Long", rationale: "Direct exposure to power, thermal management, and backup systems." },
      ],
      catalysts: [
        { name: "Utility load-plan revisions", rationale: "Utilities explicitly raise medium-term demand assumptions." },
        { name: "Hyperscaler capex guidance", rationale: "Cloud and AI infrastructure budgets stay elevated." },
      ],
      confirming_signals: [
        { name: "Power load forecasts move higher", rationale: "Utilities and grid operators revise expectations upward." },
        { name: "Transformer backlog stays firm", rationale: "Equipment lead times confirm real physical scarcity." },
      ],
      invalidation_signals: [
        { name: "Hyperscaler capex pause", rationale: "A spending pause breaks the core demand channel." },
        { name: "Power-market looseness", rationale: "Fast supply relief weakens the scarcity angle." },
      ],
      notes: ["Fallback result generated locally because the backend was unavailable."],
    };
  }

  if (lower.includes("higher") || lower.includes("rates") || lower.includes("small cap")) {
    return {
      interpreted_theme: "Higher-for-longer rates pressure small caps",
      confidence: 0.79,
      theme_family: "Rates, Balance Sheets, and Domestic Cyclicals",
      time_horizon: "Medium-term (3-12 months)",
      expression_style: "Relative value / quality over small caps",
      matched_keywords: ["rates", "small caps"],
      secondary_themes: ["Quality over cyclicals", "Regional-bank stress"],
      transmission_channels: [
        { name: "Higher financing costs", rationale: "Smaller companies have less balance-sheet flexibility and more refinancing sensitivity." },
        { name: "Multiple compression", rationale: "Higher discount rates weigh more heavily on lower-quality equities." },
      ],
      sectors: [
        { name: "Small-cap cyclicals", stance: "Underweight", rationale: "Funding and demand sensitivity both become headwinds." },
        { name: "Defensive quality", stance: "Overweight", rationale: "Cash-generative large caps hold up better in tight conditions." },
      ],
      etf_exposures: [
        { name: "iShares Russell 2000 ETF", symbol: "IWM", stance: "Underweight / Relative short", rationale: "Direct small-cap sensitivity expression." },
        { name: "iShares 1-3 Year Treasury Bond ETF", symbol: "SHY", stance: "Long", rationale: "Keeps carry high while limiting duration risk." },
      ],
      representative_stocks: [
        { name: "Zions Bancorporation", symbol: "ZION", stance: "Underweight", rationale: "Regional lenders are exposed to tighter conditions." },
        { name: "Monster Beverage", symbol: "MNST", stance: "Overweight", rationale: "A quality large-cap alternative if cyclicals stay pressured." },
      ],
      catalysts: [{ name: "Sticky front-end yields", rationale: "2Y yields remain elevated and delay relief." }],
      confirming_signals: [{ name: "Russell 2000 relative weakness persists", rationale: "Small caps keep lagging the larger benchmarks." }],
      invalidation_signals: [{ name: "Front-end rates reprice lower", rationale: "A clearer easing path relieves the core pressure point." }],
      notes: ["Fallback result generated locally because the backend was unavailable."],
    };
  }

  if (lower.includes("credit")) {
    return buildCreditStressResult();
  }

  return buildGenericResult(input);
}

function buildMockSavedTheses(): SavedThesisResponse[] {
  return [
    {
      id: 1,
      input_text: "Credit stress will appear before equities react",
      interpreted_theme: "Credit stress leads equities",
      result: buildCreditStressResult(),
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    },
  ];
}

function buildMockRefreshStatus(): RefreshStatusResponse {
  return {
    mode: "local-first",
    status: "degraded",
    last_success_at: new Date().toISOString(),
    latest_indicator_at: new Date().toISOString(),
    source_summary: "mixed-live",
    next_scheduled_refresh: new Date(Date.now() + 1000 * 60 * 45).toISOString(),
    stale_indicators: [
      {
        code: "cpi_yoy",
        name: "CPI YoY",
        last_updated: new Date(Date.now() - 1000 * 60 * 60 * 24 * 34).toISOString(),
        age_days: 34,
        source: "live-fred",
        max_staleness_days: 45,
      },
    ],
    provider_statuses: [
      {
        provider: "fred",
        status: "degraded",
        indicator_count: 7,
        live_count: 4,
        fallback_count: 2,
        demo_count: 0,
        mixed_count: 1,
        stale_count: 0,
      },
      {
        provider: "yahoo",
        status: "live",
        indicator_count: 10,
        live_count: 10,
        fallback_count: 0,
        demo_count: 0,
        mixed_count: 0,
        stale_count: 0,
      },
      {
        provider: "derived",
        status: "mixed",
        indicator_count: 1,
        live_count: 0,
        fallback_count: 0,
        demo_count: 0,
        mixed_count: 1,
        stale_count: 0,
      },
    ],
    last_digest_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    recent_alert_count: 3,
  };
}

function buildMockAlertConfig(): AlertConfig {
  return {
    regime_change_enabled: true,
    anomaly_severity_threshold: 75,
    digest_cadence: "market_close",
    updated_at: new Date().toISOString(),
  };
}

function buildMockAlertHistory(): AlertHistoryResponse {
  const items: AlertEvent[] = [
    {
      id: 1,
      event_type: "digest",
      title: "Close digest: Slowdown",
      message:
        "Slowdown is the active regime with mixed cross-asset confirmation. Credit and breadth still need attention, but no hard stale-data failure is present.",
      severity: null,
      cadence: "market_close",
      payload: {
        regime: "Slowdown",
        source_summary: "mixed-live",
        top_anomalies: "Equity tape outrunning credit confirmation",
      },
      created_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    },
    {
      id: 2,
      event_type: "regime_change",
      title: "Regime shift: Slowdown",
      message:
        "SignalStack moved from Disinflationary Growth to Slowdown as labor softened and credit confirmation weakened.",
      severity: 74,
      cadence: null,
      payload: {
        current_regime: "Slowdown",
        previous_regime: "Disinflationary Growth",
      },
      created_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    },
    {
      id: 3,
      event_type: "anomaly",
      title: "Equity tape is outrunning credit confirmation",
      message:
        "Stocks are still grinding higher, but both high-yield and investment-grade spreads are widening.",
      severity: 84,
      cadence: null,
      payload: {
        rule_code: "equities_up_credit_worse",
      },
      created_at: new Date(Date.now() - 1000 * 60 * 220).toISOString(),
    },
  ];

  return { items };
}

function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return process.env.NEXT_PUBLIC_API_BASE_URL;
  }
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return "http://localhost:8000";
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(`${getApiBaseUrl()}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`Request failed for ${path}`);
    }

    return (await response.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getOverview(): Promise<OverviewResponse> {
  try {
    return await requestJson<OverviewResponse>("/api/overview");
  } catch {
    return buildMockOverview();
  }
}

export async function getCurrentRegime(): Promise<RegimeCurrentResponse> {
  try {
    return await requestJson<RegimeCurrentResponse>("/api/regime/current");
  } catch {
    return buildMockRegimeCurrent();
  }
}

export async function getRegimeHistory(): Promise<RegimeHistoryResponse> {
  try {
    return await requestJson<RegimeHistoryResponse>("/api/regime/history");
  } catch {
    return buildMockRegimeHistory();
  }
}

export async function getAnomalies(): Promise<AnomalyResponse> {
  try {
    return await requestJson<AnomalyResponse>("/api/anomalies");
  } catch {
    return buildMockAnomalies();
  }
}

export async function analyzeThesis(text: string, save = false): Promise<ThesisResult> {
  try {
    return await requestJson<ThesisResult>("/api/thesis/analyze", {
      method: "POST",
      body: JSON.stringify({ text, save }),
    });
  } catch {
    return mockAnalyzeThesis(text);
  }
}

export async function getSavedTheses(): Promise<SavedThesisResponse[]> {
  try {
    return await requestJson<SavedThesisResponse[]>("/api/thesis/saved");
  } catch {
    return buildMockSavedTheses();
  }
}

export async function persistThesis(text: string): Promise<SavedThesisResponse> {
  return requestJson<SavedThesisResponse>("/api/thesis/saved", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function getRefreshStatus(): Promise<RefreshStatusResponse> {
  try {
    return await requestJson<RefreshStatusResponse>("/api/system/refresh-status");
  } catch {
    return buildMockRefreshStatus();
  }
}

export async function getAlertConfig(): Promise<AlertConfig> {
  try {
    return await requestJson<AlertConfig>("/api/alerts/config");
  } catch {
    return buildMockAlertConfig();
  }
}

export async function updateAlertConfig(config: AlertConfig): Promise<AlertConfig> {
  try {
    return await requestJson<AlertConfig>("/api/alerts/config", {
      method: "PUT",
      body: JSON.stringify(config),
    });
  } catch {
    return {
      ...config,
      updated_at: new Date().toISOString(),
    };
  }
}

export async function getAlertHistory(): Promise<AlertHistoryResponse> {
  try {
    return await requestJson<AlertHistoryResponse>("/api/alerts/history");
  } catch {
    return buildMockAlertHistory();
  }
}

export async function runDigest(): Promise<AlertEvent> {
  try {
    return await requestJson<AlertEvent>("/api/alerts/run-digest", {
      method: "POST",
      body: JSON.stringify({}),
    });
  } catch {
    return {
      ...buildMockAlertHistory().items[0],
      id: Date.now(),
      created_at: new Date().toISOString(),
      cadence: "manual",
      title: "Manual digest: Slowdown",
    };
  }
}
