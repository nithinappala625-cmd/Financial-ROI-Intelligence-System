"""
F016: EmployeeUnderperformanceClassifier training.
Logistic Regression; binary At Risk / Not At Risk; EVS trend + blocker features.
"""

import os
import json
import logging
import datetime
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, f1_score, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def generate_synthetic_employee_data(n_samples: int = 500) -> tuple:
    """Generate synthetic employee performance data."""
    np.random.seed(42)

    evs_current = np.random.uniform(0.2, 3.0, n_samples)
    evs_trend_3w = np.random.uniform(-0.5, 0.5, n_samples)  # EVS change over 3 weeks
    hours_worked = np.random.uniform(10, 60, n_samples)
    tasks_completed = np.random.randint(0, 30, n_samples).astype(float)
    blocker_count = np.random.randint(0, 5, n_samples).astype(float)
    avg_task_time = np.random.uniform(1, 20, n_samples)

    # Underperforming: low EVS + negative trend + blockers
    risk_score = (
        (1 - evs_current / 3.0) * 3
        + (-evs_trend_3w) * 2
        + blocker_count * 0.5
        + (1 - tasks_completed / 30.0) * 2
    )
    labels = (risk_score > 3.5).astype(int)  # 1 = At Risk

    X = np.column_stack([evs_current, evs_trend_3w, hours_worked, tasks_completed, blocker_count, avg_task_time])
    feature_names = ["evs_current", "evs_trend_3w", "hours_worked", "tasks_completed", "blocker_count", "avg_task_time"]

    return X, labels, feature_names


def train_employee_classifier(
    X: np.ndarray = None,
    y: np.ndarray = None,
    tenant_id: int = None,
) -> dict:
    """Train EmployeeUnderperformanceClassifier with Logistic Regression."""
    logger.info("Training EmployeeUnderperformanceClassifier (Logistic Regression)...")

    if X is None or y is None:
        X, y, feature_names = generate_synthetic_employee_data()
    else:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, target_names=["Not At Risk", "At Risk"], output_dict=True)

    coefficients = dict(zip(feature_names, model.coef_[0].tolist()))

    cv_scores = cross_val_score(model, scaler.transform(X), y, cv=5, scoring="f1")

    metrics = {
        "accuracy": round(float(acc), 4),
        "f1_score": round(float(f1), 4),
        "auc_roc": round(float(auc), 4),
        "cv_f1_mean": round(float(cv_scores.mean()), 4),
        "classification_report": report,
        "feature_coefficients": {k: round(v, 4) for k, v in coefficients.items()},
        "n_samples": len(X),
        "trained_at": str(datetime.datetime.now()),
    }

    # Save model + scaler
    suffix = f"_{tenant_id}" if tenant_id else ""
    model_name = f"employee_classifier{suffix}"
    model_path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    scaler_path = os.path.join(MODEL_DIR, f"employee_scaler{suffix}.joblib")
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    from ai_engine.training.train_cost import _version_model
    _version_model(model_name, metrics)

    logger.info(f"Employee Classifier trained — Accuracy={acc:.4f}, F1={f1:.4f}, AUC={auc:.4f}")
    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    metrics = train_employee_classifier()
    print(f"\nTraining complete: {json.dumps(metrics, indent=2, default=str)}")
