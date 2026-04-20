from typing import TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.project_assignment import ProjectAssignment
    from app.models.ai_prediction import AIPrediction
    from app.models.work_log import WorkLog


class Project(Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    expenditure: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, default=0.0
    )
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    start_date: Mapped[datetime.date | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime.date | None] = mapped_column(DateTime, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense", back_populates="project", cascade="all, delete"
    )
    assignments: Mapped[list["ProjectAssignment"]] = relationship(
        "ProjectAssignment", back_populates="project", cascade="all, delete"
    )
    ai_predictions: Mapped[list["AIPrediction"]] = relationship(
        "AIPrediction", back_populates="project", cascade="all, delete"
    )
    work_logs: Mapped[list["WorkLog"]] = relationship(
        "WorkLog", back_populates="project", cascade="all, delete"
    )
