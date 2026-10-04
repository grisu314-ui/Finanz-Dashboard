"""Publication times in operation (M3, step 9): when new values first arrived, against series.toml.

Read-only. For every observation whose first row came from a regular fetch (not from the backfill),
the retrieval time is compared with the configured estimate (fever.release.estimated_release). Scoring
counts an observation from the New York day of that estimate on (E-49): a value that arrived only on a
later New York day points to a lag_days that is too short (look-ahead in the history) or to a gap in the
fetches. The second part looks at Cboe index files fetched during US trading hours: does the CSV already
hold a row for the running day? Prints times only, no values (licensed series, E-69).

Run in the worker container: python -m fever.release_check
Without the module in the image (one-off, from the project directory): python - < fever/release_check.py
"""

import gzip
import sys
from collections import defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from fever.config import series_catalog
from fever.release import estimated_release
from fever.store.db import data_dir, make_engine
from fever.store.tables import observation

NEW_YORK = ZoneInfo("America/New_York")
FREQUENCIES = {"daily": "täglich", "weekly": "wöchentlich", "monthly": "monatlich", "quarterly": "quartalsweise"}
TRADING = (time(9, 30), time(16, 15))  # Cboe index hours; a row of the running day would be a snapshot


def first_live(conn) -> list[tuple[str, date, datetime]]:
    """(series, observation date, retrieval) of observations whose first row was not backfilled."""
    first = (select(observation.c.series_id, observation.c.obs_date, func.min(observation.c.vintage).label("vintage"))
             .group_by(observation.c.series_id, observation.c.obs_date).subquery())
    query = (select(observation.c.series_id, observation.c.obs_date, observation.c.retrieved_at)
             .join(first, (observation.c.series_id == first.c.series_id) & (observation.c.obs_date == first.c.obs_date)
                   & (observation.c.vintage == first.c.vintage))
             .where(observation.c.vintage_estimated.is_(False))
             .order_by(observation.c.series_id, observation.c.obs_date))
    return [(row.series_id, row.obs_date, row.retrieved_at) for row in conn.execute(query)]


def classify(rows, catalog) -> dict[str, dict]:
    """Per series: count, early (before the estimate), on the day, late (a later New York day), largest delay."""
    result = defaultdict(lambda: {"n": 0, "early": [], "day": 0, "late": [], "delay": None})
    for series_id, obs_date, retrieved in rows:
        series = catalog.get(series_id)
        if series is None:
            continue  # no longer in the catalogue
        expected = estimated_release(obs_date, series)
        entry = result[series_id]
        entry["n"] += 1
        if retrieved < expected:
            entry["early"].append((obs_date, expected, retrieved))
        elif retrieved.astimezone(NEW_YORK).date() > expected.astimezone(NEW_YORK).date():
            entry["late"].append((obs_date, expected, retrieved))
        else:
            entry["day"] += 1
            delay = retrieved - expected
            entry["delay"] = delay if entry["delay"] is None else max(entry["delay"], delay)
    return dict(result)


def cboe_snapshots(directory: Path) -> list[tuple[str, datetime, date | None]]:
    """Cboe index files fetched on a New York weekday during trading hours: (group, retrieval, date of last row)."""
    found = []
    for path in sorted((directory / "raw" / "cboe").glob("*/*.gz")):
        retrieved = datetime.strptime(path.name.split("_")[0], "%Y%m%dT%H%M%S%fZ").replace(tzinfo=timezone.utc)
        local = retrieved.astimezone(NEW_YORK)
        if local.weekday() >= 5 or not TRADING[0] <= local.time() <= TRADING[1]:
            continue
        try:
            last = gzip.decompress(path.read_bytes()).decode("utf-8").strip().splitlines()[-1]
            last_day = datetime.strptime(last.split(",")[0], "%m/%d/%Y").date()
        except (OSError, ValueError, IndexError):
            last_day = None  # unreadable: shown as such
        found.append((path.parent.name, retrieved, last_day))
    return found


def report(rows, catalog, snapshots) -> list[str]:
    since = min((retrieved for _, _, retrieved in rows), default=None)
    lines = [f"Veröffentlichung im Betrieb (M3, Schritt 9): {len(rows)} neue Werte"
             + (f" seit {_ny(since)}" if since else "") + "; Zeiten New York",
             f"{'Reihe':<27}{'Takt':<14}{'erwartet':<14}{'n':>4}{'früher':>8}{'am Tag':>8}{'später':>8}  größte Verspätung am Tag"]
    summary = classify(rows, catalog)
    for series_id, series in sorted(catalog.items()):
        entry = summary.get(series_id)
        if entry is None:
            continue  # listed in one line below
        expected = f"+{series.lag_days} T, {series.release_time:%H:%M}"
        delay = _hours(entry["delay"]) if entry["delay"] is not None else "–"
        lines.append(f"{series_id:<27}{FREQUENCIES.get(series.frequency, series.frequency):<14}{expected:<14}"
                     f"{entry['n']:>4}{len(entry['early']):>8}{entry['day']:>8}{len(entry['late']):>8}  {delay}")
    quiet = [series_id for series_id in sorted(catalog) if series_id not in summary]
    lines += ["", f"Ohne neuen Wert im Betrieb: {', '.join(quiet) if quiet else 'keine'}"]
    for key, title in (("late", "Später als erwartet (erster Abruf an einem späteren New Yorker Tag):"),
                       ("early", "Früher als erwartet (vor der erwarteten Zeit abgerufen, etwa per Sofort-Abruf):")):
        cases = [(s, *case) for s, entry in sorted(summary.items()) for case in entry[key]]
        lines.append("")
        lines.append(title if cases else title.split(" (")[0] + ": keine")
        lines += [f"  {s:<22} Beobachtung {obs:%d.%m.%Y}: erwartet {_ny(expected)}, erster Abruf {_ny(retrieved)}"
                  for s, obs, expected, retrieved in cases]
    with_row = [(g, r) for g, r, last in snapshots if last == r.astimezone(NEW_YORK).date()]
    unreadable = sum(1 for *_, last in snapshots if last is None)
    lines += ["", f"Cboe-Indizes während der US-Handelszeit ({TRADING[0]:%H:%M}–{TRADING[1]:%H:%M}): {len(snapshots)} "
                  f"Rohdateien, {len(with_row)} mit einer Zeile des laufenden Tages, {unreadable} nicht lesbar"]
    lines += [f"  {group} {_ny(retrieved)}" for group, retrieved in with_row]
    return lines


def _ny(moment: datetime) -> str:
    return f"{moment.astimezone(NEW_YORK):%a %d.%m.%Y %H:%M}"


def _hours(delta) -> str:
    minutes = int(delta.total_seconds() // 60)
    return f"+{minutes // 60}:{minutes % 60:02d}"


def main() -> int:
    directory = data_dir()
    engine = make_engine(directory, read_only=True)
    with engine.connect() as conn:
        rows = first_live(conn)
    engine.dispose()
    print("\n".join(report(rows, series_catalog(), cboe_snapshots(directory))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
