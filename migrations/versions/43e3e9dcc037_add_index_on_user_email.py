"""add index on user email

Revision ID: 43e3e9dcc037
Revises: e0edeae97bd3
Create Date: 2026-03-24 17:16:19.971517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43e3e9dcc037'
down_revision: Union[str, Sequence[str], None] = 'e0edeae97bd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on users.email for fast login lookups."""
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove index on users.email."""
    op.drop_index('ix_users_email', table_name='users')
