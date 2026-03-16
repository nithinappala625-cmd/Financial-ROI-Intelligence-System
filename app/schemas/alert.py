from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional


class AlertBase(BaseModel):
    type: str
    severity: str
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None
    message: str
    resolved: bool = False


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    target: Optional[str] = None  # Added based on default update structure
    resolved: Optional[bool] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
