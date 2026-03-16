from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class WorkLogBase(BaseModel):
    employee_id: int
    project_id: int
    hours: float = 0.0
    task_description: Optional[str] = None
    date: Optional[date] = None
    contribution_value: float = 0.0


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    hours: Optional[float] = None
    task_description: Optional[str] = None
    date: Optional[date] = None
    contribution_value: Optional[float] = None


class WorkLogResponse(WorkLogBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
