"""CFTC Commitments of Traders, legacy report (futures only), via the Socrata API.

source_id is "<contract market code>/<field>", e.g. "1170E1/noncomm_positions_long_all"
(VIX futures). One request per market returns all FIELDS (group, E-36); the field names
are the CFTC's own, including the typo in "noncomm_postions_spread_all". Positions are
as of Tuesday, released Friday 3:30 p.m. ET, on federal holiday weeks later. Public
domain; the CFTC asks for acknowledgement (checked 26.09.2026).
"""

import json
import re
from datetime import date, datetime

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
DATE_FIELD = "report_date_as_yyyy_mm_dd"
FIELDS = (
    "open_interest_all",
    "noncomm_positions_long_all",
    "noncomm_positions_short_all",
    "noncomm_postions_spread_all",
)
LIMIT = 50000  # rows per request; a full answer must stay below it
_MARKET = re.compile(r"[0-9A-Z]{4,8}")


def _split(series: Series) -> tuple[str, str]:
    market, _, field = series.source_id.partition("/")
    if not _MARKET.fullmatch(market) or field not in FIELDS:
        raise SourceError(f"ungültige Kennung {series.source_id!r} (erwartet <Marktcode>/<Feld aus {', '.join(FIELDS)}>)")
    return market, field


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    # `since` is not needed: every request returns the full history.
    market, _ = _split(series)
    return client.get(URL, {
        "$select": ",".join((DATE_FIELD, *FIELDS)),
        "$where": f"cftc_contract_market_code='{market}'",
        "$order": DATE_FIELD,
        "$limit": str(LIMIT),
    })


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    _, field = _split(series)
    try:
        records = json.loads(content)
    except ValueError:
        raise SourceError("keine gültige JSON-Antwort") from None
    if not isinstance(records, list):
        raise SourceError("Antwort ist keine Liste von Berichten")
    if len(records) >= LIMIT:
        raise SourceError(f"Antwort womöglich abgeschnitten ({len(records)} Zeilen, Grenze {LIMIT})")
    rows = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get(DATE_FIELD), str):
            raise SourceError(f"Eintrag {index}: Stichtag fehlt")
        if field not in record:  # Socrata leaves out empty fields
            continue
        try:
            obs_date = datetime.strptime(record[DATE_FIELD], "%Y-%m-%dT%H:%M:%S.%f").date()
            rows.append(Row(obs_date, float(int(record[field]))))
        except (TypeError, ValueError):
            raise SourceError(f"Eintrag {index}: unlesbar: {str(record.get(DATE_FIELD))[:30]!r} {str(record.get(field))[:20]!r}") from None
    return checked(rows)
