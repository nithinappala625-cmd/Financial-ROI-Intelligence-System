"""
F014: Model Training Pipeline — train_cost.py
XGBoost ProjectCostPredictor training with model versioning and rollback.
Weekly retrain via cron; R2 > 0.82 target.
"""

import os
import json
import shutil
import logging
import datetime
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
VERSION_DIR = os.path.join(MODEL_DIR, "versions")
METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.json")


def _ensure_dirs():
    os.makedirs(VERSION_DIR, exist_ok=True)


def _load_metadata() -> dict:
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {"models": {}}


def _save_metadata(metadata: dict):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2, default=str)


def _version_model(model_name: str, metrics: dict):
    """Save a versioned copy of the current model with metadata."""
    _ensure_dirs()
    metadata = _load_metadata()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    version_id = f"{model_name}_v{timestamp}"

    src = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    dst = os.path.join(VERSION_DIR, f"{version_id}.joblib")

    if os.path.exists(src):
        shutil.copy2(src, dst)

    if model_name not in metadata["models"]:
        metadata["models"][model_name] = {"versions": [], "current_version": None}

    version_entry = {
        "version_id": version_id,
        "timestamp": timestamp,
        "metrics": metrics,
        "path": dst,
    }

    metadata["models"][model_name]["versions"].append(version_entry)
    metadata["models"][model_name]["current_version"] = version_id
    _save_metadata(metadata)

    logger.info(f"Model {model_name} versioned as {version_id}")
    return version_id


def rollback_model(model_name: str, version_id: str) -> bool:
    """Rollback a model to a previous version."""
    metadata = _load_metadata()

    if model_name not in metadata["models"]:
        logger.error(f"Model {model_name} not found in metadata")
        return False

    versions = metadata["models"][model_name]["versions"]
    target = next((v for v in versions if v["version_id"] == version_id), None)

    if not target:
        logger.error(f"Version {version_id} not found")
        return False

    src = target["path"]
    dst = os.path.join(MODEL_DIR, f"{model_name}.joblib")

    if os.path.exists(src):
        shutil.copy2(src, dst)
        metadata["models"][model_name]["current_version"] = version_id
        _save_metadata(metadata)
        logger.info(f"Model {model_name} rolled back to {version_id}")
        return True

    return False


def generate_synthetic_cost_data(n_samples: int = 500) -> tuple:
    """Generate realistic synthetic training data for cost prediction."""
    np.random.seed(42)

    burn_rate = np.random.uniform(0.01, 0.15, n_samples)
    budget_pct = np.random.uniform(0.1, 1.0, n_samples)
    team_size = np.random.randint(2, 50, n_samples).astype(float)
    complexity = np.random.uniform(0.1, 1.0, n_samples)
    duration_months = np.random.randint(1, 24, n_samples).astype(float)

    # Cost formula with realistic relationships
    base_cost = team_size * 8000 * duration_months
    complexity_factor = 1 + complexity * 0.5
    burn_factor = 1 + burn_rate * 2
    noise = np.random.normal(0, 5000, n_samples)

    y = base_cost * complexity_factor * burn_factor * budget_pct + noise
    y = np.maximum(y, 1000)  # Floor at $1k

    X = np.column_stack([burn_rate, budget_pct, team_size, complexity, duration_months])
    feature_names = ["burn_rate", "budget_pct", "team_size", "complexity", "duration_months"]

    return X, y, feature_names


def train_cost_predictor(
    X: np.ndarray = None,
    y: np.ndarray = None,
    tenant_id: int = None,
    n_estimators: int = 200,
    learning_rate: float = 0.05,
    max_depth: int = 6,
) -> dict:
    """
    Train the ProjectCostPredictor XGBoost model.
    Supports per-tenant fine-tuning when tenant_id is provided.
    Returns training metrics dict.
    """
    logger.info("Training ProjectCostPredictor (XGBoost)...")

    if X is None or y is None:
        X, y, _ = generate_synthetic_cost_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")

    metrics = {
        "r2_score": round(float(r2), 4),
        "mae": round(float(mae), 2),
        "rmse": round(float(rmse), 2),
        "cv_r2_mean": round(float(cv_scores.mean()), 4),
        "cv_r2_std": round(float(cv_scores.std()), 4),
        "n_samples": len(X),
        "trained_at": str(datetime.datetime.now()),
    }

    # Save model
    suffix = f"_{tenant_id}" if tenant_id else ""
    model_name = f"cost_predictor{suffix}"
    model_path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    joblib.dump(model, model_path)

    # Version tracking
    _version_model(model_name, metrics)

    logger.info(f"Cost Predictor trained — R2={r2:.4f}, MAE={mae:.2f}, RMSE={rmse:.2f}")

    if r2 < 0.82:
        logger.warning(f"R2 score {r2:.4f} below target 0.82!")

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    metrics = train_cost_predictor()
    print(f"\nTraining complete: {json.dumps(metrics, indent=2)}")
