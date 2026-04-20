"""add updated_at to some tables

Revision ID: 4bf08f74b2c4
Revises: 448fcb899f7c
Create Date: 2026-03-24 17:16:22.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bf08f74b2c4'
down_revision: Union[str, Sequence[str], None] = '448fcb899f7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add updated_at column to work_logs and alerts if missing."""
    # work_logs
    op.execute("""
        ALTER TABLE work_logs
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
            NOT NULL DEFAULT NOW()
    """)
    # alerts
    op.execute("""
        ALTER TABLE alerts
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
            NOT NULL DEFAULT NOW()
    """)


def downgrade() -> None:
    """Remove updated_at from work_logs and alerts."""
    op.drop_column('work_logs', 'updated_at')
    op.drop_column('alerts', 'updated_at')
