"""add index on project name

Revision ID: 0e62cc0a5bbd
Revises: 43e3e9dcc037
Create Date: 2026-03-24 17:16:20.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e62cc0a5bbd'
down_revision: Union[str, Sequence[str], None] = '43e3e9dcc037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add index on projects.name for fast project lookups."""
    op.create_index(
        'ix_projects_name',
        'projects',
        ['name'],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove index on projects.name."""
    op.drop_index('ix_projects_name', table_name='projects')
