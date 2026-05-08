"""create_watchlist_table

Revision ID: d49670f854f2
Revises: e9248bee0c1f
Create Date: 2026-05-08 07:02:42.657391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd49670f854f2'
down_revision: Union[str, Sequence[str], None] = 'e9248bee0c1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "watchlist",
        sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tmdb_movie_id", sa.Integer, nullable=False),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('want_to_watch', 'watching', 'watched', 'dropped')", name="ck_watchlist_status"),
        sa.UniqueConstraint("user_id", "tmdb_movie_id", name="uq_watchlist_user_movie"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("watchlist")
