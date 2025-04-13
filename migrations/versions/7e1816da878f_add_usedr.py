"""Add user role column

Revision ID: 7e1816da878f
Revises: 7b0d4b81a838
Create Date: 2025-04-12 13:41:14.994813
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e1816da878f"
down_revision: Union[str, None] = "7b0d4b81a838"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Створення enum-типу окремо
user_role_enum = sa.Enum("USER", "ADMIN", name="userrole")


def upgrade() -> None:
    """Upgrade schema."""
    # Створення ENUM типу вручну (рекомендується для rollback'у)
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("role", user_role_enum, nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")
