"""
User ORM model — maps to the 'users' table in PostgreSQL.

Columns: id, email, hashed_password, full_name, role, is_active, tenant_id.
Role is a PostgreSQL enum with values: admin, finance_manager, project_manager, employee.
"""

import enum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, IntegerPrimaryKeyMixin


class RoleEnum(str, enum.Enum):
    """User roles for RBAC — matches Section 3 of the design document."""

    admin = "admin"
    finance_manager = "finance_manager"
    project_manager = "project_manager"
    employee = "employee"


class User(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    """SQLAlchemy ORM model for the users table."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="roleenum", create_type=True),
        nullable=False,
        default=RoleEnum.employee,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    tenant_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role.value}>"
