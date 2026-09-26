import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from fever.store.db import BUSY_TIMEOUT_MS, DataDirError, data_dir, db_path, make_engine


def pragma(conn, name):
    return conn.execute(text(f"PRAGMA {name}")).scalar()


def test_data_dir_requires_fever_data(monkeypatch):
    monkeypatch.delenv("FEVER_DATA", raising=False)
    with pytest.raises(DataDirError, match="FEVER_DATA ist nicht gesetzt"):
        data_dir()


def test_data_dir_must_exist(tmp_path, monkeypatch):
    monkeypatch.setenv("FEVER_DATA", str(tmp_path / "missing"))
    with pytest.raises(DataDirError, match="Datenordner fehlt"):
        data_dir()


def test_engine_never_creates_a_database(tmp_path):
    for read_only in (False, True):
        with pytest.raises(DataDirError, match="Datenbank fehlt"):
            make_engine(tmp_path, read_only=read_only)
    assert not db_path(tmp_path).exists()


def test_writer_connection_pragmas(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.connect() as conn:
        assert pragma(conn, "foreign_keys") == 1
        assert pragma(conn, "journal_mode") == "wal"
        assert pragma(conn, "busy_timeout") == BUSY_TIMEOUT_MS
        assert pragma(conn, "query_only") == 0
    engine.dispose()


def test_read_only_connection_cannot_write(migrated_dir):
    engine = make_engine(migrated_dir, read_only=True)
    with engine.connect() as conn:
        assert pragma(conn, "query_only") == 1
        assert pragma(conn, "journal_mode") == "wal"
        with pytest.raises(OperationalError, match="readonly"):
            conn.execute(text("INSERT INTO heartbeat VALUES ('web', '2026-09-25T00:00:00.000000+00:00')"))
    engine.dispose()
