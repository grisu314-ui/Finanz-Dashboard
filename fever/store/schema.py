"""Migration check (E-70): code and database must be on the same Alembic revision.

Migrations never run at container start (CLAUDE.md). Without this check a skipped
`alembic upgrade head` surfaces as an SQL error in the middle of a scoring run or a page.
The backup module does not use it: the backup before a migration must work on the old schema.
"""

from functools import cache
from pathlib import Path

from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
_VERSION_TABLE = "alembic_version"


class SchemaError(RuntimeError):
    """The database is not on the revision this code expects."""


@cache
def _script() -> ScriptDirectory:
    return ScriptDirectory(str(MIGRATIONS))


def expected_revision() -> str:
    """Newest migration shipped with this code."""
    return _script().get_current_head()


def database_revision(conn: Connection) -> str | None:
    """Revision stored in the database; None before the first migration.

    Read directly instead of through Alembic's MigrationContext, which logs two INFO lines per call.
    """
    if not inspect(conn).has_table(_VERSION_TABLE):
        return None
    return conn.execute(text(f"SELECT version_num FROM {_VERSION_TABLE}")).scalar()


def problem(conn: Connection) -> str | None:
    """German message if the database is not on the expected revision, otherwise None."""
    expected, actual = expected_revision(), database_revision(conn)
    if actual == expected:
        return None
    if actual is not None and actual not in {revision.revision for revision in _script().walk_revisions()}:
        return (f"Datenbank auf Migration {actual}, die dieses Programm nicht kennt (erwartet {expected}): "
                "Image auf den Stand der Datenbank bringen (docs/einrichtung.md, Update)")
    return (f"Migration fehlt: Datenbank auf {actual or 'keiner Migration'}, Programm erwartet {expected}. "
            "Stack stoppen, Backup, alembic upgrade head (docs/einrichtung.md, Update)")


def require_current(conn: Connection) -> None:
    """Raise SchemaError with the message of problem() if the revisions differ."""
    message = problem(conn)
    if message:
        raise SchemaError(message)
