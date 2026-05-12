"""make_age_nullable

Revision ID: 853f5bf3b7e6
Revises: e5cb1eec9149
Create Date: 2026-05-12 14:40:11.820055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '853f5bf3b7e6'
down_revision: Union[str, Sequence[str], None] = 'e5cb1eec9149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'age', nullable=True)

def downgrade() -> None:
    op.alter_column('users', 'age', nullable=False)
