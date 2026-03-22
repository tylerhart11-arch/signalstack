from __future__ import annotations

from datetime import UTC, datetime

import requests


class FredProvider:
    base_url = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def fetch_series(self, series_id: str) -> list[tuple[datetime, float]]:
        if not self.api_key:
            raise ValueError("FRED_API_KEY is not configured.")

        response = requests.get(
            self.base_url,
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "asc",
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()

        observations: list[tuple[datetime, float]] = []
        for item in payload.get("observations", []):
            value = item.get("value")
            if value in {".", None, ""}:
                continue
            timestamp = datetime.fromisoformat(item["date"]).replace(tzinfo=UTC)
            observations.append((timestamp, float(value)))

        return observations
