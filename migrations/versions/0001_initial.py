"""Initial schema: observation (append-only), source_status, heartbeat.

Revision ID: 0001
Revises:
Create Date: 2026-09-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# UTC timestamps are fixed-width ISO 8601 text (fever.store.tables.UtcDateTime).
UTC_TEXT = sa.String(length=32)


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "observation",
        sa.Column("series_id", sa.String(length=64), nullable=False),
        sa.Column("obs_date", sa.Date(), nullable=False),
        sa.Column("vintage", UTC_TEXT, nullable=False),
        sa.Column("vintage_estimated", sa.Boolean(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("retrieved_at", UTC_TEXT, nullable=False),
        sa.PrimaryKeyConstraint("series_id", "obs_date", "vintage"),
    )
    # The observation archive (including irreplaceable ICE data) is append-only.
    for action in ("UPDATE", "DELETE"):
        op.execute(
            f"CREATE TRIGGER observation_no_{action.lower()} BEFORE {action} ON observation "
            "BEGIN SELECT RAISE(ABORT, 'observation is append-only'); END"
        )
    op.create_table(
        "source_status",
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("last_attempt_at", UTC_TEXT, nullable=True),
        sa.Column("last_success_at", UTC_TEXT, nullable=True),
        sa.Column("last_error_at", UTC_TEXT, nullable=True),
        sa.Column("last_error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("source"),
    )
    op.create_table(
        "heartbeat",
        sa.Column("component", sa.String(length=32), nullable=False),
        sa.Column("beat_at", UTC_TEXT, nullable=False),
        sa.PrimaryKeyConstraint("component"),
    )


def downgrade() -> None:
    """Refused: it would drop the observation archive."""
    raise RuntimeError("Downgrade verweigert: würde das Beobachtungsarchiv (inkl. ICE-Daten) löschen.")
