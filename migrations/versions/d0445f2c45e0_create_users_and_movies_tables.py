"""create_users_and_movies_tables

Revision ID: d0445f2c45e0
Revises: 
Create Date: 2026-05-05 06:11:42.433435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0445f2c45e0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("age", sa.Integer, nullable=False),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("cpf", sa.Text, nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.CheckConstraint("length(trim(name)) BETWEEN 2 AND 50", name="ck_users_name_length"),
        sa.CheckConstraint("age BETWEEN 18 AND 100", name="ck_users_age_range"),
        sa.CheckConstraint("length(cpf)=11",name="ck_users_cpf_length")
    )

    op.create_table(
        "movies",
        sa.Column("id", sa.Integer, sa.Identity(always=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("rating", sa.Float, nullable=False, unique=True),
        sa.CheckConstraint("length(trim(name)) BETWEEN 2 AND 50", name="ck_movies_name_length"),
        sa.CheckConstraint("year BETWEEN 1800 AND 2026", name="ck_movies_age_range"),
        sa.CheckConstraint("rating IS NULL OR (rating>=0 AND rating <=10)", name="ck_movies_rating_range")
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("movies")
    op.drop_table("users")
