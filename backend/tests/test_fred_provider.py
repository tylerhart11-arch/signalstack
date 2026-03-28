from datetime import UTC, datetime

import requests

from app.data.providers.fred_provider import FredProvider


class DummyResponse:
    def __init__(self, text: str = "", json_payload: dict | None = None, status_code: int = 200) -> None:
        self.text = text
        self._json_payload = json_payload or {}
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._json_payload


def test_fetch_series_uses_api_when_key_is_configured(monkeypatch) -> None:
    calls: list[tuple[str, dict | None]] = []

    def fake_get(url: str, params: dict | None = None, timeout: int | None = None):
        calls.append((url, params))
        return DummyResponse(
            json_payload={
                "observations": [
                    {"date": "2026-01-01", "value": "4.25"},
                    {"date": "2026-02-01", "value": "."},
                    {"date": "2026-03-01", "value": "4.00"},
                ]
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)

    observations = FredProvider(api_key="test-key").fetch_series("FEDFUNDS")

    assert calls == [
        (
            "https://api.stlouisfed.org/fred/series/observations",
            {
                "series_id": "FEDFUNDS",
                "api_key": "test-key",
                "file_type": "json",
                "sort_order": "asc",
            },
        )
    ]
    assert observations == [
        (datetime(2026, 1, 1, tzinfo=UTC), 4.25),
        (datetime(2026, 3, 1, tzinfo=UTC), 4.0),
    ]


def test_fetch_series_falls_back_to_public_csv_when_no_key_is_configured(monkeypatch) -> None:
    calls: list[tuple[str, dict | None]] = []

    def fake_get(url: str, params: dict | None = None, timeout: int | None = None):
        calls.append((url, params))
        return DummyResponse(
            text="observation_date,DGS2\n2026-03-20,3.95\n2026-03-21,\n2026-03-23,3.90\n"
        )

    monkeypatch.setattr(requests, "get", fake_get)

    observations = FredProvider(api_key=None).fetch_series("DGS2")

    assert calls == [
        (
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            {"id": "DGS2"},
        )
    ]
    assert observations == [
        (datetime(2026, 3, 20, tzinfo=UTC), 3.95),
        (datetime(2026, 3, 23, tzinfo=UTC), 3.9),
    ]


def test_fetch_series_falls_back_to_public_csv_when_api_request_fails(monkeypatch) -> None:
    calls: list[tuple[str, dict | None]] = []

    def fake_get(url: str, params: dict | None = None, timeout: int | None = None):
        calls.append((url, params))
        if "api.stlouisfed.org" in url:
            raise requests.HTTPError("bad key")
        return DummyResponse(
            text="observation_date,BAMLH0A0HYM2\n2026-03-20,3.45\n2026-03-21,\n2026-03-23,3.52\n"
        )

    monkeypatch.setattr(requests, "get", fake_get)

    observations = FredProvider(api_key="bad-key").fetch_series("BAMLH0A0HYM2")

    assert calls == [
        (
            "https://api.stlouisfed.org/fred/series/observations",
            {
                "series_id": "BAMLH0A0HYM2",
                "api_key": "bad-key",
                "file_type": "json",
                "sort_order": "asc",
            },
        ),
        (
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            {"id": "BAMLH0A0HYM2"},
        ),
    ]
    assert observations == [
        (datetime(2026, 3, 20, tzinfo=UTC), 3.45),
        (datetime(2026, 3, 23, tzinfo=UTC), 3.52),
    ]
