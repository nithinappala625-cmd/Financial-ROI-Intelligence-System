from typing import TYPE_CHECKING
from sqlalchemy import Float, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project


class WorkLog(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "work_logs"

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    task_description: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    contribution_value: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", back_populates="work_logs")
    project: Mapped["Project"] = relationship("Project", back_populates="work_logs")
