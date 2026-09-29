"""Read-only database access for the interface: every connection sets PRAGMA query_only.

The long reads (histories, freshness) are kept per data version (E-78): until the worker stores a
new observation or a new scoring run, a page view reads them from memory instead of the database.
"""

import calendar
import threading
from datetime import date, datetime
from functools import cache, wraps

from sqlalchemy import func, select, text
from sqlalchemy.engine import Engine

from fever.store import schema
from fever.store.db import data_dir, make_engine
from fever.store.observations import latest_pairs
from fever.store.status import read_heartbeat, read_status
from fever.store.tables import composite_score, indicator_score, observation
from fever.store.validation import StoredReport, read_report


@cache
def engine() -> Engine:
    """One read-only engine per process; the database must exist (DataDirError otherwise)."""
    return make_engine(data_dir(), read_only=True)


# observation is append-only (triggers), so its largest rowid grows with every stored value; every
# scoring run replaces the score tables with a new computed_at.
_VERSION = text("SELECT (SELECT max(rowid) FROM observation), (SELECT computed_at FROM composite_score LIMIT 1)")
_kept: dict = {}
_kept_version: tuple | None = None
_lock = threading.Lock()


def data_version() -> tuple:
    """Database file, newest observation and scoring run: changes whenever a kept read could change."""
    database = engine()
    with database.connect() as conn:
        return (database.url.database, *conn.execute(_VERSION).one())


def per_data_version(read):
    """Keep the result of `read` until the data version changes (E-78); callers must not change it."""
    @wraps(read)
    def wrapper(*args):
        global _kept_version
        version, key = data_version(), (read.__name__, args)
        with _lock:
            if version != _kept_version:
                _kept.clear()
                _kept_version = version
            if key in _kept:
                return _kept[key]
        value = read(*args)
        with _lock:
            if version == _kept_version:
                _kept[key] = value
        return value
    return wrapper


def validation_report() -> StoredReport | None:
    """The stored validation report (M10, E-93). Read every time, not kept: the validation run follows the
    scoring run a few seconds later without changing the data version (E-78)."""
    with engine().connect() as conn:
        return read_report(conn)


def latest_composite() -> dict | None:
    with engine().connect() as conn:
        row = conn.execute(select(composite_score).order_by(composite_score.c.score_date.desc()).limit(1)).first()
    return None if row is None else dict(row._mapping)


@per_data_version
def composite_history(*columns: str) -> list[dict]:
    wanted = [composite_score.c.score_date] + [composite_score.c[name] for name in columns]
    with engine().connect() as conn:
        return [dict(row._mapping) for row in conn.execute(select(*wanted).order_by(composite_score.c.score_date))]


def indicator_scores_on(day: date) -> dict[str, dict]:
    with engine().connect() as conn:
        rows = conn.execute(select(indicator_score).where(indicator_score.c.score_date == day))
        return {row.indicator_id: dict(row._mapping) for row in rows}


@per_data_version
def indicator_history(indicator_id: str, *columns: str) -> list[dict]:
    """score_date and the given columns of an indicator, oldest first (only what the chart needs)."""
    wanted = [indicator_score.c.score_date] + [indicator_score.c[name] for name in columns]
    query = select(*wanted).where(indicator_score.c.indicator_id == indicator_id).order_by(indicator_score.c.score_date)
    with engine().connect() as conn:
        return [row._asdict() for row in conn.execute(query)]


@per_data_version
def indicator_values_since(start: date) -> dict[str, list[dict]]:
    """score_date, status and value per indicator after `start`, oldest first (sparklines, view 7)."""
    query = (select(indicator_score.c.indicator_id, indicator_score.c.score_date, indicator_score.c.status,
                    indicator_score.c.value)
             .where(indicator_score.c.score_date > start).order_by(indicator_score.c.score_date))
    histories: dict[str, list[dict]] = {}
    with engine().connect() as conn:
        for row in conn.execute(query):
            histories.setdefault(row.indicator_id, []).append(
                {"score_date": row.score_date, "status": row.status, "value": row.value})
    return histories


@per_data_version
def score_days() -> list[date]:
    """Every day with a stored indicator score, oldest first."""
    query = select(indicator_score.c.score_date).distinct().order_by(indicator_score.c.score_date)
    with engine().connect() as conn:
        return list(conn.execute(query).scalars())


@per_data_version
def valid_percentiles(days: tuple[date, ...]) -> dict[tuple[str, date], float]:
    """Percentile per (indicator_id, score_date) on the given days, only where the score is valid (heatmap)."""
    query = (select(indicator_score.c.indicator_id, indicator_score.c.score_date, indicator_score.c.percentile)
             .where(indicator_score.c.score_date.in_(days), indicator_score.c.status == "ok"))
    with engine().connect() as conn:
        return {(row.indicator_id, row.score_date): row.percentile for row in conn.execute(query)}


def first_observation(series_ids: list[str]) -> date | None:
    with engine().connect() as conn:
        return conn.execute(select(func.min(observation.c.obs_date)).where(observation.c.series_id.in_(series_ids))).scalar()


def history_start(series_ids: list[str]) -> date | None:
    """First day on which every input series has an observation: an indicator needs all of them."""
    query = (select(observation.c.series_id, func.min(observation.c.obs_date))
             .where(observation.c.series_id.in_(series_ids)).group_by(observation.c.series_id))
    with engine().connect() as conn:
        firsts = dict(conn.execute(query).all())
    return max(firsts.values()) if firsts and set(firsts) == set(series_ids) else None


@per_data_version
def series_freshness() -> dict[str, dict]:
    """Per series: newest observation date, newest retrieval and number of rows."""
    query = select(
        observation.c.series_id,
        func.max(observation.c.obs_date).label("obs_date"),
        func.max(observation.c.retrieved_at).label("retrieved_at"),
        func.count().label("rows"),
    ).group_by(observation.c.series_id)
    with engine().connect() as conn:
        return {row.series_id: dict(row._mapping) for row in conn.execute(query)}


def newest_retrieval(series_ids: list[str]) -> datetime | None:
    """Most recent fetch that stored an observation of one of the series."""
    query = select(func.max(observation.c.retrieved_at)).where(observation.c.series_id.in_(series_ids))
    with engine().connect() as conn:
        return conn.execute(query).scalar()


@per_data_version
def series_history(series_id: str) -> list[tuple[date, float]]:
    """Observations of a raw series, newest vintage per date (phase-1 rule), oldest first."""
    with engine().connect() as conn:
        return latest_pairs(conn, series_id)


def newest_observation(series_id: str) -> tuple[date, float] | None:
    """Newest observation date of a raw series with the value of its newest vintage."""
    query = (select(observation.c.obs_date, observation.c.value).where(observation.c.series_id == series_id)
             .order_by(observation.c.obs_date.desc(), observation.c.vintage.desc()).limit(1))
    with engine().connect() as conn:
        row = conn.execute(query).first()
    return None if row is None else (row.obs_date, row.value)


def value_on(series_id: str, day: date) -> float | None:
    """Value of a raw series on one observation date, newest vintage; None without observation."""
    query = (select(observation.c.value).where(observation.c.series_id == series_id, observation.c.obs_date == day)
             .order_by(observation.c.vintage.desc()).limit(1))
    with engine().connect() as conn:
        return conn.execute(query).scalar()


RECESSION_SERIES = "usrec"


@per_data_version
def recessions() -> tuple[tuple[date, date], ...]:
    """US recessions (E-56) as (first day of the first month, last day of the last month).

    Consecutive months with USREC = 1 form one period (trough method, as on FRED graphs).
    """
    with engine().connect() as conn:
        rows = latest_pairs(conn, RECESSION_SERIES)
    periods, start, previous = [], None, None
    for obs_date, value in rows:
        if value == 1 and start is None:
            start = obs_date
        elif value != 1 and start is not None:
            periods.append((start, _month_end(previous)))
            start = None
        previous = obs_date
    if start is not None:
        periods.append((start, _month_end(previous)))
    return tuple(periods)


def _month_end(day: date) -> date:
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def sources() -> list[dict]:
    with engine().connect() as conn:
        return read_status(conn)


def heartbeat() -> datetime | None:
    with engine().connect() as conn:
        return read_heartbeat(conn, "worker")


def schema_problem() -> str | None:
    """Message if the database is not on the migration this code expects (E-70)."""
    with engine().connect() as conn:
        return schema.problem(conn)
