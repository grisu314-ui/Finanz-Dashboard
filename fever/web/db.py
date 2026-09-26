"""Read-only database access for the interface: every connection sets PRAGMA query_only."""

from datetime import date, datetime
from functools import cache

from sqlalchemy import func, select
from sqlalchemy.engine import Engine

from fever.store.db import data_dir, make_engine
from fever.store.status import read_heartbeat, read_status
from fever.store.tables import composite_score, indicator_score, observation


@cache
def engine() -> Engine:
    """One read-only engine per process; the database must exist (DataDirError otherwise)."""
    return make_engine(data_dir(), read_only=True)


def latest_composite() -> dict | None:
    with engine().connect() as conn:
        row = conn.execute(select(composite_score).order_by(composite_score.c.score_date.desc()).limit(1)).first()
    return None if row is None else dict(row._mapping)


def composite_history(*columns: str) -> list[dict]:
    wanted = [composite_score.c.score_date] + [composite_score.c[name] for name in columns]
    with engine().connect() as conn:
        return [dict(row._mapping) for row in conn.execute(select(*wanted).order_by(composite_score.c.score_date))]


def indicator_scores_on(day: date) -> dict[str, dict]:
    with engine().connect() as conn:
        rows = conn.execute(select(indicator_score).where(indicator_score.c.score_date == day))
        return {row.indicator_id: dict(row._mapping) for row in rows}


def indicator_history(indicator_id: str) -> list[dict]:
    with engine().connect() as conn:
        rows = conn.execute(
            select(indicator_score).where(indicator_score.c.indicator_id == indicator_id).order_by(indicator_score.c.score_date)
        )
        return [dict(row._mapping) for row in rows]


def first_observation(series_ids: list[str]) -> date | None:
    with engine().connect() as conn:
        return conn.execute(select(func.min(observation.c.obs_date)).where(observation.c.series_id.in_(series_ids))).scalar()


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


def sources() -> list[dict]:
    with engine().connect() as conn:
        return read_status(conn)


def heartbeat() -> datetime | None:
    with engine().connect() as conn:
        return read_heartbeat(conn, "worker")
