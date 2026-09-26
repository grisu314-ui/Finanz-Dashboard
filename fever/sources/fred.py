"""FRED series observations (JSON) through the FRED API.

The API key travels as a query parameter; the HTTP client masks it in every
message. Missing values come as "." (e.g. holidays of the ICE spreads) and are
skipped, never stored. Terms of use: see docs/umsetzungsplan.md, M2.
"""

import json
import os
from datetime import date, datetime

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

URL = "https://api.stlouisfed.org/fred/series/observations"
_MAX_SHOWN = 40  # characters of a broken field quoted in an error message


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    # `since` is not needed: every request returns the full history.
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise SourceError("FRED_API_KEY ist nicht gesetzt")
    return client.get(URL, {"series_id": series.source_id, "api_key": key, "file_type": "json"})


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    try:
        data = json.loads(content)
    except ValueError:
        raise SourceError("keine gültige JSON-Antwort") from None
    if not isinstance(data, dict) or not isinstance(data.get("observations"), list):
        raise SourceError("Antwort ohne Liste 'observations'")
    observations = data["observations"]
    # FRED returns at most `limit` rows (default 100000); fewer rows than `count` means a cut-off history.
    if data.get("count") != len(observations) or data.get("offset", 0) != 0:
        raise SourceError(f"unvollständige Antwort: count {data.get('count')!r}, geliefert {len(observations)}")

    rows = []
    for index, obs in enumerate(observations):
        if not (isinstance(obs, dict) and isinstance(obs.get("date"), str) and isinstance(obs.get("value"), str)):
            raise SourceError(f"Eintrag {index}: 'date' oder 'value' fehlt")
        if obs["value"] == ".":
            continue
        try:
            rows.append(Row(datetime.strptime(obs["date"], "%Y-%m-%d").date(), float(obs["value"])))
        except ValueError:
            raise SourceError(
                f"Eintrag {index}: unlesbar: date={obs['date'][:_MAX_SHOWN]!r} value={obs['value'][:_MAX_SHOWN]!r}"
            ) from None
    return checked(rows)
