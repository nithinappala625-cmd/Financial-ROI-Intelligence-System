from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class AIPredictionBase(BaseModel):
    project_id: int
    model_type: str
    predicted_value: float
    confidence: float = 0.0
    generated_at: Optional[datetime] = None


class AIPredictionCreate(AIPredictionBase):
    pass


class AIPredictionUpdate(BaseModel):
    predicted_value: Optional[float] = None
    confidence: Optional[float] = None


class AIPredictionResponse(AIPredictionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
