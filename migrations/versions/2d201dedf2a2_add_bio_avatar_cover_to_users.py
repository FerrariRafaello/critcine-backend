"""add_bio_avatar_cover_to_users

Revision ID: 2d201dedf2a2
Revises: 39fae5b4658e
Create Date: 2026-05-10 10:54:41.042559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d201dedf2a2'
down_revision: Union[str, Sequence[str], None] = '39fae5b4658e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("bio", sa.Text, nullable=True))
    op.add_column("users", sa.Column("avatar_id", sa.Text, nullable=True))
    op.add_column("users", sa.Column("cover_id", sa.Text, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "cover_id")
    op.drop_column("users", "avatar_id")
    op.drop_column("users", "bio")
