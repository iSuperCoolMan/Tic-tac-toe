"""craate_pydantic_board_model

Revision ID: 18901887f88a
Revises: 9bb94a525a03
Create Date: 2026-04-16 04:12:40.720628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18901887f88a'
down_revision: Union[str, Sequence[str], None] = '9bb94a525a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('games', 'board')
    op.add_column('games', sa.Column(
        'board',
        sa.JSON(),
        nullable=False,
        server_default='[["", "", ""], ["", "", ""], ["", "", ""]]'
    ))


def downgrade() -> None:
    op.drop_column('games', 'board')
    op.add_column('games', sa.Column(
        'board',
        sa.JSON(),
        nullable=False,
        server_default='[]'
    ))
