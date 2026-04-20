from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from enum import Enum


class ExpenseCategory(str, Enum):
    SALARIES = "Salaries"
    OPS = "Ops"
    INFRA = "Infra"
    SOFTWARE = "Software"
    MARKETING = "Marketing"
    MISC = "Misc"


class ExpenseBase(BaseModel):
    project_id: int
    category: ExpenseCategory
    amount: float = 0.0
    date: Optional[date] = None
    flagged_anomaly: bool = False
    notes: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: Optional[ExpenseCategory] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    flagged_anomaly: Optional[bool] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
