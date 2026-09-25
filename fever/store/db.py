"""Database location and connections.

Every connection gets the same PRAGMAs; read-only connections (web) additionally
set query_only. Neither ever creates a database: that is the job of the first
Alembic migration.
"""

import os
from pathlib import Path

from sqlalchemy import URL, create_engine, event
from sqlalchemy.engine import Engine

DB_FILE = "fever.sqlite3"
BUSY_TIMEOUT_MS = 5000


class DataDirError(RuntimeError):
    """Data directory or database not configured or missing."""


def data_dir() -> Path:
    """Data directory from FEVER_DATA.

    There is no default on purpose, so development never reaches the production
    database by accident (container: /data, local development: data-dev).
    """
    value = os.environ.get("FEVER_DATA")
    if not value:
        raise DataDirError("FEVER_DATA ist nicht gesetzt (Container: /data, lokal: data-dev)")
    path = Path(value)
    if not path.is_dir():
        raise DataDirError(f"Datenordner fehlt: {path}")
    return path


def db_path(directory: Path) -> Path:
    return directory / DB_FILE


def make_engine(directory: Path, *, read_only: bool = False, must_exist: bool = True) -> Engine:
    """Engine for the database in `directory`.

    must_exist=False is reserved for the migration environment, which creates
    the database file on the first `alembic upgrade head`.
    """
    path = db_path(directory)
    if (must_exist or read_only) and not path.is_file():
        raise DataDirError(
            f"Datenbank fehlt: {path} (Ersteinrichtung: alembic upgrade head, siehe docs/einrichtung.md)"
        )
    # URL.create keeps the path verbatim; in a URL string "?" or "#" would cut it short.
    engine = create_engine(URL.create("sqlite", database=str(path)))

    @event.listens_for(engine, "connect")
    def _set_pragmas(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        if read_only:
            cursor.execute("PRAGMA query_only = ON")
        cursor.close()

    return engine
