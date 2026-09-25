"""Database backups via VACUUM INTO, verified before they count, with bounded retention.

Kinds (decision E-8):
- "daily": made by the worker once a day (from milestone M3), 14 kept.
- "manual": `python -m fever.backup`; the migration procedure uses it, 5 kept.

Never copy the live database file with cp; VACUUM INTO reads a consistent
snapshot even while the worker writes.
"""

import logging
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from fever import log
from fever.store.db import DataDirError, data_dir, db_path, make_engine

RETENTION = {"daily": 14, "manual": 5}
_BACKUP_NAME = re.compile(r"fever-\d{8}T\d{6}Z-(daily|manual)\.sqlite3")

logger = logging.getLogger(__name__)


class BackupError(RuntimeError):
    """Backup could not be created or failed verification."""


def run_backup(directory: Path, kind: str, now: datetime) -> Path:
    """Create backup/fever-<UTC time>-<kind>.sqlite3, verify it, then apply retention."""
    if kind not in RETENTION:
        raise ValueError(f"Unbekannte Backup-Art: {kind!r}")
    if not db_path(directory).is_file():
        raise BackupError(f"Keine Datenbank vorhanden: {db_path(directory)}")

    backup_dir = directory / "backup"
    backup_dir.mkdir(exist_ok=True)
    stamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = backup_dir / f"fever-{stamp}-{kind}.sqlite3"
    if target.exists():
        raise BackupError(f"Backup existiert bereits: {target}")
    partial = backup_dir / f"{target.name}.partial"
    partial.unlink(missing_ok=True)  # leftover of an interrupted run

    engine = make_engine(directory)
    try:
        # VACUUM cannot run inside a transaction, hence autocommit.
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            conn.exec_driver_sql("VACUUM INTO ?", (str(partial),))
    finally:
        engine.dispose()

    _verify(partial)
    os.replace(partial, target)
    _apply_retention(backup_dir, kind)
    return target


def _verify(path: Path) -> None:
    # as_uri() percent-encodes, so paths with "#" or "?" stay intact.
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchall()
    finally:
        connection.close()
    if result != [("ok",)]:
        raise BackupError(f"Backup fehlerhaft, verworfen: {path}: {result[:5]}")


def _apply_retention(backup_dir: Path, kind: str) -> None:
    own = sorted(
        path
        for path in backup_dir.iterdir()
        if (match := _BACKUP_NAME.fullmatch(path.name)) and match.group(1) == kind
    )
    for old in own[: -RETENTION[kind]]:
        old.unlink()
        logger.info("Altes Backup gelöscht (Aufbewahrung %s: %d): %s", kind, RETENTION[kind], old.name)


def main() -> int:
    log.setup()
    try:
        path = run_backup(data_dir(), "manual", datetime.now(timezone.utc))
    except (BackupError, DataDirError) as exc:
        logger.error("%s", exc)
        return 2
    logger.info("Backup erstellt und geprüft: %s", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
