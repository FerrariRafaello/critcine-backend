"""add_unique_name_users

Revision ID: 8039e6344e06
Revises: 853f5bf3b7e6
Create Date: 2026-05-13 03:00:54.743228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8039e6344e06'
down_revision: Union[str, Sequence[str], None] = '853f5bf3b7e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_users_name", "users", ["name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_name", "users", type_="unique")
