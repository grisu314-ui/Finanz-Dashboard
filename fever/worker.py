"""Worker: every 15 minutes fetch the due series, write the heartbeat, make the daily backup.

Schedule (decision E-31), planned in America/New_York:
- A series is due on New York weekdays from its release_time on, once per New York day.
- After a failed fetch it is due again one hour later.
- Daily series: if the observation expected by now is still missing after a successful fetch,
  the series is due again every hour until the New York day ends (late publication, holiday).
- After a restart every series counts as not yet fetched today, so missed fetches are caught up.
Holidays are not errors: the fetch simply brings no new value.

Start: python -m fever.worker. Healthcheck: healthcheck() (decision E-33).
"""

import logging
import signal
import sys
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from fever import log
from fever.backup import BackupError, has_backup, run_backup
from fever.config import ConfigError, Series, series_catalog
from fever.http import HttpClient
from fever.sources.update import estimated_release, update_series
from fever.store.db import DataDirError, data_dir, make_engine
from fever.store.observations import latest_obs_date
from fever.store.status import read_heartbeat, record_error, record_heartbeat

CYCLE = timedelta(minutes=15)
RETRY_AFTER = timedelta(hours=1)
HEARTBEAT_MAX_AGE = timedelta(minutes=45)  # E-33: three missed cycles
COMPONENT = "worker"
NEW_YORK = ZoneInfo("America/New_York")
_LOOKBACK_DAYS = 10  # more than any gap between two weekdays, holidays included

logger = logging.getLogger(__name__)


@dataclass
class SeriesState:
    """What the running worker remembers per series; empty after a restart."""

    last_success_day: date | None = None  # New York date of the last successful fetch
    last_attempt: datetime | None = None  # UTC


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def expected_obs_date(series: Series, now: datetime) -> date | None:
    """Latest weekday observation whose estimated publication lies at or before now."""
    today = now.astimezone(NEW_YORK).date()
    for back in range(_LOOKBACK_DAYS):
        day = today - timedelta(days=back)
        if day.weekday() < 5 and estimated_release(day, series) <= now:
            return day
    return None


def is_due(series: Series, state: SeriesState, now: datetime, latest: date | None) -> bool:
    """Schedule rule E-31; `latest` is the newest stored observation date of the series."""
    local = now.astimezone(NEW_YORK)
    if local.weekday() >= 5 or local.time() < series.release_time:
        return False
    if state.last_success_day != local.date():
        return state.last_attempt is None or now - state.last_attempt >= RETRY_AFTER
    if series.frequency != "daily":
        return False
    expected = expected_obs_date(series, now)
    missing = expected is not None and (latest is None or latest < expected)
    return missing and now - state.last_attempt >= RETRY_AFTER


def run_cycle(
    engine: Engine,
    directory: Path,
    client: HttpClient,
    catalog: dict[str, Series],
    states: dict[str, SeriesState],
    stop: threading.Event,
    *,
    clock=_utcnow,
) -> None:
    _heartbeat(engine, clock())
    _daily_backup(directory, clock())
    for series in catalog.values():
        if stop.is_set():
            return
        now = clock()
        with engine.connect() as conn:
            latest = latest_obs_date(conn, series.id)
        state = states[series.id]
        if not is_due(series, state, now, latest):
            continue
        # Also before every fetch: a cycle with many slow retries must not look like a dead worker.
        _heartbeat(engine, now)
        state.last_attempt = now
        try:
            result = update_series(engine, directory, client, series, clock=clock)
        except Exception as exc:  # one broken series must not stop the others (ICE archive)
            logger.exception("Unerwarteter Fehler bei %s", series.id)
            with engine.begin() as conn:
                message = log.mask(f"{series.id}: interner Fehler: {type(exc).__name__}: {exc}")
                record_error(conn, series.source, clock(), message)
            continue
        if result.fetched:
            state.last_success_day = now.astimezone(NEW_YORK).date()


def serve(
    engine: Engine,
    directory: Path,
    client: HttpClient,
    catalog: dict[str, Series],
    stop: threading.Event,
    *,
    clock=_utcnow,
    cycle: timedelta = CYCLE,
) -> None:
    """Run cycles until `stop` is set; a cycle starts every `cycle` after the previous start."""
    states = {series_id: SeriesState() for series_id in catalog}
    while not stop.is_set():
        started = time.monotonic()
        run_cycle(engine, directory, client, catalog, states, stop, clock=clock)
        stop.wait(max(0.0, cycle.total_seconds() - (time.monotonic() - started)))


def healthcheck(now: datetime | None = None) -> int:
    """Exit code for the container healthcheck: 0 if the heartbeat is at most 45 minutes old."""
    now = now or _utcnow()
    try:
        engine = make_engine(data_dir(), read_only=True)
        try:
            with engine.connect() as conn:
                beat = read_heartbeat(conn, COMPONENT)
        finally:
            engine.dispose()
    except (DataDirError, SQLAlchemyError) as exc:
        print(f"ungesund: {exc}")
        return 1
    if beat is None:
        print("ungesund: noch kein Heartbeat")
        return 1
    age = now - beat
    if age > HEARTBEAT_MAX_AGE:
        print(f"ungesund: letzter Heartbeat vor {int(age.total_seconds() // 60)} Minuten")
        return 1
    print(f"gesund: letzter Heartbeat vor {int(age.total_seconds() // 60)} Minuten")
    return 0


def _heartbeat(engine: Engine, now: datetime) -> None:
    with engine.begin() as conn:
        record_heartbeat(conn, COMPONENT, now)


def _daily_backup(directory: Path, now: datetime) -> None:
    if has_backup(directory, "daily", now.astimezone(timezone.utc).date()):
        return
    try:
        path = run_backup(directory, "daily", now)
    except (BackupError, OSError, SQLAlchemyError) as exc:
        logger.error("Tägliches Backup fehlgeschlagen, nächster Versuch im nächsten Takt: %s", exc)
        return
    logger.info("Tägliches Backup erstellt und geprüft: %s", path.name)


def install_stop_handlers(stop: threading.Event) -> None:
    """SIGTERM (docker compose stop) and SIGINT end the worker after the current series."""
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda _signum, _frame: stop.set())


def main() -> int:
    log.setup()
    stop = threading.Event()
    install_stop_handlers(stop)
    try:
        directory = data_dir()
        engine = make_engine(directory)
        catalog = series_catalog()
    except (DataDirError, ConfigError) as exc:
        logger.error("Worker nicht gestartet: %s", exc)
        return 2
    logger.info("Worker gestartet: %d Reihen, Takt %d Minuten", len(catalog), CYCLE.total_seconds() // 60)
    serve(engine, directory, HttpClient(), catalog, stop)
    engine.dispose()
    logger.info("Worker beendet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
