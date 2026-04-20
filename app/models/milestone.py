from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin
import datetime

class Milestone(Base, IntegerPrimaryKeyMixin, TimestampMixin, TenantMixin):
    __tablename__ = "milestones"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    target_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, in_progress, completed, delayed
    progress_percentage = Column(Float, nullable=False, default=0.0)

    project = relationship("Project", backref="milestones")
