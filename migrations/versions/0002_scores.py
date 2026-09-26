"""Score tables: indicator_score, composite_score (M5, decision E-50).

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, Sequence[str], None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UTC_TEXT = sa.String(length=32)
BLOCKS = ("volatility", "credit", "macro", "breadth", "positioning")


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "indicator_score",
        sa.Column("score_date", sa.Date(), nullable=False),
        sa.Column("indicator_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("obs_date", sa.Date(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("percentile", sa.Float(), nullable=True),
        sa.Column("percentile_display", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("score_date", "indicator_id"),
    )
    op.create_table(
        "composite_score",
        sa.Column("score_date", sa.Date(), nullable=False),
        *(sa.Column(f"block_{block}", sa.Float(), nullable=True) for block in BLOCKS),
        sa.Column("fast_block_smoothed", sa.Float(), nullable=True),
        sa.Column("stress_raw", sa.Float(), nullable=True),
        sa.Column("stress", sa.Float(), nullable=True),
        sa.Column("vulnerability_raw", sa.Float(), nullable=True),
        sa.Column("vulnerability", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("diffusion", sa.Float(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("active_rules", sa.Text(), nullable=False),
        sa.Column("computed_at", UTC_TEXT, nullable=False),
        sa.Column("config_hash", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("score_date"),
    )


def downgrade() -> None:
    """Drop the score tables; they are recomputed from the observations at any time."""
    op.drop_table("composite_score")
    op.drop_table("indicator_score")
