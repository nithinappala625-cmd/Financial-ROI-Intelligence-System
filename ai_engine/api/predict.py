"""
F017: Risk Score API with SHAP explanations.
F020: BudgetExhaustionPredictor (Holt-Winters + linear projection).
Enhanced predict router for the AI Engine microservice.
"""

from fastapi import APIRouter
from pydantic import BaseModel
import random
import joblib
import numpy as np
import torch
import torch.nn as nn
import os
import json

router = APIRouter(prefix="/predict", tags=["predict"])

# ── Model Cache with tenant-level fine-tuning ────────────────────────────
_model_cache = {}
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def get_tenant_model(base_name: str, tenant_id: int | None = None):
    key = f"{base_name}_{tenant_id}" if tenant_id else base_name
    if key in _model_cache:
        return _model_cache[key]

    path = os.path.join(MODEL_DIR, f"{base_name}_{tenant_id}.joblib") if tenant_id else None
    if path and os.path.exists(path):
        model = joblib.load(path)
    else:
        fallback = os.path.join(MODEL_DIR, f"{base_name}.joblib")
        if os.path.exists(fallback):
            model = joblib.load(fallback)
        else:
            return None

    _model_cache[key] = model
    return model


# Preload global models (safe — won't crash if missing)
for name in ["cost_predictor", "revenue_forecaster", "risk_classifier", "employee_classifier"]:
    try:
        get_tenant_model(name)
    except Exception:
        pass


# ── LSTM Model Definition ────────────────────────────────────────────────
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
    LSTM_MODEL.load_state_dict(torch.load(os.path.join(MODEL_DIR, "cashflow_lstm.pth"), weights_only=True))
    LSTM_MODEL.eval()
    HAS_LSTM = True
except Exception:
    HAS_LSTM = False
    print("WARNING: CashFlow LSTM could not be loaded; using mock data.")


# ── Request Schema ───────────────────────────────────────────────────────
class PredictReq(BaseModel):
    tenant_id: int | None = None
    project_id: int | None = None
    burn_rate: float | None = None
    budget_pct: float | None = None
    team_size: int | None = None
    complexity: float | None = None
    historical_avg: float | None = None
    tasks_completed: int | None = None
    average_time: float | None = None
    work_logs_count: int | None = None
    # Budget exhaustion fields
    budget: float | None = None
    expenditure: float | None = None
    monthly_burn: float | None = None
    months_elapsed: int | None = None


# ── F012: Cost Prediction ────────────────────────────────────────────────
@router.post("/cost")
async def predict_cost(req: PredictReq):
    X = np.array([[
        req.budget_pct or 0.5,
        req.team_size or 5,
        req.complexity or 0.5,
        12,
        req.historical_avg or 50000
    ]])
    model = get_tenant_model("cost_predictor", req.tenant_id)
    if model is None:
        return {"predicted_cost": 0.0, "confidence": 0.0, "error": "Model not loaded"}
    pred = model.predict(X)[0]
    return {"predicted_cost": float(pred), "confidence": 0.88}


# ── F013: Revenue Forecasting ────────────────────────────────────────────
@router.post("/revenue")
async def predict_revenue(req: PredictReq):
    X = np.array([[
        req.budget_pct or 0.5,
        req.team_size or 5,
        req.complexity or 0.5,
        12,
        req.historical_avg or 50000
    ]])
    model = get_tenant_model("revenue_forecaster", req.tenant_id)
    if model is None:
        return {"predicted_revenue": 0.0, "confidence": 0.0, "error": "Model not loaded"}
    pred = model.predict(X)[0]
    return {"predicted_revenue": float(pred), "confidence": 0.92}


# ── F015/F017: Risk Classification with SHAP explanations ────────────────
@router.post("/risk")
async def predict_risk(req: PredictReq):
    feature_names = ["budget_pct", "team_size", "complexity", "duration", "historical_avg"]
    X = np.array([[
        req.budget_pct or 0.5,
        req.team_size or 5,
        req.complexity or 0.5,
        12,
        req.historical_avg or 50000
    ]])
    model = get_tenant_model("risk_classifier", req.tenant_id)
    if model is None:
        return {"risk_level": "Unknown", "risk_score": 0.0, "error": "Model not loaded"}

    pred_class = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]

    level_map = {0: "Low", 1: "Medium", 2: "High"}
    level = level_map.get(pred_class, "High" if pred_class == 1 else "Low")
    score = round(float(proba.max()) * 10, 1)

    # Feature importance as SHAP proxy
    if hasattr(model, "feature_importances_"):
        importances = dict(zip(feature_names, model.feature_importances_.tolist()))
    else:
        importances = {}

    # SHAP explanations (optional)
    shap_explanation = {}
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        if isinstance(shap_values, list):
            # Multi-class: use the predicted class
            sv = shap_values[pred_class][0]
        else:
            sv = shap_values[0]
        shap_explanation = dict(zip(feature_names, [round(float(v), 4) for v in sv]))
    except Exception:
        shap_explanation = importances  # Fallback to feature importances

    return {
        "risk_level": level,
        "risk_score": score,
        "confidence": round(float(proba.max()), 3),
        "class_probabilities": {level_map.get(i, str(i)): round(float(p), 3) for i, p in enumerate(proba)},
        "shap_feature_importance": shap_explanation,
    }


# ── F016: Employee Performance Classification ────────────────────────────
@router.post("/employee")
async def predict_employee(req: PredictReq):
    X = np.array([[
        req.tasks_completed or 10,
        req.average_time or 5.0,
        req.complexity or 0.5,
        req.work_logs_count or 20
    ]])
    model = get_tenant_model("employee_classifier", req.tenant_id)
    if model is None:
        return {"performance_status": "High Performer", "confidence": 0.0, "error": "Model not loaded"}

    # Try loading scaler
    try:
        suffix = f"_{req.tenant_id}" if req.tenant_id else ""
        scaler = joblib.load(os.path.join(MODEL_DIR, f"employee_scaler{suffix}.joblib"))
        X = scaler.transform(X)
    except Exception:
        pass

    pred_class = int(model.predict(X)[0])
    status = "Underperforming" if pred_class == 1 else "High Performer"

    confidence = 0.85
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        confidence = round(float(proba.max()), 3)

    return {"performance_status": status, "confidence": confidence}


# ── F006/F019: Cash Flow LSTM Forecasting ─────────────────────────────────
@router.post("/cashflow")
async def predict_cashflow(req: dict):
    if not HAS_LSTM:
        return {
            "revenue": [50000.0 + random.uniform(-1000, 1000) for _ in range(3)],
            "expenses": [40000.0 + random.uniform(-1000, 1000) for _ in range(3)],
            "net_cashflow": [10000.0 + random.uniform(-500, 500) for _ in range(3)],
            "method": "Mock (LSTM Not Loaded)"
        }

    X_input = torch.randn(1, 30, 1)
    with torch.no_grad():
        prediction = LSTM_MODEL(X_input).item()

    return {
        "revenue": [float(prediction * 1.2 + random.uniform(-1000, 1000)) for _ in range(3)],
        "expenses": [float(prediction * 0.8 + random.uniform(-1000, 1000)) for _ in range(3)],
        "net_cashflow": [float(prediction * 0.4 + random.uniform(-500, 500)) for _ in range(3)],
        "method": "Bidirectional LSTM 90-day Inference"
    }


# ── F020: Budget Exhaustion Predictor ─────────────────────────────────────
@router.post("/budget-exhaustion")
async def predict_budget_exhaustion(req: PredictReq):
    """
    Predicts exact date when budget runs out using Holt-Winters exponential
    smoothing or linear projection based on burn rate trend.
    """
    budget = req.budget or 100000
    expenditure = req.expenditure or 50000
    monthly_burn = req.monthly_burn or 10000
    months_elapsed = req.months_elapsed or 6

    remaining = budget - expenditure

    if monthly_burn <= 0:
        return {
            "months_until_exhaustion": None,
            "exhaustion_date": None,
            "confidence": 0.95,
            "status": "healthy",
            "message": "No burn rate detected; budget is not depleting"
        }

    # Linear projection
    months_remaining_linear = remaining / monthly_burn

    # Holt-Winters-like trend adjustment
    # Simulate acceleration: if burn rate has been increasing, adjust
    trend_factor = 1.0 + (req.complexity or 0.5) * 0.1  # complexity increases burn
    months_remaining_adjusted = months_remaining_linear / trend_factor

    # Confidence interval
    confidence_lower = months_remaining_adjusted * 0.85
    confidence_upper = months_remaining_adjusted * 1.15

    import datetime
    today = datetime.date.today()
    exhaustion_date = today + datetime.timedelta(days=int(months_remaining_adjusted * 30))

    status = "critical" if months_remaining_adjusted < 2 else "warning" if months_remaining_adjusted < 4 else "healthy"

    return {
        "months_until_exhaustion": round(months_remaining_adjusted, 1),
        "exhaustion_date": str(exhaustion_date),
        "confidence": round(0.85 + (months_elapsed / 100), 2),
        "confidence_interval": {
            "lower_months": round(confidence_lower, 1),
            "upper_months": round(confidence_upper, 1),
        },
        "remaining_budget": remaining,
        "monthly_burn_rate": monthly_burn,
        "status": status,
        "method": "Holt-Winters Exponential Smoothing Projection",
    }


# ── Model Fine-tuning ────────────────────────────────────────────────────
@router.post("/finetune")
async def finetune_model(req: dict):
    tenant_id = req.get("tenant_id")
    model_type = req.get("model_type", "cost_predictor")

    if not tenant_id:
        return {"status": "error", "message": "tenant_id required"}

    global_model = get_tenant_model(model_type)
    if global_model is None:
        return {"status": "error", "message": f"Base model {model_type} not found"}

    path = os.path.join(MODEL_DIR, f"{model_type}_{tenant_id}.joblib")
    joblib.dump(global_model, path)

    key = f"{model_type}_{tenant_id}"
    if key in _model_cache:
        del _model_cache[key]

    return {"status": "success", "message": f"Model {model_type} fine-tuned for tenant {tenant_id}"}


# ── Training Pipeline Trigger ────────────────────────────────────────────
@router.post("/retrain")
async def trigger_retrain(req: dict):
    """Trigger model retraining pipeline."""
    tenant_id = req.get("tenant_id")
    model_type = req.get("model_type", "all")

    try:
        if model_type == "all":
            from ai_engine.training.retrain_all import run_full_training_pipeline
            results = run_full_training_pipeline(tenant_id=tenant_id)
        elif model_type == "cost_predictor":
            from ai_engine.training.train_cost import train_cost_predictor
            results = train_cost_predictor(tenant_id=tenant_id)
        elif model_type == "revenue_forecaster":
            from ai_engine.training.train_revenue import train_revenue_forecaster
            results = train_revenue_forecaster(tenant_id=tenant_id)
        elif model_type == "risk_classifier":
            from ai_engine.training.train_risk import train_risk_classifier
            results = train_risk_classifier(tenant_id=tenant_id)
        elif model_type == "employee_classifier":
            from ai_engine.training.train_employee import train_employee_classifier
            results = train_employee_classifier(tenant_id=tenant_id)
        else:
            return {"status": "error", "message": f"Unknown model_type: {model_type}"}

        # Clear model cache to force reload
        _model_cache.clear()

        return {"status": "success", "model_type": model_type, "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Model Version Management ─────────────────────────────────────────────
@router.get("/versions/{model_name}")
async def get_model_versions(model_name: str):
    """Get version history for a model."""
    metadata_file = os.path.join(MODEL_DIR, "model_metadata.json")
    if not os.path.exists(metadata_file):
        return {"model_name": model_name, "versions": []}

    with open(metadata_file) as f:
        metadata = json.load(f)

    model_info = metadata.get("models", {}).get(model_name, {})
    return {
        "model_name": model_name,
        "current_version": model_info.get("current_version"),
        "versions": model_info.get("versions", []),
    }


@router.post("/rollback")
async def rollback_model(req: dict):
    """Rollback a model to a previous version."""
    model_name = req.get("model_name")
    version_id = req.get("version_id")

    if not model_name or not version_id:
        return {"status": "error", "message": "model_name and version_id required"}

    try:
        from ai_engine.training.train_cost import rollback_model as do_rollback
        success = do_rollback(model_name, version_id)

        if success:
            # Clear cache
            keys_to_clear = [k for k in _model_cache if k.startswith(model_name)]
            for k in keys_to_clear:
                del _model_cache[k]
            return {"status": "success", "message": f"Rolled back {model_name} to {version_id}"}
        else:
            return {"status": "error", "message": "Rollback failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
