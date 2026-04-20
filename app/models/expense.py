from typing import TYPE_CHECKING
from sqlalchemy import Float, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Expense(Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "expenses"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    flagged_anomaly: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="expenses")
