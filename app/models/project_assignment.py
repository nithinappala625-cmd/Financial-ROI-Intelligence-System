from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.employee import Employee


class ProjectAssignment(Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "project_assignments"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    role_in_project: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="assignments")
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="assignments"
    )
