"""Shiller's ie_data.xls against a synthetic fixture (E-27), and the Z.1 margin series via FRED."""

from dataclasses import replace
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import xlrd

from fever.config import group_members, series_catalog
from fever.http import ALLOWED_HOSTS, Fetched
from fever.sources import Row, SourceError, fred, shiller
from fever.sources.update import estimated_release, update_group
from fever.store.db import make_engine

FIXTURES = Path(__file__).parent / "fixtures"
XLS = (FIXTURES / "shiller" / "ie_data.xls").read_bytes()
CATALOG = series_catalog()
CAPE, ECY = CATALOG["shiller_cape"], CATALOG["shiller_ecy"]
AT = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)
LINK = "//img1.wsimg.com/blobby/go/e5e7/downloads/70fe/ie_data.xls?ver=1788371540009"


def page(*links):
    anchors = "".join(f'<a href="{link}">Download</a>' for link in links)
    return f'<html><body><a href="//img1.wsimg.com/x/Fig3-1%20(1).xls?ver=1">Fig</a>{anchors}</body></html>'.encode()


class PageClient:
    def __init__(self, page_content, file_content=XLS):
        self.pages = {shiller.PAGE_URL: page_content}
        self.file_content, self.urls = file_content, []

    def get(self, url, params=None):
        self.urls.append(url)
        return Fetched(self.pages.get(url, self.file_content), AT, 200)


def test_cape_and_excess_cape_yield_are_read_by_their_header_text():
    cape = shiller.parse(XLS, CAPE, AT)
    ecy = shiller.parse(XLS, ECY, AT)
    assert cape[0] == Row(date(1881, 1, 1), 18.0)  # "NA" rows before 1881 are missing values
    assert ecy[0] == Row(date(1881, 1, 1), -0.01)  # empty cells too
    assert cape[-1] == Row(date(2026, 9, 1), 40.0) and ecy[-1] == Row(date(2026, 9, 1), 0.0105)
    assert len(cape) == len(ecy) == 7  # the note row below the data is skipped


def test_october_is_written_as_point_one():
    dates = [row.obs_date for row in shiller.parse(XLS, CAPE, AT)]
    assert dates[2:6] == [date(2025, 10, 1), date(2025, 11, 1), date(2025, 12, 1), date(2026, 1, 1)]


@pytest.mark.parametrize("label, message", [("CAPE", "Spalte 'CAPE' fehlt"), ("TR CAPE", "fehlt"), ("Excess CAPE", "fehlt")])
def test_columns_must_match_the_whole_header_text(label, message):
    with pytest.raises(SourceError, match=message):
        shiller.parse(XLS, replace(CAPE, source_id=label), AT)


@pytest.mark.parametrize(
    "value, message",
    [(2026.13, "kein Monat"), (2026.095, "kein Monat"), (2026.0, "kein Monat"), (0.05, "kein Monat"), (-2026.09, "kein Monat")],
)
def test_impossible_months_are_errors(value, message):
    with pytest.raises(SourceError, match=message):
        shiller._month(value, 9)


@pytest.mark.parametrize(
    "content, message",
    [
        (b"<html>Service Unavailable</html>", "keine Excel-Datei"),
        (shiller._OLE2 + b"\x00" * 600, "Datei nicht lesbar"),
    ],
)
def test_other_content_is_an_error(content, message):
    with pytest.raises(SourceError, match=message):
        shiller.parse(content, CAPE, AT)


class FakeSheet:
    """Just the part of xlrd's Sheet that the parser uses; strings are text cells, floats numbers."""

    def __init__(self, rows):
        self.rows = rows
        self.nrows, self.ncols = len(rows), max(len(row) for row in rows)

    def cell(self, row, column):
        value = self.rows[row][column] if column < len(self.rows[row]) else ""
        if isinstance(value, float):
            return xlrd.sheet.Cell(xlrd.XL_CELL_NUMBER, value)
        return xlrd.sheet.Cell(xlrd.XL_CELL_TEXT if value else xlrd.XL_CELL_EMPTY, value)

    def cell_value(self, row, column):
        return self.cell(row, column).value


def parse_rows(monkeypatch, rows, series=ECY):
    class Book:
        def sheet_by_name(self, name):
            return FakeSheet(rows)

    monkeypatch.setattr(shiller.xlrd, "open_workbook", lambda file_contents: Book())
    return shiller.parse(shiller._OLE2, series, AT)


HEAD = [["", "Excess"], ["Date", "CAPE Yield"]]


@pytest.mark.parametrize(
    "rows, message",
    [
        ([["Datum", "Excess CAPE Yield"], [2026.09, 0.01]], "Kopfzeile mit 'Date'"),
        (HEAD + [[2026.09, "n/a"]], "Zeile 3: Wert unlesbar: 'n/a'"),
        (HEAD + [["2026-09", 0.01]], "Zeile 3: Datum unlesbar"),
        ([["", "Excess", "Excess"], ["Date", "CAPE Yield", "CAPE Yield"], [2026.09, 0.01, 0.02]], "mehrdeutig"),
        (HEAD + [[2026.09, "NA"]], "keine Werte"),
    ],
)
def test_layout_changes_are_errors(monkeypatch, rows, message):
    with pytest.raises(SourceError, match=message):
        parse_rows(monkeypatch, rows)


def test_header_text_is_compared_with_single_blanks(monkeypatch):
    rows = [["", "  Excess "], ["Date", "CAPE   Yield"], [2026.09, 0.01]]
    assert parse_rows(monkeypatch, rows) == [Row(date(2026, 9, 1), 0.01)]


def test_a_missing_sheet_is_an_error(monkeypatch):
    monkeypatch.setattr(shiller, "SHEET", "Daten")
    with pytest.raises(SourceError, match="Datei nicht lesbar: XLRDError"):
        shiller.parse(XLS, CAPE, AT)


def test_fetch_takes_the_one_ie_data_link_from_the_page():
    client = PageClient(page(LINK))
    fetched = shiller.fetch(client, CAPE)
    assert client.urls == [shiller.PAGE_URL, "https:" + LINK] and fetched.content == XLS
    assert all(urlsplit(url).hostname in ALLOWED_HOSTS for url in client.urls)


def test_the_same_link_twice_counts_once():
    client = PageClient(page(LINK, LINK))
    shiller.fetch(client, CAPE)
    assert client.urls[-1] == "https:" + LINK


def test_html_entities_in_the_link_are_decoded():
    client = PageClient(page(LINK + "&amp;x=1"))
    shiller.fetch(client, CAPE)
    assert client.urls[-1] == "https:" + LINK + "&x=1"


@pytest.mark.parametrize(
    "links, message",
    [
        ((), "0 Links"),
        ((LINK, LINK.replace("1788371540009", "1790000000000")), "2 Links"),
        (("//files.example.com/ie_data.xls",), "0 Links"),
        (("http://img1.wsimg.com/a/ie_data.xls",), "0 Links"),
    ],
)
def test_no_unique_link_on_the_host_is_an_error(links, message):
    with pytest.raises(SourceError, match=message):
        shiller.fetch(PageClient(page(*links)), CAPE)


def test_the_group_fetches_page_and_file_once_and_archives_the_file(migrated_dir):
    engine = make_engine(migrated_dir)
    client = PageClient(page(LINK))
    results = update_group(engine, migrated_dir, client, group_members(CATALOG)["shiller"], clock=lambda: AT)
    assert len(client.urls) == 2 and [result.added for result in results] == [7, 7]
    [raw] = (migrated_dir / "raw" / "shiller" / "shiller").glob("*.gz")
    assert raw.stat().st_size > 0


def test_shiller_backfill_counts_a_month_only_after_its_end():
    # E-44: 01.08.2026 + 45 days = Tuesday 15.09.2026, 16:00 EDT
    assert estimated_release(date(2026, 8, 1), CAPE) == datetime(2026, 9, 15, 20, 0, tzinfo=timezone.utc)


# --- margin debt from the Fed Financial Accounts (Z.1) via FRED, E-42 ---------------------------


def test_z1_margin_series_is_parsed_and_dated_on_the_first_day_of_the_quarter():
    series = CATALOG["bogz1fl663067003q"]
    rows = fred.parse((FIXTURES / "fred" / "BOGZ1FL663067003Q.json").read_bytes(), series, AT)
    assert rows == [Row(date(1945, 10, 1), 1252.0), Row(date(2026, 1, 1), 622199.0), Row(date(2026, 4, 1), 742321.0)]
    assert series.frequency == "quarterly" and series.tolerance_days == 10


def test_z1_estimated_release_uses_the_regular_maximum_lag():
    # E-44: Q2 2026 (dated 01.04.2026) + 175 days = Wednesday 23.09.2026, 13:15 EDT; actual 11.09.2026
    assert estimated_release(date(2026, 4, 1), CATALOG["bogz1fl663067003q"]) == datetime(2026, 9, 23, 17, 15, tzinfo=timezone.utc)
