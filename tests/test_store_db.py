import threading
import time
from datetime import datetime, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from fever.store.db import BUSY_TIMEOUT_MS, DataDirError, data_dir, db_path, make_engine
from fever.store.status import read_heartbeat, record_heartbeat


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


def test_a_second_writer_waits_for_the_first(migrated_dir):
    """A one-off command next to the worker waits for the worker's write instead of failing (30.09.2026): replacing
    all scores held the write lock 7.9 s in the development environment, so the wait must be far longer."""
    assert BUSY_TIMEOUT_MS >= 60_000
    worker, command = make_engine(migrated_dir), make_engine(migrated_dir)
    at = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)
    locked = threading.Event()

    def long_write():
        with worker.begin() as conn:
            record_heartbeat(conn, "worker", at)
            locked.set()
            time.sleep(0.5)

    thread = threading.Thread(target=long_write)
    thread.start()
    assert locked.wait(5)
    start = time.monotonic()
    with command.begin() as conn:
        record_heartbeat(conn, "command", at)
    waited = time.monotonic() - start
    thread.join()
    with command.connect() as conn:
        assert read_heartbeat(conn, "worker") == at and read_heartbeat(conn, "command") == at
    assert waited >= 0.3
    worker.dispose()
    command.dispose()


def test_read_only_connection_cannot_write(migrated_dir):
    engine = make_engine(migrated_dir, read_only=True)
    with engine.connect() as conn:
        assert pragma(conn, "query_only") == 1
        assert pragma(conn, "journal_mode") == "wal"
        with pytest.raises(OperationalError, match="readonly"):
            conn.execute(text("INSERT INTO heartbeat VALUES ('web', '2026-09-25T00:00:00.000000+00:00')"))
    engine.dispose()
