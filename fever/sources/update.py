"""Fetch raw series, check them and store new or changed values.

Order per download group (E-36): attempt -> fetch once -> raw archive -> per series:
parse -> checks -> vintage -> append -> status. Decisions (docs/umsetzungsplan.md):
E-14 vintage, E-15 a value outside the bounds is dropped while the rest is stored,
E-24 start date, E-25 lead_days.

`python -m fever.sources.update` fetches every series once, independent of the
worker's schedule (one-off fetch, docs/einrichtung.md).
"""

import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.engine import Engine

from fever import log
from fever.config import ConfigError, Series, group_members, series_catalog
from fever.http import FetchError, Fetched, HttpClient
from fever.sources import Row, SourceError, cboe, cftc, ecb, fed, fred, ofr
from fever.store.db import DataDirError, data_dir, make_engine
from fever.store.observations import NewObservation, append_observations, latest_values
from fever.store.raw import archive_raw
from fever.store.status import record_attempt, record_error, record_success

NEW_YORK = ZoneInfo("America/New_York")
MODULES = {"cboe": cboe, "fred": fred, "ecb": ecb, "ofr": ofr, "fed": fed, "cftc": cftc}
MAX_LISTED_PROBLEMS = 5

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateResult:
    added: int  # rows stored
    rejected: int  # values dropped by the checks
    error: str | None  # message written to source_status; None if everything was fine
    fetched: bool = True  # False if the fetch or the format check failed and nothing was read


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def update_series(
    engine: Engine,
    data_dir: Path,
    client: HttpClient,
    series: Series,
    *,
    clock: Callable[[], datetime] = _utcnow,
) -> UpdateResult:
    """Fetch, check and store one series (a group of one)."""
    return update_group(engine, data_dir, client, [series], clock=clock)[0]


def update_group(
    engine: Engine,
    data_dir: Path,
    client: HttpClient,
    members: list[Series],
    *,
    clock: Callable[[], datetime] = _utcnow,
) -> list[UpdateResult]:
    """Fetch the group's download once and store every member. Problems are logged and recorded, not raised."""
    first = members[0]
    module = MODULES[first.source]
    with engine.begin() as conn:
        record_attempt(conn, first.source, clock())
    try:
        fetched = module.fetch(client, first)
        # Archived before parsing, so a changed format can be inspected afterwards.
        archive_raw(data_dir, first.source, first.group, fetched.content, fetched.retrieved_at)
    except (FetchError, SourceError) as exc:
        message = f"{first.group}: {exc}"
        logger.error("Nichts gespeichert: %s", message)
        with engine.begin() as conn:
            record_error(conn, first.source, clock(), message)
        return [UpdateResult(0, 0, message, fetched=False) for _ in members]

    results = [_store(engine, module, series, fetched) for series in members]
    messages = [result.error for result in results if result.error]
    with engine.begin() as conn:
        now = clock()
        # Success means at least one readable series; dropped values are reported next to it (E-15).
        if any(result.fetched for result in results):
            record_success(conn, first.source, now)
        if messages:
            record_error(conn, first.source, now, " | ".join(messages))
    return results


def _store(engine: Engine, module, series: Series, fetched: Fetched) -> UpdateResult:
    try:
        rows = module.parse(fetched.content, series, fetched.retrieved_at)
    except SourceError as exc:
        message = f"{series.id}: {exc}"
        logger.error("Nichts gespeichert: %s", message)
        return UpdateResult(0, 0, message, fetched=False)
    valid, problems = check(rows, series, fetched.retrieved_at)
    message = None
    if problems:
        listed = "; ".join(problems[:MAX_LISTED_PROBLEMS])
        more = f" (und {len(problems) - MAX_LISTED_PROBLEMS} weitere)" if len(problems) > MAX_LISTED_PROBLEMS else ""
        message = f"{series.id}: {len(problems)} Wert(e) verworfen: {listed}{more}"
        logger.error("%s", message)
    with engine.begin() as conn:
        backfill = not latest_values(conn, series.id)
        new = [_observation(row, series, fetched.retrieved_at, backfill) for row in valid]
        added = append_observations(conn, series.id, new, retrieved_at=fetched.retrieved_at)
    logger.info("%s: %d neue Zeilen%s", series.id, added, " (Erstabruf)" if backfill else "")
    return UpdateResult(added, len(problems), message)


def check(rows: list[Row], series: Series, retrieved_at: datetime) -> tuple[list[Row], list[str]]:
    """Split rows into storable ones and problems. Rows before `start` are skipped silently (E-24)."""
    last_allowed = retrieved_at.astimezone(NEW_YORK).date() + timedelta(days=series.lead_days)
    valid, problems = [], []
    for row in rows:
        if series.start and row.obs_date < series.start:
            continue
        if row.obs_date > last_allowed:
            problems.append(f"{row.obs_date:%d.%m.%Y}: Datum liegt in der Zukunft")
        elif not series.lower <= row.value <= series.upper:
            problems.append(
                f"{row.obs_date:%d.%m.%Y}: Wert {_number(row.value)} außerhalb der Grenzen "
                f"[{_number(series.lower)}; {_number(series.upper)}]"
            )
        else:
            valid.append(row)
    return valid, problems


def estimated_release(obs_date: date, series: Series) -> datetime:
    """Observation date + lag_days, Saturday/Sunday moved to Monday, at release_time New York, in UTC.

    US holidays are not taken into account (E-14).
    """
    day = obs_date + timedelta(days=series.lag_days)
    if day.weekday() >= 5:
        day += timedelta(days=7 - day.weekday())
    return datetime.combine(day, series.release_time, tzinfo=NEW_YORK).astimezone(timezone.utc)


def _observation(row: Row, series: Series, retrieved_at: datetime, backfill: bool) -> NewObservation:
    # E-14: only the first fetch of a series estimates publication times; afterwards the
    # retrieval time is the (conservative) moment from which a new or revised value was known.
    if backfill:
        return NewObservation(row.obs_date, row.value, min(estimated_release(row.obs_date, series), retrieved_at), True)
    return NewObservation(row.obs_date, row.value, retrieved_at, False)


def _number(value: float) -> str:
    return f"{value:.12g}".replace(".", ",")


def main() -> int:
    """One-off fetch of every series; exit code 1 if any series reported a problem."""
    log.setup()
    try:
        directory = data_dir()
        engine = make_engine(directory)
        catalog = series_catalog()
    except (DataDirError, ConfigError) as exc:
        logger.error("Abruf nicht gestartet: %s", exc)
        return 2
    client = HttpClient()
    problems = 0
    for members in group_members(catalog).values():
        problems += sum(1 for result in update_group(engine, directory, client, members) if result.error)
    engine.dispose()
    logger.info("Sofort-Abruf beendet: %d Reihen, %d mit Problemen", len(catalog), problems)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
