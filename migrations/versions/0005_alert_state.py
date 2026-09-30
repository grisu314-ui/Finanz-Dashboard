"""Alert state (M12, decisions E-99, E-100): per kind of alert what the last message reported.

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UTC_TEXT = sa.String(length=32)


def upgrade() -> None:
    """Create the table; the first worker cycle with a topic fills it and reports today's state once."""
    op.create_table(
        "alert_state",
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("updated_at", UTC_TEXT, nullable=False),
        sa.PrimaryKeyConstraint("kind"),
    )


def downgrade() -> None:
    """Drop the table; without it the next worker cycle reports today's state once more."""
    op.drop_table("alert_state")
