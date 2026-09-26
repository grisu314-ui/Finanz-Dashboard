import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from fever.config import series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, fred

FIXTURES = Path(__file__).parent / "fixtures" / "fred"
CATALOG = series_catalog()
RETRIEVED = datetime(2026, 9, 25, 15, 0, tzinfo=timezone.utc)


def fixture(name):
    return (FIXTURES / name).read_bytes()


def response(observations, **extra):
    return json.dumps({"count": len(observations), "offset": 0, "observations": observations, **extra}).encode()


def test_fixture_is_parsed_and_missing_values_are_skipped():
    rows = fred.parse(fixture("BAMLH0A0HYM2.json"), CATALOG["bamlh0a0hym2"], RETRIEVED)
    dates = [r.obs_date for r in rows]
    assert rows[0] == Row(date(2023, 9, 26), 3.0)
    assert rows[-1] == Row(date(2026, 9, 24), 3.09)
    assert date(2025, 12, 25) not in dates  # "." on Christmas Day
    assert date(2026, 5, 31) in dates  # month end on a Sunday is a real observation
    assert len(rows) == 10


@pytest.mark.parametrize(
    "content, message",
    [
        (b"<html>", "keine gültige JSON"),
        (b"\xff", "keine gültige JSON"),
        (json.dumps({"error_code": 400}).encode(), "ohne Liste 'observations'"),
        (json.dumps([]).encode(), "ohne Liste 'observations'"),
        (json.dumps({"count": 3, "offset": 0, "observations": [{"date": "2026-09-24", "value": "2.8"}]}).encode(),
         "unvollständige Antwort: count 3, geliefert 1"),
        (response([{"date": "2026-09-24"}]), "Eintrag 0: 'date' oder 'value' fehlt"),
        (response([{"date": "2026-09-24", "value": 2.8}]), "Eintrag 0: 'date' oder 'value' fehlt"),
        (response([{"date": "24.09.2026", "value": "2.8"}]), "Eintrag 0: unlesbar"),
        (response([{"date": "20260924", "value": "2.8"}]), "Eintrag 0: unlesbar"),
        (response([{"date": "2026-09-24", "value": "n/a"}]), "Eintrag 0: unlesbar"),
        (response([{"date": "2026-09-24", "value": "inf"}]), "ungültiger Wert"),
        (response([{"date": "2026-09-24", "value": "."}]), "keine Werte"),
        (response([{"date": "2026-09-24", "value": "1"}, {"date": "2026-09-24", "value": "2"}]), "doppelt"),
    ],
)
def test_format_changes_are_errors(content, message):
    with pytest.raises(SourceError, match=message):
        fred.parse(content, CATALOG["bamlh0a0hym2"], RETRIEVED)


class RecordingClient:
    def get(self, url, params=None):
        self.url, self.params = url, params
        return Fetched(b"{}", RETRIEVED, 200)


def test_fetch_sends_series_id_key_and_format(monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "k" * 32)
    client = RecordingClient()
    fred.fetch(client, CATALOG["nfci"])
    assert client.url == "https://api.stlouisfed.org/fred/series/observations"
    assert client.params == {"series_id": "NFCI", "api_key": "k" * 32, "file_type": "json"}


def test_fetch_without_key_is_an_error(monkeypatch):
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    with pytest.raises(SourceError, match="FRED_API_KEY ist nicht gesetzt"):
        fred.fetch(RecordingClient(), CATALOG["nfci"])


def test_source_host_is_on_the_allowlist():
    assert urlsplit(fred.URL).hostname in ALLOWED_HOSTS
