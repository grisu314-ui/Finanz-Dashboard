"""Table definitions (SQLAlchemy Core).

The schema is created only by Alembic migrations (migrations/versions/); these
definitions must match them, which tests/test_migrations.py checks.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, Float, Integer, MetaData, String, Table, Text
from sqlalchemy.types import TypeDecorator


class UtcDateTime(TypeDecorator):
    """Timezone-aware timestamp stored as fixed-width UTC ISO 8601 text.

    Fixed width keeps the text sortable in time order. Naive datetimes are
    rejected: a local time mistaken for UTC would shift publication times.
    """

    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"Zeitstempel ohne Zeitzone: {value!r}")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return datetime.fromisoformat(value)


metadata = MetaData()

# Append-only: UPDATE and DELETE are blocked by triggers (migration 0001).
# vintage = point in time from which the value was known (UTC); vintage_estimated
# marks backfilled values whose vintage is observation date + configured lag.
observation = Table(
    "observation",
    metadata,
    Column("series_id", String(64), primary_key=True),
    Column("obs_date", Date, primary_key=True),
    Column("vintage", UtcDateTime, primary_key=True),
    Column("vintage_estimated", Boolean, nullable=False),
    Column("value", Float, nullable=False),
    Column("retrieved_at", UtcDateTime, nullable=False),
)

# One row per source, overwritten; the last error stays visible after a later success.
source_status = Table(
    "source_status",
    metadata,
    Column("source", String(32), primary_key=True),
    Column("last_attempt_at", UtcDateTime),
    Column("last_success_at", UtcDateTime),
    Column("last_error_at", UtcDateTime),
    Column("last_error_message", Text),
)

heartbeat = Table(
    "heartbeat",
    metadata,
    Column("component", String(32), primary_key=True),
    Column("beat_at", UtcDateTime, nullable=False),
)

# Scores (M5, decision E-50): derived data, recomputed completely and replaced in one
# transaction (fever.score); never an input of anything else. Percentiles are oriented so
# that high = more stress or vulnerability (0-100).
indicator_score = Table(
    "indicator_score",
    metadata,
    Column("score_date", Date, primary_key=True),
    Column("indicator_id", String(64), primary_key=True),
    Column("status", String(16), nullable=False),  # ok | stale | history | missing
    Column("obs_date", Date),
    Column("value", Float),
    Column("percentile", Float),
    Column("percentile_display", Float),  # shorter display window (display_window = true)
)

composite_score = Table(
    "composite_score",
    metadata,
    Column("score_date", Date, primary_key=True),
    Column("block_volatility", Float),
    Column("block_credit", Float),
    Column("block_macro", Float),
    Column("block_breadth", Float),
    Column("block_positioning", Float),
    Column("fast_block_smoothed", Float),
    Column("stress_raw", Float),
    Column("stress", Float),
    Column("vulnerability_raw", Float),
    Column("vulnerability", Float),
    Column("confidence", Float, nullable=False),
    Column("diffusion", Float),
    Column("level", Integer, nullable=False),  # 0 green, 1 yellow, 2 orange, 3 red
    Column("active_rules", Text, nullable=False),  # comma separated, empty if none
    Column("computed_at", UtcDateTime, nullable=False),
    Column("config_hash", String(64), nullable=False),
)
