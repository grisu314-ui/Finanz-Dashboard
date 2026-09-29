"""Validation report (M10, decision E-93): one row with the backtest of the traffic light as JSON.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UTC_TEXT = sa.String(length=32)


def upgrade() -> None:
    """Create the table; it stays empty until the next validation run fills it."""
    op.create_table(
        "validation_report",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("computed_at", UTC_TEXT, nullable=False),
        sa.Column("score_computed_at", UTC_TEXT, nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop the table; the report is recomputed from the scores at any time."""
    op.drop_table("validation_report")
