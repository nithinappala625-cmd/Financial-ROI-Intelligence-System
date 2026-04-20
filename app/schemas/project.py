from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date
from typing import Optional


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    budget: float = Field(default=0.0, ge=0.0)
    expenditure: float = Field(default=0.0, ge=0.0)
    revenue: float = Field(default=0.0, ge=0.0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)


class ProjectCreate(ProjectBase):
    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v: Optional[date], info):
        if v and "start_date" in info.data and info.data["start_date"]:
            if v < info.data["start_date"]:
                raise ValueError("end_date must be after start_date")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    budget: Optional[float] = Field(None, ge=0.0)
    expenditure: Optional[float] = Field(None, ge=0.0)
    revenue: Optional[float] = Field(None, ge=0.0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)


class ProjectResponse(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
