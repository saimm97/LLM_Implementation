"""create dummy table

Revision ID: 47335c58910c
Revises: 
Create Date: 2026-07-05 18:59:36.082010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '47335c58910c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:   
    op.create_table(
        'dummy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # pass


def downgrade() -> None:
    op.drop_table('dummy')
    # pass
