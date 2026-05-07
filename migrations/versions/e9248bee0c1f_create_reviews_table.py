"""create_reviews_table

Revision ID: e9248bee0c1f
Revises: d0445f2c45e0
Create Date: 2026-05-07 11:20:13.491396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9248bee0c1f'
down_revision: Union[str, Sequence[str], None] = 'd0445f2c45e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tmdb_movie_id", sa.Integer, nullable=False),
        sa.Column("rating", sa.Float, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("rating >= 0 AND rating <=10", name="ck_reviews_rating_range"),
        sa.UniqueConstraint("user_id", "tmdb_movie_id", name="uq_reviews_user_movie"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("reviews")
