"""ECB, OFR and Fed parsers against shortened real responses (fetched 26.09.2026)."""

from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from fever.config import series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, ecb, fed, ofr

FIXTURES = Path(__file__).parent / "fixtures"
CATALOG = series_catalog()
AT = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def fixture(path):
    return (FIXTURES / path).read_bytes()


class RecordingClient:
    def get(self, url, params=None):
        self.url, self.params = url, params
        return Fetched(b"", AT, 200)


# --- ECB ---------------------------------------------------------------------------------


def test_ecb_ciss_is_parsed():
    rows = ecb.parse(fixture("ecb/CISS_D.U2.Z0Z.4F.EC.SS_CIN.IDX.csv"), CATALOG["ecb_ciss"], AT)
    assert rows[0] == Row(date(1980, 1, 3), 0.135571)
    assert rows[-1].obs_date == date(2026, 9, 24)
    assert len(rows) == 4


def test_ecb_empty_value_is_a_missing_value():
    rows = ecb.parse(fixture("ecb/EXR_D.USD.EUR.SP00.A.csv"), CATALOG["ecb_exr_usd"], AT)
    assert date(1999, 12, 31) not in [row.obs_date for row in rows]
    assert rows[-1] == Row(date(2026, 9, 25), 1.1403)
    assert len(rows) == 4


@pytest.mark.parametrize(
    "content, message",
    [
        (b"KEY,TIME_PERIOD\nEXR.D.USD.EUR.SP00.A,2026-09-25\n", "Spalten fehlen: OBS_VALUE"),
        (b"KEY,TIME_PERIOD,OBS_VALUE\nEXR.D.JPY.EUR.SP00.A,2026-09-25,180.1\n", "unerwartete Reihe"),
        (b"KEY,TIME_PERIOD,OBS_VALUE\nEXR.D.USD.EUR.SP00.A,2026-09,1.14\n", "Zeile 2: unlesbar"),
        (b"KEY,TIME_PERIOD,OBS_VALUE\nEXR.D.USD.EUR.SP00.A,2026-09-25,n/a\n", "Zeile 2: unlesbar"),
        (b"KEY,TIME_PERIOD,OBS_VALUE\n", "keine Werte"),
        (b"<html>Service Unavailable</html>", "Spalten fehlen"),
    ],
)
def test_ecb_format_changes_are_errors(content, message):
    with pytest.raises(SourceError, match=message):
        ecb.parse(content, CATALOG["ecb_exr_usd"], AT)


def test_ecb_fetch_builds_the_sdmx_request():
    client = RecordingClient()
    ecb.fetch(client, CATALOG["ecb_ciss"])
    assert client.url == "https://data-api.ecb.europa.eu/service/data/CISS/D.U2.Z0Z.4F.EC.SS_CIN.IDX"
    assert client.params == {"format": "csvdata", "detail": "dataonly"}


# --- OFR ---------------------------------------------------------------------------------


def test_ofr_columns_are_read_by_name():
    content = fixture("ofr/fsi.csv")
    total = ofr.parse(content, CATALOG["ofr_fsi"], AT)
    credit = ofr.parse(content, CATALOG["ofr_fsi_credit"], AT)
    emerging = ofr.parse(content, CATALOG["ofr_fsi_emerging_markets"], AT)
    assert total[0] == Row(date(2000, 1, 3), 2.14)
    assert credit[-1] == Row(date(2026, 9, 23), -1.148)
    assert emerging[-1] == Row(date(2026, 9, 23), -0.562)


@pytest.mark.parametrize(
    "content, message",
    [
        (b"Datum,OFR FSI\n2026-09-23,1\n", "unerwartete Kopfzeile"),
        (b"Date,OFR FSI total\n2026-09-23,1\n", "Spalte 'OFR FSI' fehlt"),
        (b"Date,OFR FSI\n09/23/2026,1\n", "Zeile 2: unlesbar"),
        (b"Date,OFR FSI\n2026-09-23,1,2\n", "Zeile 2: 3 statt 2 Felder"),
        (b"Date,OFR FSI\n2026-09-23,\n", "keine Werte"),
    ],
)
def test_ofr_format_changes_are_errors(content, message):
    with pytest.raises(SourceError, match=message):
        ofr.parse(content, CATALOG["ofr_fsi"], AT)


def test_ofr_empty_cell_is_a_missing_value():
    rows = ofr.parse(b"Date,OFR FSI\n2026-09-22,1.5\n2026-09-23,\n", CATALOG["ofr_fsi"], AT)
    assert rows == [Row(date(2026, 9, 22), 1.5)]


# --- Fed (EBP) ---------------------------------------------------------------------------


def test_fed_ebp_and_gz_spread_are_read_by_name():
    content = fixture("fed/ebp_csv.csv")
    ebp = fed.parse(content, CATALOG["fed_ebp"], AT)
    gz = fed.parse(content, CATALOG["fed_gz_spread"], AT)
    assert ebp[0] == Row(date(1973, 1, 1), -0.046854494)
    assert ebp[-1].obs_date == date(2026, 7, 1)
    assert gz[-1] == Row(date(2026, 7, 1), 0.8422860534739828)


def test_fed_monthly_value_must_be_dated_on_the_first():
    with pytest.raises(SourceError, match="nicht auf den Monatsersten"):
        fed.parse(b"date,ebp\n7/15/2026,0.1\n", CATALOG["fed_ebp"], AT)


# --- common ------------------------------------------------------------------------------


@pytest.mark.parametrize("module", [ecb, ofr, fed])
def test_source_hosts_are_on_the_allowlist(module):
    assert urlsplit(module.URL.format(flow="X", key="Y")).hostname in ALLOWED_HOSTS


def test_ofr_and_fed_fetch_their_fixed_file():
    for module, series in ((ofr, CATALOG["ofr_fsi_credit"]), (fed, CATALOG["fed_gz_spread"])):
        client = RecordingClient()
        module.fetch(client, series)
        assert client.url == module.URL and client.params is None


def test_columns_are_matched_exactly():
    series = replace(CATALOG["ofr_fsi"], source_id="Credit ")
    with pytest.raises(SourceError, match="fehlt"):
        ofr.parse(fixture("ofr/fsi.csv"), series, AT)
