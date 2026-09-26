"""Scoring run: newest values -> scores (fever.scoring) -> score tables, in one transaction.

The worker runs it after each cycle when observations were stored since the last run or
scoring.toml/series.toml changed (E-50). `python -m fever.score` runs it at once. Runs and
errors appear under "scoring" in source_status (data status view).
"""

import hashlib
import logging
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy.engine import Engine

from fever import log
from fever.config import CONFIG_DIR, ConfigError, indicator_catalog, scoring_config
from fever.scoring.composite import CompositeScore
from fever.scoring.pipeline import score
from fever.store.db import DataDirError, data_dir, make_engine
from fever.store.observations import latest_values
from fever.store.scores import newest_retrieval, replace_scores, score_state
from fever.store.status import record_attempt, record_success

SOURCE = "scoring"
CALENDAR_SERIES = "vix"  # score days are the Cboe trading days with a VIX close (E-49)
CONFIG_FILES = ("scoring.toml", "series.toml")
LEVEL_NAMES = ("Grün", "Gelb", "Orange", "Rot")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Summary:
    days: int
    first: date | None
    last: CompositeScore | None
    seconds: float


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def config_hash(config_dir: Path = CONFIG_DIR) -> str:
    digest = hashlib.sha256()
    for name in CONFIG_FILES:
        digest.update(name.encode() + b"\0" + (config_dir / name).read_bytes() + b"\0")
    return digest.hexdigest()


def needs_run(engine: Engine, digest: str) -> bool:
    """True without stored scores, after a configuration change or after newly stored observations."""
    with engine.connect() as conn:
        state = score_state(conn)
        newest = newest_retrieval(conn)
    if state is None:
        return True
    computed_at, stored_digest = state
    return stored_digest != digest or (newest is not None and newest > computed_at)


def run(engine: Engine, *, clock=_utcnow, config_dir: Path = CONFIG_DIR) -> Summary:
    """Recompute every score from the stored observations and replace the score tables."""
    started, start = clock(), time.monotonic()
    indicators = list(indicator_catalog(config_dir).values())
    config = scoring_config(config_dir)
    digest = config_hash(config_dir)
    series_ids = sorted({series.id for indicator in indicators for series in indicator.series} | {CALENDAR_SERIES})
    with engine.begin() as conn:
        record_attempt(conn, SOURCE, started)
    with engine.connect() as conn:
        raw = {series_id: _as_series(latest_values(conn, series_id)) for series_id in series_ids}
    calendar = list(raw[CALENDAR_SERIES].index)
    indicator_rows, composite_rows = score(raw, indicators, calendar, config)
    with engine.begin() as conn:
        replace_scores(conn, indicator_rows, composite_rows, computed_at=started, config_hash=digest)
        record_success(conn, SOURCE, clock())
    return Summary(
        len(composite_rows),
        composite_rows[0].score_date if composite_rows else None,
        composite_rows[-1] if composite_rows else None,
        time.monotonic() - start,
    )


def describe(summary: Summary) -> str:
    def number(value):
        return "–" if value is None else f"{value:.1f}".replace(".", ",")

    if summary.last is None:
        return f"Scores berechnet: keine Tage mit gültigem Indikator ({number(summary.seconds)} s)"
    last = summary.last

    return (
        f"Scores berechnet: {summary.days} Tage ab {summary.first:%d.%m.%Y}, zuletzt {last.score_date:%d.%m.%Y}: "
        f"Stress {number(last.stress)}, Fallhöhe {number(last.vulnerability)}, Ampel {LEVEL_NAMES[last.level]}, "
        f"Konfidenz {number(last.confidence)} % ({number(summary.seconds)} s)"
    )


def _as_series(rows) -> pd.Series:
    return pd.Series([row.value for row in rows], index=[row.obs_date for row in rows], dtype=float)


def main() -> int:
    log.setup()
    try:
        engine = make_engine(data_dir())
        summary = run(engine)
    except (DataDirError, ConfigError) as exc:
        logger.error("Scoring nicht gestartet: %s", exc)
        return 2
    logger.info("%s", describe(summary))
    engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
