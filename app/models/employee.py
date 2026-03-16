from typing import TYPE_CHECKING
from sqlalchemy import String, Date, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.work_log import WorkLog
    from app.models.project_assignment import ProjectAssignment


class Employee(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "employees"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    evs_score: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True, default=0.0
    )
    productivity_score: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True, default=0.0
    )
    is_underperforming: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    assignments: Mapped[list["ProjectAssignment"]] = relationship(
        "ProjectAssignment", back_populates="employee", cascade="all, delete"
    )
    work_logs: Mapped[list["WorkLog"]] = relationship(
        "WorkLog", back_populates="employee", cascade="all, delete"
    )
