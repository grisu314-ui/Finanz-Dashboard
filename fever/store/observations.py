"""Append-only access to observations.

There is deliberately no update or delete function; the table is additionally
protected by triggers (migration 0001). The locally archived ICE-BofA spreads
cannot be obtained again.
"""

import math
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import func, insert, select
from sqlalchemy.engine import Connection

from fever.store.tables import observation


@dataclass(frozen=True)
class NewObservation:
    obs_date: date
    value: float
    vintage: datetime
    vintage_estimated: bool


@dataclass(frozen=True)
class StoredObservation:
    obs_date: date
    value: float
    vintage: datetime
    vintage_estimated: bool
    retrieved_at: datetime


def append_observations(
    conn: Connection, series_id: str, rows: Iterable[NewObservation], *, retrieved_at: datetime
) -> int:
    """Store new and changed values; an unchanged value adds no row. Returns the rows added."""
    rows = list(rows)
    _check(series_id, rows, retrieved_at)
    latest = {obs.obs_date: obs.value for obs in latest_values(conn, series_id)}
    new = [
        {
            "series_id": series_id,
            "obs_date": row.obs_date,
            "vintage": row.vintage,
            "vintage_estimated": row.vintage_estimated,
            "value": row.value,
            "retrieved_at": retrieved_at,
        }
        for row in rows
        if latest.get(row.obs_date) != row.value
    ]
    if new:
        conn.execute(insert(observation), new)
    return len(new)


def latest_values(conn: Connection, series_id: str) -> list[StoredObservation]:
    """Newest vintage per observation date, sorted by date (phase 1: the latest vintage counts)."""
    result = conn.execute(
        select(observation)
        .where(observation.c.series_id == series_id)
        .order_by(observation.c.obs_date, observation.c.vintage)
    )
    latest: dict[date, StoredObservation] = {}
    for row in result:
        latest[row.obs_date] = StoredObservation(
            row.obs_date, row.value, row.vintage, row.vintage_estimated, row.retrieved_at
        )
    return list(latest.values())


def latest_obs_date(conn: Connection, series_id: str) -> date | None:
    """Most recent observation date stored for the series, None if there is none."""
    return conn.execute(select(func.max(observation.c.obs_date)).where(observation.c.series_id == series_id)).scalar()


def _check(series_id: str, rows: list[NewObservation], retrieved_at: datetime) -> None:
    if not _is_aware(retrieved_at):
        raise ValueError(f"{series_id}: Abrufzeit ohne Zeitzone: {retrieved_at!r}")
    seen: set[date] = set()
    for row in rows:
        if row.obs_date in seen:
            raise ValueError(f"{series_id}: Beobachtungsdatum doppelt im selben Abruf: {row.obs_date}")
        seen.add(row.obs_date)
        if not math.isfinite(row.value):
            raise ValueError(f"{series_id}: ungültiger Wert am {row.obs_date}: {row.value!r}")
        if not _is_aware(row.vintage):
            raise ValueError(f"{series_id}: Stand ohne Zeitzone am {row.obs_date}: {row.vintage!r}")


def _is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None
