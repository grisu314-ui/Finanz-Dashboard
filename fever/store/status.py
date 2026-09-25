"""Fetch status per source for the data status view (decision E-9).

Only the last attempt, success and error are kept; there is no error history.
Messages must not contain secrets; the HTTP client masks them before they get here.
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from fever.store.tables import source_status

MAX_MESSAGE_LENGTH = 2000


def record_attempt(conn: Connection, source: str, at: datetime) -> None:
    _upsert(conn, source, last_attempt_at=at)


def record_success(conn: Connection, source: str, at: datetime) -> None:
    _upsert(conn, source, last_success_at=at)


def record_error(conn: Connection, source: str, at: datetime, message: str) -> None:
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[: MAX_MESSAGE_LENGTH - 1] + "…"
    _upsert(conn, source, last_error_at=at, last_error_message=message)


def read_status(conn: Connection) -> list[dict]:
    rows = conn.execute(select(source_status).order_by(source_status.c.source))
    return [dict(row._mapping) for row in rows]


def _upsert(conn: Connection, source: str, **values) -> None:
    stmt = insert(source_status).values(source=source, **values)
    conn.execute(stmt.on_conflict_do_update(index_elements=[source_status.c.source], set_=values))
