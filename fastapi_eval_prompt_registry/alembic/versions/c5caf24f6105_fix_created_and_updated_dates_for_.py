"""fix created and updated dates for golend example

Revision ID: c5caf24f6105
Revises: 56ffe8abdfd3
Create Date: 2026-10-06 17:26:45.534339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5caf24f6105'
down_revision: Union[str, Sequence[str], None] = '56ffe8abdfd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "golden_examples",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )
    op.alter_column(
        "golden_examples",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "golden_examples",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "golden_examples",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
        server_default=None,
    )  