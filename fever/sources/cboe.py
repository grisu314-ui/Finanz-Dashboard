"""Cboe daily index closes: one CSV per index with its full history.

Two formats exist (checked 26.09.2026): DATE,OPEN,HIGH,LOW,CLOSE (VIX, VIX9D,
VIX3M, VIX6M) and DATE,<symbol> (VVIX, SKEW); dates are MM/DD/YYYY. Only the
close is stored. Licence: personal, non-commercial use (decision E-26).
"""

import csv
import io
from datetime import datetime
from zoneinfo import ZoneInfo

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

# cdn.cboe.com/api/... redirects here; asking the target directly saves a request.
URL = "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/{symbol}_History.csv"
NEW_YORK = ZoneInfo("America/New_York")
_OHLC = ["DATE", "OPEN", "HIGH", "LOW", "CLOSE"]
_MAX_SHOWN = 120  # characters of a broken line quoted in an error message


def fetch(client: HttpClient, series: Series) -> Fetched:
    return client.get(URL.format(symbol=series.source_id))


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SourceError(f"keine lesbare CSV-Datei: {exc}") from None
    lines = csv.reader(io.StringIO(text))
    header = next(lines, None)
    if header == _OHLC:
        column = 4
    elif header == ["DATE", series.source_id]:
        column = 1
    else:
        raise SourceError(f"unerwartete Kopfzeile: {str(header)[:_MAX_SHOWN]}")

    rows = []
    for number, fields in enumerate(lines, start=2):
        if not fields:
            continue
        if len(fields) != len(header):
            raise SourceError(f"Zeile {number}: {len(fields)} statt {len(header)} Felder")
        try:
            rows.append(Row(datetime.strptime(fields[0], "%m/%d/%Y").date(), float(fields[column])))
        except ValueError:
            raise SourceError(f"Zeile {number}: unlesbar: {','.join(fields)[:_MAX_SHOWN]}") from None
    rows = checked(rows)

    # The file might carry the running trading day before its final update. Stored once, such a
    # value would stay in the append-only archive as the close, so it counts only from release_time on.
    now = retrieved_at.astimezone(NEW_YORK)
    if now.time() < series.release_time:
        rows = [row for row in rows if row.obs_date < now.date()]
    return rows
