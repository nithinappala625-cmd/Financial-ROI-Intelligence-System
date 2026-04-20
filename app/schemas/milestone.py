from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime

class MilestoneBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_date: date
    status: str = "pending"
    progress_percentage: float = 0.0
    project_id: int

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[date] = None
    completion_date: Optional[date] = None
    status: Optional[str] = None
    progress_percentage: Optional[float] = None

class MilestoneResponse(MilestoneBase):
    id: int
    completion_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    tenant_id: int

    model_config = ConfigDict(from_attributes=True)
