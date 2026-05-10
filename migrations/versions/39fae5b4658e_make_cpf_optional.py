"""make_cpf_optional

Revision ID: 39fae5b4658e
Revises: d49670f854f2
Create Date: 2026-05-10 10:05:46.172201

"""
from typing import Sequence, Union
from alembic import op



# revision identifiers, used by Alembic.
revision: str = '39fae5b4658e'
down_revision: Union[str, Sequence[str], None] = 'd49670f854f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("users", "cpf", nullable=True)
    op.drop_constraint("ck_users_cpf_length", "users", type_="check")
    op.create_check_constraint("ck_users_cpf_length", "users", "cpf IS NULL OR length(cpf) =11")
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_users_cpf_length", "users", type_="check")
    op.create_check_constraint("ck_users_cpf_length", "users", "length(cpf) =11")
    op.alter_column("users", "cpf", nullable=False)
