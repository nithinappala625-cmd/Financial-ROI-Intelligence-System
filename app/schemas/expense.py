from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class ExpenseBase(BaseModel):
    project_id: int
    category: str
    amount: float = 0.0
    date: Optional[date] = None
    flagged_anomaly: bool = False
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    flagged_anomaly: Optional[bool] = None
    notes: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
