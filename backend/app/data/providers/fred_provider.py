from __future__ import annotations

import csv
from datetime import UTC, datetime
from io import StringIO

import requests


class FredProvider:
    api_url = "https://api.stlouisfed.org/fred/series/observations"
    csv_url = "https://fred.stlouisfed.org/graph/fredgraph.csv"

    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    def fetch_series(self, series_id: str) -> list[tuple[datetime, float]]:
        if self.api_key:
            try:
                return self._fetch_series_from_api(series_id)
            except requests.RequestException:
                pass

        return self._fetch_series_from_csv(series_id)

    def _fetch_series_from_api(self, series_id: str) -> list[tuple[datetime, float]]:
        response = requests.get(
            self.api_url,
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

    def _fetch_series_from_csv(self, series_id: str) -> list[tuple[datetime, float]]:
        response = requests.get(
            self.csv_url,
            params={"id": series_id},
            timeout=20,
        )
        response.raise_for_status()

        reader = csv.DictReader(StringIO(response.text))
        observations: list[tuple[datetime, float]] = []
        value_column = series_id

        for item in reader:
            raw_date = item.get("observation_date")
            raw_value = item.get(value_column)
            if not raw_date or raw_value in {".", None, ""}:
                continue
            timestamp = datetime.fromisoformat(raw_date).replace(tzinfo=UTC)
            observations.append((timestamp, float(raw_value)))

        if not observations:
            raise ValueError(f"No observations returned for FRED series {series_id}.")

        return observations
