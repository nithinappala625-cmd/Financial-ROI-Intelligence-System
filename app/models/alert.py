from typing import TYPE_CHECKING
from sqlalchemy import Float, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin

if TYPE_CHECKING:
    from app.models.project import Project


class Alert(Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "alerts"

    type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    # Generic entity relationships might be stored loosely
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False)

    # created_at is automatically provided by TimestampMixin
