"""
Models package — imports all ORM models so Alembic can detect them.
"""

from app.models.base import Base, TimestampMixin, IntegerPrimaryKeyMixin
from app.models.user import User, RoleEnum

# Placeholder model imports — uncomment as developers implement them:
# from app.models.project import Project
# from app.models.expense import Expense
# from app.models.employee import Employee
# from app.models.work_log import WorkLog
# from app.models.alert import Alert
# from app.models.ai_prediction import AIPrediction
# from app.models.project_assignment import ProjectAssignment

__all__ = [
    "Base",
    "TimestampMixin",
    "IntegerPrimaryKeyMixin",
    "User",
    "RoleEnum",
]
