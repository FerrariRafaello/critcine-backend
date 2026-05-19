"""add_token_version_to_users

Revision ID: b2e4f7a1c3d8
Revises: a1f3c9d2e4b7
Create Date: 2026-05-19 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'b2e4f7a1c3d8'
down_revision: Union[str, Sequence[str], None] = 'a1f3c9d2e4b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS token_version")
