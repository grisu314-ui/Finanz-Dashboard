"""Score tables (M5, E-50): replaced as a whole by every scoring run, read by the interface."""

from dataclasses import asdict
from datetime import datetime

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Connection

from fever.config import STRESS_BLOCKS
from fever.scoring.composite import CompositeScore, IndicatorScore
from fever.store.tables import composite_score, indicator_score, observation

_CHUNK = 5000  # rows per INSERT; keeps the parameter lists of executemany moderate


def replace_scores(
    conn: Connection,
    indicators: list[IndicatorScore],
    composites: list[CompositeScore],
    *,
    computed_at: datetime,
    config_hash: str,
) -> None:
    """Delete all scores and insert the new ones; call inside one transaction (engine.begin())."""
    conn.execute(delete(indicator_score))
    conn.execute(delete(composite_score))
    indicator_rows = [asdict(row) for row in indicators]
    composite_rows = [_composite_row(row, computed_at, config_hash) for row in composites]
    for table, rows in ((indicator_score, indicator_rows), (composite_score, composite_rows)):
        for start in range(0, len(rows), _CHUNK):
            conn.execute(insert(table), rows[start : start + _CHUNK])


def score_state(conn: Connection) -> tuple[datetime, str] | None:
    """(computed_at, config_hash) of the stored scores, None if there are none."""
    row = conn.execute(select(composite_score.c.computed_at, composite_score.c.config_hash).limit(1)).first()
    return None if row is None else (row.computed_at, row.config_hash)


def newest_retrieval(conn: Connection) -> datetime | None:
    """Time of the most recent fetch that stored an observation."""
    return conn.execute(select(func.max(observation.c.retrieved_at))).scalar()


def _composite_row(row: CompositeScore, computed_at: datetime, config_hash: str) -> dict:
    values = asdict(row)
    blocks = values.pop("blocks")
    values["active_rules"] = ",".join(values["active_rules"])
    values.update({f"block_{block}": blocks[block] for block in STRESS_BLOCKS})
    values.update(computed_at=computed_at, config_hash=config_hash)
    return values
