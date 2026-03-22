from __future__ import annotations

from datetime import UTC

import yfinance as yf


class MarketProvider:
    def fetch_history(self, symbol: str, period: str = "8mo", interval: str = "1d") -> list[tuple]:
        ticker = yf.Ticker(symbol)
        frame = ticker.history(period=period, interval=interval, auto_adjust=False)
        if frame.empty:
            raise ValueError(f"No Yahoo Finance history returned for {symbol}.")

        observations: list[tuple] = []
        for index, row in frame.iterrows():
            raw_timestamp = index.to_pydatetime()
            timestamp = raw_timestamp.replace(tzinfo=UTC) if raw_timestamp.tzinfo is None else raw_timestamp.astimezone(UTC)
            observations.append((timestamp, float(row["Close"])))

        return observations
