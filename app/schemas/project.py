from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    budget: float = 0.0
    expenditure: float = 0.0
    revenue: float = 0.0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_score: float = 0.0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    budget: Optional[float] = None
    expenditure: Optional[float] = None
    revenue: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_score: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
