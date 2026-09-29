"""Validation run (M10, E-93): stored scores and closes -> backtest (fever.validation) -> validation_report.

The worker runs it after the scoring run when there are new scores or the validation itself changed
(fever/validation.py, this file, scoring.toml); `python -m fever.validate` runs it at once. Runs and
errors appear under "validation" in source_status (data status view). Nothing here changes a score.
"""

import hashlib
import logging
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.engine import Connection, Engine

from fever import log
from fever.config import CONFIG_DIR, ConfigError, scoring_config, validation_config
from fever.scoring.composite import ewma_series
from fever.store.db import DataDirError, data_dir, make_engine
from fever.store.observations import latest_pairs
from fever.store.schema import SchemaError, require_current
from fever.store.scores import score_state
from fever.store.status import record_attempt, record_success
from fever.store.tables import composite_score, indicator_score
from fever.store.validation import replace_report, report_state
from fever.validation import validate

SOURCE = "validation"
PACKAGE = Path(__file__).resolve().parent
CODE_FILES = ("validation.py", "validate.py")
PRICE_SERIES, VIX_SERIES, VIX_INDICATOR = "spx", "vix", "vix"
EVENT_NAMES = {"drawdown": "Rückgang", "vix": "VIX-Spitze", "bear": "Bärenmarkt"}
VERDICTS = {"better": "besser", "same": "nicht unterscheidbar", "worse": "schlechter"}

logger = logging.getLogger(__name__)


class NoScores(RuntimeError):
    """There are no stored scores to validate yet."""


@dataclass(frozen=True)
class Summary:
    report: dict
    seconds: float


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def config_hash(config_dir: Path = CONFIG_DIR, package: Path = PACKAGE) -> str:
    """Fingerprint of the validation code and scoring.toml ([validation] and the "erhöht" mark)."""
    digest = hashlib.sha256()
    digest.update(b"scoring.toml\0" + (config_dir / "scoring.toml").read_bytes() + b"\0")
    for name in CODE_FILES:
        digest.update(name.encode() + b"\0" + (package / name).read_bytes() + b"\0")
    return digest.hexdigest()


def needs_run(engine: Engine, digest: str) -> bool:
    """True once there are scores without a report on them, or the validation changed."""
    with engine.connect() as conn:
        scores = score_state(conn)
        report = report_state(conn)
    if scores is None:
        return False
    return report is None or report != (scores[0], digest)


def run(engine: Engine, *, clock=_utcnow, config_dir: Path = CONFIG_DIR) -> Summary:
    """Validate the stored scores and replace the report."""
    started, start = clock(), time.monotonic()
    config = validation_config(config_dir)
    scoring = scoring_config(config_dir)
    digest = config_hash(config_dir)
    with engine.begin() as conn:
        record_attempt(conn, SOURCE, started)
    with engine.connect() as conn:  # one read transaction: scores and closes of the same moment
        state = score_state(conn)
        if state is None:
            raise NoScores("Noch keine Scores: erst python -m fever.score")
        scores = _scores(conn)
        vix_percentile = _vix_percentile(conn)
        spx, vix = _series(conn, PRICE_SERIES), _series(conn, VIX_SERIES)
        blocks = _blocks(conn, config.fit_blocks, scoring.fast_block, scoring.stress_half_life)
    report = validate(spx, vix, scores, vix_percentile, config, scoring.yellow_diffusion_percentile, blocks)
    with engine.begin() as conn:
        replace_report(conn, report, computed_at=started, score_computed_at=state[0], config_hash=digest)
        record_success(conn, SOURCE, clock())
    return Summary(report, time.monotonic() - start)


def describe(summary: Summary) -> str:
    """One log line: per event the AUC of stress and VIX percentile and the verdict."""
    def number(value):
        return "–" if value is None else f"{value:.2f}".replace(".", ",")

    parts = []
    for event, result in summary.report["events"].items():
        auc, difference = result.get("auc", {}), result.get("auc_difference")
        if not difference:  # no closes (e.g. spx before its first retrieval) or no scores: no day to evaluate
            parts.append(f"{EVENT_NAMES[event]}: {'zu wenige Ereignisse' if result.get('days') else 'keine auswertbaren Tage'}")
            continue
        text = (f"{EVENT_NAMES[event]}: AUC Stress {number(auc['stress']['value'])}, VIX {number(auc['vix']['value'])} "
                f"({VERDICTS[difference['verdict']]})")
        fitted = (result.get("fitted") or {}).get("auc_differences", {}).get("fitted-equal")
        if fitted:  # M11: estimated against equal weights
            aucs = result["fitted"]["auc"]
            text += (f", geschätzte Gewichte {number(aucs['fitted']['value'])} gegen gleiche {number(aucs['equal']['value'])} "
                     f"({VERDICTS[fitted['verdict']]})")
        parts.append(text)
    return f"Validierung berechnet: {'; '.join(parts)} ({number(summary.seconds)} s)"


def _scores(conn: Connection) -> pd.DataFrame:
    rows = conn.execute(select(composite_score.c.score_date, composite_score.c.level, composite_score.c.stress,
                               composite_score.c.vulnerability).order_by(composite_score.c.score_date)).all()
    return pd.DataFrame([row[1:] for row in rows], index=[row[0] for row in rows],
                        columns=["level", "stress", "vulnerability"], dtype=float)


def _vix_percentile(conn: Connection) -> pd.Series:
    rows = conn.execute(select(indicator_score.c.score_date, indicator_score.c.percentile)
                        .where(indicator_score.c.indicator_id == VIX_INDICATOR, indicator_score.c.status == "ok")
                        .order_by(indicator_score.c.score_date)).all()
    return pd.Series([row[1] for row in rows], index=[row[0] for row in rows], dtype=float)


def _blocks(conn: Connection, names: tuple[str, ...], fast_block: str, half_life: float) -> pd.DataFrame:
    """The stress blocks of the walk-forward logit (M11) per score day, smoothed like the composite: the fast
    block as stored after its own smoothing, then every block with the half-life of the stress."""
    columns = [composite_score.c.fast_block_smoothed if name == fast_block else composite_score.c[f"block_{name}"]
               for name in names]
    rows = conn.execute(select(composite_score.c.score_date, *columns).order_by(composite_score.c.score_date)).all()
    days = [row[0] for row in rows]
    return pd.DataFrame({name: ewma_series([row[i + 1] for row in rows], half_life) for i, name in enumerate(names)},
                        index=days, dtype=float)


def _series(conn: Connection, series_id: str) -> pd.Series:
    pairs: list[tuple[date, float]] = latest_pairs(conn, series_id)
    return pd.Series([value for _, value in pairs], index=[day for day, _ in pairs], dtype=float)


def main() -> int:
    log.setup()
    try:
        engine = make_engine(data_dir())
        with engine.connect() as conn:
            require_current(conn)
        summary = run(engine)
    except (DataDirError, ConfigError, SchemaError, NoScores) as exc:
        logger.error("Validierung nicht gestartet: %s", exc)
        return 2
    logger.info("%s", describe(summary))
    engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
