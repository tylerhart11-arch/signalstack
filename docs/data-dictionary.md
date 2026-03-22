# Data Dictionary

## Core Database Tables

### `indicator_snapshots`

- `indicator_code`: internal code for each tracked series
- `timestamp`: observation time
- `value`: normalized numeric value
- `source`: `live-*`, `demo`, or `demo-fallback-*`
- `meta`: display metadata such as unit and label

### `regime_history`

- `as_of`: evaluation timestamp
- `regime`: winning regime label
- `confidence`: model confidence score
- `summary`: text summary of why the regime won
- `drivers`: serialized top driver list
- `supporting_indicators`: compact numeric context

### `anomaly_feed_items`

- `detected_at`: anomaly timestamp
- `rule_code`: stable anomaly rule id
- `title`: analyst-readable signal name
- `category`: anomaly grouping
- `severity`: ranked signal score
- `related_assets`: asset labels tied to the signal
- `supporting_metrics`: feed metrics used to explain the ranking

### `saved_theses`

- `input_text`: raw thesis text
- `interpreted_theme`: mapped theme label
- `result`: full structured thesis output payload

## Featured Overview Indicators

- `sp500`
- `nasdaq100`
- `russell2000`
- `vix`
- `us2y`
- `us10y`
- `s2s10s`
- `hy_spread`
- `ig_spread`
- `dxy`
- `wti`
- `gold`
- `copper`
- `cpi_yoy`
- `core_cpi_yoy`
- `unemployment_rate`
- `fed_funds_rate`

## Additional Internal Indicators

These power regime and anomaly logic even if they are not all shown on the main overview page:

- `qqq`
- `iwm`
- `xle`
- `xlf`
- `hyg`
- `lqd`
