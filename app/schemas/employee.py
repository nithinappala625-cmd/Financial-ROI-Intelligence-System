from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class EmployeeBase(BaseModel):
    name: str
    role: str  # Could be linked to an enum later
    salary: float = 0.0
    department: Optional[str] = None
    hire_date: Optional[date] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    salary: Optional[float] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    evs_score: Optional[float] = None
    productivity_score: Optional[float] = None
    is_underperforming: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    evs_score: Optional[float] = 0.0
    productivity_score: Optional[float] = 0.0
    is_underperforming: bool = False

    model_config = ConfigDict(from_attributes=True)
