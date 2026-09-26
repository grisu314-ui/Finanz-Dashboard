"""Cboe Futures Exchange: VX futures term structure as rank series (decisions E-45, E-46).

Stored per trading day t for rank n = 1..8: the settlement price of the n-th monthly VX
contract that is listed on t (first row in its file on or before t) and expires after t,
and its calendar days to expiry. A contract no longer counts on its expiry day, whose
settlement is the final settlement value (a VIX value of that morning). A listed contract
without a row on t leaves its rank empty; later contracts do not move up.

source_id: "VX<n>" (settlement) or "VX<n>_DAYS" (days to expiry); all 16 series come from one
download (group "cfe_vx", E-36). fetch() reads the contract list and the files of the monthly
contracts (weeklies and mini VX are left out) and bundles them as JSON for the raw archive.
With `since` (newest stored trading day of the group) only contracts expiring after
since - WINDOW are loaded, about ten files; the first fetch loads all (from 2013, about 180).
Settlement 0 means no settlement (files up to 17.05.2013) and counts as missing.
Licence as for the Cboe indices (E-26): private use only, no redistribution; test data synthetic.
"""

import csv
import io
import json
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fever.config import Series
from fever.http import Fetched, HttpClient
from fever.sources import Row, SourceError, checked

LIST_URL = "https://www.cboe.com/us/futures/market_statistics/historical_data/product/list/VX/"
FILE_URL = "https://cdn.cboe.com/{path}"
MAX_RANK = 8
WINDOW = timedelta(days=45)  # more than one monthly expiry cycle
NEW_YORK = ZoneInfo("America/New_York")
HEADER = ["Trade Date", "Futures", "Open", "High", "Low", "Close", "Settle", "Change", "Total Volume", "EFP", "Open Interest"]
_PATH = re.compile(r"data/us/futures/market_statistics/historical_data/VX/VX_(\d{4}-\d{2}-\d{2})\.csv")
_SOURCE_ID = re.compile(r"VX([1-9])(_DAYS)?")
_LABEL = re.compile(r"[A-Z] \((\w{3}) (\d{4})\)")
_SHOWN = 80  # characters of a broken line quoted in an error message


def fetch(client: HttpClient, series: Series, since: date | None = None) -> Fetched:
    listing = client.get(LIST_URL)
    contracts = _monthly_contracts(listing.content, listing.retrieved_at.astimezone(NEW_YORK).date())
    cutoff = None if since is None else since - WINDOW
    files, last = {}, listing
    for expiry, path in sorted(contracts.items()):
        if cutoff is not None and expiry < cutoff:
            continue
        last = client.get(FILE_URL.format(path=path))
        try:
            files[expiry.isoformat()] = last.content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise SourceError(f"VX_{expiry}.csv: keine lesbare Textdatei") from None
    bundle = {"from_date": None if cutoff is None else cutoff.isoformat(), "contracts": files}
    return Fetched(json.dumps(bundle, sort_keys=True).encode(), last.retrieved_at, 200)


def parse(content: bytes, series: Series, retrieved_at: datetime) -> list[Row]:
    rank, days = _rank_of(series)
    rows = []
    for obs_date, ranks in _term_structure(content, series, retrieved_at).items():
        settle, days_left = ranks.get(rank, (None, None))
        if settle is not None:
            rows.append(Row(obs_date, float(days_left) if days else settle))
    return checked(rows)


def _rank_of(series: Series) -> tuple[int, bool]:
    match = _SOURCE_ID.fullmatch(series.source_id)
    if not match or int(match.group(1)) > MAX_RANK:
        raise SourceError(f"ungültige Kennung {series.source_id!r} (erwartet VX1 bis VX{MAX_RANK}, optional _DAYS)")
    return int(match.group(1)), match.group(2) is not None


def _monthly_contracts(content: bytes, today: date) -> dict[date, str]:
    """Expiry -> file path of every monthly VX contract in the contract list."""
    try:
        years = json.loads(content)
    except ValueError:
        raise SourceError("Kontraktliste ist kein gültiges JSON") from None
    if not isinstance(years, dict) or not all(isinstance(entries, list) for entries in years.values()):
        raise SourceError("Kontraktliste hat nicht die Form {Jahr: [Kontrakte]}")
    contracts: dict[date, str] = {}
    for entries in years.values():
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("futures_root") != "VX" or entry.get("duration_type") != "M":
                continue
            match = _PATH.fullmatch(str(entry.get("path")))
            if not match or match.group(1) != entry.get("expire_date"):
                raise SourceError(f"Kontraktliste: unerwarteter Eintrag {str(entry)[:_SHOWN]}")
            contracts[date.fromisoformat(match.group(1))] = entry["path"]  # the path names the expiry
    running = sum(1 for expiry in contracts if expiry > today)
    if running < MAX_RANK:
        raise SourceError(f"Kontraktliste: nur {running} laufende Monatskontrakte (erwartet mindestens {MAX_RANK})")
    return contracts


def _term_structure(content: bytes, series: Series, retrieved_at: datetime) -> dict[date, dict[int, tuple]]:
    """Trading day -> {rank: (settlement or None, days to expiry)} for the days the bundle covers completely."""
    try:
        bundle = json.loads(content)
        from_date = None if bundle["from_date"] is None else date.fromisoformat(bundle["from_date"])
        files = {date.fromisoformat(expiry): text for expiry, text in bundle["contracts"].items()}
    except (ValueError, KeyError, TypeError, AttributeError):
        raise SourceError("Abrufbündel unlesbar") from None
    settles = {expiry: _contract(text, expiry) for expiry, text in files.items()}
    listed_from = {expiry: min(days) for expiry, days in settles.items() if days}
    days = sorted({day for per_day in settles.values() for day in per_day})
    if from_date is not None:
        days = [day for day in days if day >= from_date]  # earlier days lack contracts expiring before from_date
    now = retrieved_at.astimezone(NEW_YORK)
    if now.time() < series.release_time:
        days = [day for day in days if day < now.date()]  # the running day is not settled yet
    table = {}
    for day in days:
        running = sorted(expiry for expiry, first in listed_from.items() if first <= day < expiry)
        table[day] = {
            rank: (settles[expiry].get(day), (expiry - day).days)
            for rank, expiry in enumerate(running[:MAX_RANK], start=1)
        }
    return table


def _contract(text: str, expiry: date) -> dict[date, float | None]:
    """Trading day -> settlement (None for 0) of one contract file."""
    lines = csv.reader(io.StringIO(text))
    header = next(lines, None)
    if header != HEADER:
        raise SourceError(f"VX_{expiry}.csv: unerwartete Kopfzeile: {str(header)[:_SHOWN]}")
    month = expiry.strftime("%b %Y")
    settles: dict[date, float | None] = {}
    for number, fields in enumerate(lines, start=2):
        if not fields:
            continue
        where = f"VX_{expiry}.csv, Zeile {number}"
        if len(fields) != len(HEADER):
            raise SourceError(f"{where}: {len(fields)} statt {len(HEADER)} Felder")
        label = _LABEL.fullmatch(fields[1])
        if not label or f"{label.group(1)} {label.group(2)}" != month:
            raise SourceError(f"{where}: Kontrakt {fields[1]!r} passt nicht zum Verfall {expiry}")
        try:
            day, settle = date.fromisoformat(fields[0]), float(fields[6])
        except ValueError:
            raise SourceError(f"{where}: unlesbar: {','.join(fields)[:_SHOWN]}") from None
        if day > expiry or day in settles:
            raise SourceError(f"{where}: Handelstag {day} nach dem Verfall oder doppelt")
        settles[day] = settle if settle != 0 else None
    return settles
