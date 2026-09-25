import sqlite3
from datetime import date, datetime, timedelta, timezone

import pytest

from fever import backup
from fever.backup import RETENTION, BackupError, run_backup
from fever.store.db import db_path, make_engine
from fever.store.observations import NewObservation, append_observations

T0 = datetime(2026, 9, 25, 20, 0, tzinfo=timezone.utc)


def add_value(directory, value, when=T0):
    engine = make_engine(directory)
    with engine.begin() as conn:
        append_observations(conn, "vix", [NewObservation(date(2026, 9, 24), value, when, False)], retrieved_at=when)
    engine.dispose()


def values_in(path):
    connection = sqlite3.connect(path)
    try:
        return [row[0] for row in connection.execute("SELECT value FROM observation ORDER BY vintage")]
    finally:
        connection.close()


def test_backup_is_a_verified_copy(migrated_dir):
    add_value(migrated_dir, 20.5)
    path = run_backup(migrated_dir, "manual", T0)
    assert path == migrated_dir / "backup" / "fever-20260925T200000Z-manual.sqlite3"
    assert values_in(path) == [20.5]
    assert not list((migrated_dir / "backup").glob("*.partial"))


def test_backup_during_an_open_write_transaction_takes_the_committed_state(migrated_dir):
    add_value(migrated_dir, 20.5)
    writer = sqlite3.connect(db_path(migrated_dir), isolation_level=None)
    writer.execute("BEGIN IMMEDIATE")
    writer.execute(
        "INSERT INTO observation VALUES ('vix', '2026-09-25', '2026-09-25T21:00:00.000000+00:00', 0, 21.0,"
        " '2026-09-25T21:00:00.000000+00:00')"
    )
    try:
        path = run_backup(migrated_dir, "daily", T0)
    finally:
        writer.execute("ROLLBACK")
        writer.close()
    assert values_in(path) == [20.5]


def test_retention_keeps_the_newest_per_kind_and_ignores_other_files(migrated_dir):
    folder = migrated_dir / "backup"
    folder.mkdir()
    for i in range(20):
        (folder / f"fever-202608{i + 1:02d}T000000Z-daily.sqlite3").write_bytes(b"old")
        (folder / f"fever-202608{i + 1:02d}T000000Z-manual.sqlite3").write_bytes(b"old")
    (folder / "meine-notiz.txt").write_text("bleibt")
    (folder / "fever-kopie.sqlite3").write_bytes(b"bleibt")

    run_backup(migrated_dir, "daily", T0)
    run_backup(migrated_dir, "manual", T0)

    names = sorted(p.name for p in folder.iterdir())
    daily = [n for n in names if n.endswith("-daily.sqlite3")]
    manual = [n for n in names if n.endswith("-manual.sqlite3")]
    assert len(daily) == RETENTION["daily"] == 14 and daily[-1] == "fever-20260925T200000Z-daily.sqlite3"
    assert len(manual) == RETENTION["manual"] == 5 and manual[-1] == "fever-20260925T200000Z-manual.sqlite3"
    assert "meine-notiz.txt" in names and "fever-kopie.sqlite3" in names


def test_data_directory_with_special_characters(tmp_path, monkeypatch):
    from alembic import command
    from alembic.config import Config
    from tests.conftest import REPO

    odd = tmp_path / "daten #1?"
    odd.mkdir()
    monkeypatch.setenv("FEVER_DATA", str(odd))
    command.upgrade(Config(str(REPO / "alembic.ini")), "head")
    assert db_path(odd).is_file() and [p.name for p in tmp_path.iterdir()] == [odd.name]
    add_value(odd, 7.0)
    assert values_in(run_backup(odd, "manual", T0)) == [7.0]


def test_existing_backup_is_never_overwritten(migrated_dir):
    run_backup(migrated_dir, "manual", T0)
    with pytest.raises(BackupError, match="existiert bereits"):
        run_backup(migrated_dir, "manual", T0)


def test_leftover_partial_file_is_replaced(migrated_dir):
    add_value(migrated_dir, 20.5)
    folder = migrated_dir / "backup"
    folder.mkdir()
    (folder / "fever-20260925T200000Z-manual.sqlite3.partial").write_bytes(b"abgebrochen")
    path = run_backup(migrated_dir, "manual", T0)
    assert values_in(path) == [20.5]


def test_missing_database_is_an_error_with_exit_code_2(tmp_path, monkeypatch):
    with pytest.raises(BackupError, match="Keine Datenbank"):
        run_backup(tmp_path, "manual", T0)
    monkeypatch.setenv("FEVER_DATA", str(tmp_path))
    assert backup.main() == 2
    monkeypatch.delenv("FEVER_DATA")
    assert backup.main() == 2


def test_main_creates_a_manual_backup(migrated_dir, capsys):
    assert backup.main() == 0
    assert len(list((migrated_dir / "backup").glob("fever-*-manual.sqlite3"))) == 1
    assert "Backup erstellt und geprüft" in capsys.readouterr().out


def test_unknown_kind_is_rejected(migrated_dir):
    with pytest.raises(ValueError):
        run_backup(migrated_dir, "weekly", T0 + timedelta(seconds=1))
