"""
Models package — imports all ORM models so SQLAlchemy
relationship resolution and Alembic autogenerate work correctly.
"""

from app.models.base import Base, TimestampMixin, IntegerPrimaryKeyMixin
from app.models.user import User, RoleEnum
from app.models.project import Project
from app.models.expense import Expense
from app.models.employee import Employee
from app.models.work_log import WorkLog
from app.models.alert import Alert
from app.models.ai_prediction import AIPrediction
from app.models.project_assignment import ProjectAssignment
from app.models.milestone import Milestone

__all__ = [
    "Base",
    "TimestampMixin",
    "IntegerPrimaryKeyMixin",
    "User",
    "RoleEnum",
    "Project",
    "Expense",
    "Employee",
    "WorkLog",
    "Alert",
    "AIPrediction",
    "ProjectAssignment",
    "Milestone",
]
