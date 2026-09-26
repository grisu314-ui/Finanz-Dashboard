"""Robert J. Shiller's stock market data (ie_data.xls): CAPE and Excess CAPE Yield, monthly.

The download path on img1.wsimg.com carries changing identifiers, so fetch() reads the
official download page first and takes the one link to ie_data.xls from it (no terms of use
on the site, robots.txt blocks only /404; checked 26.09.2026). source_id is the full header
text of the column in sheet "Data": all header cells down to the "Date" row, joined by
blanks, e.g. "Excess CAPE Yield". Both series come from one download (group "shiller", E-36).

Dates are YYYY.MM with October as .1; values are dated on the first of the month. The row of
the current month is preliminary (price and GS10 of the first trading day, CPI estimated) and
revised by later uploads. "NA" or an empty cell is a missing value. The file contains S&P
data: private use only, no redistribution; test fixtures are synthetic (E-27).
"""

import html
import re
from datetime import date, datetime

import xlrd

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

PAGE_URL = "https://shillerdata.com/"
SHEET = "Data"
_LINK = re.compile(r'href="((?:https:)?//img1\.wsimg\.com/[^"\s]*/ie_data\.xls(?:\?[^"\s]*)?)"')
_OLE2 = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # signature of an Excel 97-2003 file
_HEADER_SEARCH_ROWS = 30
_MISSING = ("", "NA")
_SHOWN = 30  # characters of a broken cell quoted in an error message


def fetch(client: HttpClient, series: Series) -> Fetched:
    page = client.get(PAGE_URL)
    links = {html.unescape(link) for link in _LINK.findall(page.content.decode("utf-8", errors="replace"))}
    if len(links) != 1:
        raise SourceError(f"{len(links)} Links auf ie_data.xls in {PAGE_URL} (erwartet: genau einer auf img1.wsimg.com)")
    link = links.pop()
    return client.get(link if link.startswith("https:") else "https:" + link)


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    if not content.startswith(_OLE2):
        raise SourceError("keine Excel-Datei im Format 97-2003 (.xls)")
    try:
        sheet = xlrd.open_workbook(file_contents=content).sheet_by_name(SHEET)
    except Exception as exc:  # xlrd raises many types on damaged files; reported, never swallowed
        raise SourceError(f"Datei nicht lesbar: {type(exc).__name__}: {str(exc)[:120]}") from None
    header = _header_row(sheet)
    column = _column(sheet, header, series.source_id)
    rows = []
    for index in range(header + 1, sheet.nrows):
        stamp, cell = sheet.cell(index, 0), sheet.cell(index, column)
        if _is_blank(stamp):
            continue  # notes below the data
        if stamp.ctype != xlrd.XL_CELL_NUMBER:
            raise SourceError(f"Zeile {index + 1}: Datum unlesbar: {str(stamp.value)[:_SHOWN]!r}")
        obs_date = _month(stamp.value, index)
        if cell.ctype == xlrd.XL_CELL_NUMBER:
            rows.append(Row(obs_date, float(cell.value)))
        elif not (_is_blank(cell) or (cell.ctype == xlrd.XL_CELL_TEXT and cell.value.strip() in _MISSING)):
            raise SourceError(f"Zeile {index + 1}: Wert unlesbar: {str(cell.value)[:_SHOWN]!r}")
    return checked(rows)


def _is_blank(cell) -> bool:
    return cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or (
        cell.ctype == xlrd.XL_CELL_TEXT and cell.value.strip() == ""
    )


def _header_row(sheet) -> int:
    for index in range(min(sheet.nrows, _HEADER_SEARCH_ROWS)):
        value = sheet.cell_value(index, 0)
        if isinstance(value, str) and value.strip() == "Date":
            return index
    raise SourceError(f"Kopfzeile mit 'Date' in Spalte A fehlt in Blatt {SHEET!r}")


def _column(sheet, header: int, label: str) -> int:
    """The one column whose header cells, joined by blanks, read exactly `label`."""
    matches = []
    for column in range(sheet.ncols):
        parts = [str(sheet.cell_value(index, column)) for index in range(header + 1)]
        if " ".join(" ".join(parts).split()) == label:
            matches.append(column)
    if len(matches) != 1:
        problem = "fehlt" if not matches else f"ist mehrdeutig ({len(matches)} Spalten)"
        raise SourceError(f"Spalte {label!r} {problem} in Blatt {SHEET!r}")
    return matches[0]


def _month(value: float, index: int) -> date:
    """YYYY.MM as a number, October written as .1, to the first day of that month."""
    year = int(value)
    month = round((value - year) * 100)
    if not (1 <= month <= 12 and abs(value - (year + month / 100)) < 1e-6):
        raise SourceError(f"Zeile {index + 1}: Datum {value!r} ist kein Monat im Format JJJJ.MM")
    try:
        return date(year, month, 1)
    except ValueError:  # year outside 1..9999
        raise SourceError(f"Zeile {index + 1}: Datum {value!r} ist kein Monat im Format JJJJ.MM") from None
