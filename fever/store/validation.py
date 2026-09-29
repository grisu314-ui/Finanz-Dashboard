"""Validation report (M10, E-93): one row, replaced by every validation run, read by the interface."""

import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection

from fever.store.tables import validation_report


@dataclass(frozen=True)
class StoredReport:
    computed_at: datetime
    score_computed_at: datetime
    config_hash: str
    content: dict


def replace_report(conn: Connection, content: dict, *, computed_at: datetime, score_computed_at: datetime,
                   config_hash: str) -> None:
    """Replace the report; call inside one transaction (engine.begin()). NaN is refused (plain JSON)."""
    conn.execute(delete(validation_report))
    conn.execute(insert(validation_report).values(
        id=1, computed_at=computed_at, score_computed_at=score_computed_at, config_hash=config_hash,
        content=json.dumps(content, ensure_ascii=False, allow_nan=False)))


def report_state(conn: Connection) -> tuple[datetime, str] | None:
    """(score_computed_at, config_hash) of the stored report, None if there is none."""
    row = conn.execute(select(validation_report.c.score_computed_at, validation_report.c.config_hash)).first()
    return None if row is None else (row.score_computed_at, row.config_hash)


def read_report(conn: Connection) -> StoredReport | None:
    row = conn.execute(select(validation_report)).first()
    if row is None:
        return None
    return StoredReport(row.computed_at, row.score_computed_at, row.config_hash, json.loads(row.content))
