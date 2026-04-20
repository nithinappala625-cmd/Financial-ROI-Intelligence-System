"""add created_at to some tables

Revision ID: 448fcb899f7c
Revises: 0e62cc0a5bbd
Create Date: 2026-03-24 17:16:21.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '448fcb899f7c'
down_revision: Union[str, Sequence[str], None] = '0e62cc0a5bbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_at column to work_logs and alerts if missing."""
    # work_logs
    op.execute("""
        ALTER TABLE work_logs
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE
            NOT NULL DEFAULT NOW()
    """)
    # alerts
    op.execute("""
        ALTER TABLE alerts
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE
            NOT NULL DEFAULT NOW()
    """)


def downgrade() -> None:
    """Remove created_at from work_logs and alerts."""
    op.drop_column('work_logs', 'created_at')
    op.drop_column('alerts', 'created_at')
