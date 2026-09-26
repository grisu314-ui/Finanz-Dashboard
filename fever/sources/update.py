"""Fetch one raw series, check it and store new or changed values.

Order: attempt -> fetch -> raw archive -> parse -> checks -> vintage -> append -> status.
Decisions (docs/umsetzungsplan.md): E-14 vintage, E-15 a value outside the bounds
is dropped while the rest is stored, E-24 start date, E-25 lead_days.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.engine import Engine

from fever.config import Series
from fever.http import FetchError, HttpClient
from fever.sources import Row, SourceError, cboe, fred
from fever.store.observations import NewObservation, append_observations, latest_values
from fever.store.raw import archive_raw
from fever.store.status import record_attempt, record_error, record_success

NEW_YORK = ZoneInfo("America/New_York")
MODULES = {"cboe": cboe, "fred": fred}
MAX_LISTED_PROBLEMS = 5

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class UpdateResult:
    added: int  # rows stored
    rejected: int  # values dropped by the checks
    error: str | None  # message written to source_status; None if everything was fine


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
    """Fetch, check and store one series. Source problems are logged and recorded, not raised."""
    module = MODULES[series.source]
    with engine.begin() as conn:
        record_attempt(conn, series.source, clock())
    try:
        fetched = module.fetch(client, series)
        # Archived before parsing, so a changed format can be inspected afterwards.
        archive_raw(data_dir, series.source, series.id, fetched.content, fetched.retrieved_at)
        rows = module.parse(fetched.content, series, fetched.retrieved_at)
    except (FetchError, SourceError) as exc:
        message = f"{series.id}: {exc}"
        logger.error("Nichts gespeichert: %s", message)
        with engine.begin() as conn:
            record_error(conn, series.source, clock(), message)
        return UpdateResult(0, 0, message)

    valid, problems = check(rows, series, fetched.retrieved_at)
    message = None
    if problems:
        listed = "; ".join(problems[:MAX_LISTED_PROBLEMS])
        more = f" (und {len(problems) - MAX_LISTED_PROBLEMS} weitere)" if len(problems) > MAX_LISTED_PROBLEMS else ""
        message = f"{series.id}: {len(problems)} Wert(e) verworfen: {listed}{more}"
    with engine.begin() as conn:
        backfill = not latest_values(conn, series.id)
        new = [_observation(row, series, fetched.retrieved_at, backfill) for row in valid]
        added = append_observations(conn, series.id, new, retrieved_at=fetched.retrieved_at)
        now = clock()
        # Success means a readable response; dropped values are reported next to it (E-15).
        record_success(conn, series.source, now)
        if message:
            record_error(conn, series.source, now, message)
    if message:
        logger.error("%s", message)
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
