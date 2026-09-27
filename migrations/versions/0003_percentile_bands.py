"""Percentile bands 10/50/90 in indicator_score (M7, decision E-64).

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BANDS = ("band_p10", "band_p50", "band_p90")


def upgrade() -> None:
    """Add the band columns; they stay empty until the next scoring run fills them."""
    for name in BANDS:
        op.add_column("indicator_score", sa.Column(name, sa.Float(), nullable=True))


def downgrade() -> None:
    """Drop the band columns; SQLite needs a table rebuild for that (batch mode)."""
    with op.batch_alter_table("indicator_score") as batch:
        for name in BANDS:
            batch.drop_column(name)
