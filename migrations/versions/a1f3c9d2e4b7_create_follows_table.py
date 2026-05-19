"""create_follows_table

Revision ID: a1f3c9d2e4b7
Revises: 8039e6344e06
Create Date: 2026-05-19 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'a1f3c9d2e4b7'
down_revision: Union[str, Sequence[str], None] = '8039e6344e06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            followed_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (follower_id, followed_id),
            CHECK (follower_id != followed_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_follows_followed ON follows(followed_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS follows")
