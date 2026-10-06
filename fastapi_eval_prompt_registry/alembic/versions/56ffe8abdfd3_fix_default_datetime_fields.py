"""fix default datetime fields

Revision ID: 56ffe8abdfd3
Revises: fdd324cb4b25
Create Date: 2026-09-29 20:11:49.842851

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "56ffe8abdfd3"
down_revision: Union[str, Sequence[str], None] = "fdd324cb4b25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "eval_runs",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.alter_column(
        "eval_runs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "eval_runs",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "eval_runs",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )