from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from fever.config import series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, cboe

FIXTURES = Path(__file__).parent / "fixtures" / "cboe"
CATALOG = series_catalog()
# Saturday 26.09.2026, 12:00 UTC: after the release time of Friday's close.
LATER = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def fixture(name):
    return (FIXTURES / name).read_bytes()


def test_ohlc_file_yields_the_close():
    rows = cboe.parse(fixture("VIX_History.csv"), CATALOG["vix"], LATER)
    assert len(rows) == 6
    assert rows[0] == Row(date(1990, 1, 2), 21.0)
    assert rows[-1] == Row(date(2026, 9, 25), 26.0)  # CLOSE, not OPEN/HIGH/LOW (synthetic values)


def test_single_value_file_is_read_in_full():
    rows = cboe.parse(fixture("VVIX_History.csv"), CATALOG["vvix"], LATER)
    # The start date (E-24) is applied when storing, not by the parser.
    assert rows[0] == Row(date(2006, 3, 6), 80.0)
    assert rows[-1] == Row(date(2026, 9, 25), 87.0)
    assert len(rows) == 8


@pytest.mark.parametrize(
    "content, message",
    [
        (b"Date,Open,High,Low,Close\n01/02/1990,1,1,1,1\n", "Kopfzeile"),
        (b"DATE,SKEW\n01/02/1990,126.09\n", "Kopfzeile"),  # other symbol than configured
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,1,1,1\n", "Zeile 2: 4 statt 5 Felder"),
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n1990-01-02,1,1,1,1\n", "Zeile 2: unlesbar"),
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,1,1,1,n/a\n", "Zeile 2: unlesbar"),
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,1,1,1,nan\n", "ungültiger Wert"),
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n01/02/1990,1,1,1,1\n01/02/1990,2,2,2,2\n", "doppelt"),
        (b"DATE,OPEN,HIGH,LOW,CLOSE\n", "keine Werte"),
        (b"", "Kopfzeile"),
        (b"\xff\xfe", "keine lesbare CSV"),
    ],
)
def test_format_changes_are_errors(content, message):
    with pytest.raises(SourceError, match=message):
        cboe.parse(content, CATALOG["vix"], LATER)


def test_running_day_counts_only_from_the_release_time():
    content = b"DATE,OPEN,HIGH,LOW,CLOSE\n09/24/2026,1,1,1,15.67\n09/25/2026,1,1,1,14.87\n"
    series = CATALOG["vix"]  # release 22:00 New York
    # Friday 25.09.2026, 21:59 New York (EDT = UTC-4): the row of the day is not final yet.
    before = datetime(2026, 9, 26, 1, 59, tzinfo=timezone.utc)
    assert [r.obs_date for r in cboe.parse(content, series, before)] == [date(2026, 9, 24)]
    at_release = datetime(2026, 9, 26, 2, 0, tzinfo=timezone.utc)
    assert [r.obs_date for r in cboe.parse(content, series, at_release)] == [date(2026, 9, 24), date(2026, 9, 25)]


def test_fetch_asks_the_cdn_for_the_configured_symbol():
    class Client:
        def get(self, url, params=None):
            self.url, self.params = url, params
            return Fetched(b"", LATER, 200)

    client = Client()
    cboe.fetch(client, CATALOG["vix3m"])
    assert client.url == "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv"
    assert client.params is None


def test_source_host_is_on_the_allowlist():
    assert urlsplit(cboe.URL.format(symbol="VIX")).hostname in ALLOWED_HOSTS
