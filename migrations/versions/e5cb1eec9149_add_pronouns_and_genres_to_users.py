"""add_pronouns_and_genres_to_users

Revision ID: e5cb1eec9149
Revises: 2d201dedf2a2
Create Date: 2026-05-11 08:18:45.597940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5cb1eec9149'
down_revision: Union[str, Sequence[str], None] = '2d201dedf2a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("pronouns", sa.Text, nullable=True))
    op.add_column("users", sa.Column("favorite_genres", sa.Text, nullable=True))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "favorite_genres")
    op.drop_column("users", "pronouns")
