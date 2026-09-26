from datetime import date, datetime, timezone

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from fever.store.db import make_engine
from fever.store.observations import NewObservation, append_observations
from fever.store.tables import metadata

UTC = timezone.utc


def test_schema_matches_table_definitions(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.connect() as conn:
        assert compare_metadata(MigrationContext.configure(conn), metadata) == []
    engine.dispose()


def test_upgrade_twice_is_harmless(alembic_config, migrated_dir):
    command.upgrade(alembic_config, "head")


@pytest.mark.parametrize(
    "statement",
    ["UPDATE observation SET value = 2.0", "DELETE FROM observation"],
)
def test_observation_is_append_only(migrated_dir, statement):
    engine = make_engine(migrated_dir)
    now = datetime(2026, 9, 25, 20, 0, tzinfo=UTC)
    with engine.begin() as conn:
        append_observations(
            conn, "vix", [NewObservation(date(2026, 9, 24), 1.0, now, False)], retrieved_at=now
        )
    with engine.connect() as conn:
        with pytest.raises(IntegrityError, match="observation is append-only"):
            conn.execute(text(statement))
        assert conn.execute(text("SELECT value FROM observation")).scalar() == 1.0
    engine.dispose()


def test_downgrade_is_refused(alembic_config, migrated_dir):
    with pytest.raises(RuntimeError, match="Downgrade verweigert"):
        command.downgrade(alembic_config, "base")
    engine = make_engine(migrated_dir)
    with engine.connect() as conn:
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'")).scalars().all()
    engine.dispose()
    assert "observation" in tables
