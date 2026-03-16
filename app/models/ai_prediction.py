from typing import TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project


class AIPrediction(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_predictions"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    generated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project", back_populates="ai_predictions"
    )
