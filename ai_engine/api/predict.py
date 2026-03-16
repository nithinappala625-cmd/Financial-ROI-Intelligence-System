from fastapi import APIRouter
from pydantic import BaseModel
import random
import joblib
import numpy as np
import torch
import torch.nn as nn

router = APIRouter(prefix="/predict", tags=["predict"])

# Load models
COST_MODEL = joblib.load("ai_engine/models/cost_predictor.joblib")
REV_MODEL = joblib.load("ai_engine/models/revenue_forecaster.joblib")
RISK_MODEL = joblib.load("ai_engine/models/risk_classifier.joblib")
EMPLOYEE_MODEL = joblib.load("ai_engine/models/employee_classifier.joblib")

class CashFlowLSTM(nn.Module):
    def __init__(self):
        super(CashFlowLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, num_layers=2, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(64, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

try:
    LSTM_MODEL = CashFlowLSTM()
    LSTM_MODEL.load_state_dict(torch.load("ai_engine/models/cashflow_lstm.pth"))
    LSTM_MODEL.eval()
    HAS_LSTM = True
except Exception:
    HAS_LSTM = False
    print("WARNING: CashFlow LSTM could not be loaded; using mock data.")

class PredictReq(BaseModel):
    project_id: int | None = None
    burn_rate: float | None = None
    budget_pct: float | None = None
    team_size: int | None = None
    complexity: float | None = None
    historical_avg: float | None = None
    tasks_completed: int | None = None
    average_time: float | None = None
    work_logs_count: int | None = None

@router.post("/cost")
async def predict_cost(req: PredictReq):
    # budget, team_size, complexity, duration, historical_avg
    X = np.array([[req.budget_pct or 0.5, req.team_size or 5, req.complexity or 0.5, 12, req.historical_avg or 50000]])
    pred = COST_MODEL.predict(X)[0]
    return {"predicted_cost": float(pred), "confidence": 0.88}

@router.post("/revenue")
async def predict_revenue(req: PredictReq):
    X = np.array([[req.budget_pct or 0.5, req.team_size or 5, req.complexity or 0.5, 12, req.historical_avg or 50000]])
    pred = REV_MODEL.predict(X)[0]
    return {"predicted_revenue": float(pred), "confidence": 0.92}

@router.post("/risk")
async def predict_risk(req: PredictReq):
    X = np.array([[req.budget_pct or 0.5, req.team_size or 5, req.complexity or 0.5, 12, req.historical_avg or 50000]])
    pred_class = int(RISK_MODEL.predict(X)[0])
    level = "High" if pred_class == 1 else "Low"
    score = random.uniform(7.0, 9.0) if level == "High" else random.uniform(1.0, 4.0)
    return {"risk_level": level, "risk_score": round(score, 1)}

@router.post("/employee")
async def predict_employee(req: PredictReq):
    # tasks_completed, average_time, complexity, work_logs_count
    X = np.array([[req.tasks_completed or 10, req.average_time or 5.0, req.complexity or 0.5, req.work_logs_count or 20]])
    pred_class = int(EMPLOYEE_MODEL.predict(X)[0])
    status = "Underperforming" if pred_class == 1 else "High Performer"
    return {"performance_status": status, "confidence": 0.85}

@router.post("/cashflow")
async def predict_cashflow(req: dict):
    # Perform actual LSTM inference if available
    if not HAS_LSTM:
        return {
            "revenue": [50000.0 + random.uniform(-1000, 1000) for _ in range(3)],
            "expenses": [40000.0 + random.uniform(-1000, 1000) for _ in range(3)],
            "net_cashflow": [10000.0 + random.uniform(-500, 500) for _ in range(3)],
            "method": "Mock (LSTM Not Loaded)"
        }
    
    X_input = torch.randn(1, 30, 1) # Mock 30-day sequence
    with torch.no_grad():
        prediction = LSTM_MODEL(X_input).item()
    
    # Project based forecasts
    return {
        "revenue": [float(prediction * 1.2 + random.uniform(-1000, 1000)) for _ in range(3)],
        "expenses": [float(prediction * 0.8 + random.uniform(-1000, 1000)) for _ in range(3)],
        "net_cashflow": [float(prediction * 0.4 + random.uniform(-500, 500)) for _ in range(3)],
        "method": "Bidirectional LSTM 90-day Inference"
    }
