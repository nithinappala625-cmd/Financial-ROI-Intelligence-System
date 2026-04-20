"""add read replica logic analytics

Revision ID: 2ab388c58444
Revises: 4bf08f74b2c4
Create Date: 2026-03-24 17:16:23.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ab388c58444'
down_revision: Union[str, Sequence[str], None] = '4bf08f74b2c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add analytics indexes to support read-replica query patterns."""
    # Index on ai_predictions for fast tenant/project analytics queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_ai_predictions_project_id
        ON ai_predictions (project_id)
    """)
    # Index on expenses for analytics: project + date range queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_expenses_project_id_date
        ON expenses (project_id, date)
    """)
    # Index on work_logs for employee analytics queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_work_logs_employee_id
        ON work_logs (employee_id)
    """)


def downgrade() -> None:
    """Remove analytics indexes."""
    op.execute("DROP INDEX IF EXISTS ix_ai_predictions_project_id")
    op.execute("DROP INDEX IF EXISTS ix_expenses_project_id_date")
    op.execute("DROP INDEX IF EXISTS ix_work_logs_employee_id")
