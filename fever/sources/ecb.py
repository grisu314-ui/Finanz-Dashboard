"""ECB Data Portal (SDMX REST, CSV): CISS and ECB reference exchange rates.

source_id is "<flow>/<key>", e.g. "CISS/D.U2.Z0Z.4F.EC.SS_CIN.IDX"; the response lists
the series as KEY "<flow>.<key>". Empty OBS_VALUE cells (e.g. TARGET holidays in the
reference rates until 2012) are missing values. Reuse: free with the source note
"Source: ECB statistics." (checked 26.09.2026).
"""

import csv
import io
from datetime import date, datetime

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

URL = "https://data-api.ecb.europa.eu/service/data/{flow}/{key}"
_REQUIRED = ("KEY", "TIME_PERIOD", "OBS_VALUE")


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    # `since` is not needed: every request returns the full history.
    flow, key = series.source_id.split("/", 1)
    return client.get(URL.format(flow=flow, key=key), {"format": "csvdata", "detail": "dataonly"})


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        header = reader.fieldnames or []
        records = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise SourceError(f"keine lesbare CSV-Datei: {exc}") from None
    missing = [name for name in _REQUIRED if name not in header]
    if missing:
        raise SourceError(f"Spalten fehlen: {', '.join(missing)}")
    expected_key = series.source_id.replace("/", ".", 1)
    rows = []
    for number, record in enumerate(records, start=2):
        if record["KEY"] != expected_key:
            raise SourceError(f"Zeile {number}: unerwartete Reihe {str(record['KEY'])[:80]!r}")
        if (record["OBS_VALUE"] or "").strip() == "":
            continue
        try:
            rows.append(Row(datetime.strptime(record["TIME_PERIOD"], "%Y-%m-%d").date(), float(record["OBS_VALUE"])))
        except (TypeError, ValueError):
            raise SourceError(
                f"Zeile {number}: unlesbar: {str(record['TIME_PERIOD'])[:20]!r} {str(record['OBS_VALUE'])[:20]!r}"
            ) from None
    return checked(rows)
