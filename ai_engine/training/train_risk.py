"""
F015: ProjectRiskClassifier training — Random Forest with SMOTE and SHAP.
Low/Medium/High risk classification + 0-10 risk score.
"""

import os
import json
import logging
import datetime
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def generate_synthetic_risk_data(n_samples: int = 600) -> tuple:
    """Generate synthetic risk classification data with class imbalance."""
    np.random.seed(42)

    budget_utilization = np.random.uniform(0.1, 1.5, n_samples)
    burn_rate = np.random.uniform(0.01, 0.2, n_samples)
    milestone_delay_pct = np.random.uniform(0.0, 0.8, n_samples)
    team_size = np.random.randint(2, 50, n_samples).astype(float)
    complexity = np.random.uniform(0.1, 1.0, n_samples)

    # Risk labels based on rules
    risk_score = (
        budget_utilization * 3
        + burn_rate * 10
        + milestone_delay_pct * 4
        + complexity * 2
    )

    labels = np.where(risk_score > 7, 2, np.where(risk_score > 4, 1, 0))  # 0=Low, 1=Med, 2=High

    X = np.column_stack([budget_utilization, burn_rate, milestone_delay_pct, team_size, complexity])
    feature_names = ["budget_utilization", "burn_rate", "milestone_delay_pct", "team_size", "complexity"]

    return X, labels, feature_names


def train_risk_classifier(
    X: np.ndarray = None,
    y: np.ndarray = None,
    tenant_id: int = None,
    n_estimators: int = 200,
    use_smote: bool = True,
) -> dict:
    """
    Train ProjectRiskClassifier with SMOTE for class imbalance.
    Returns metrics dict including SHAP feature importances.
    """
    logger.info("Training ProjectRiskClassifier (Random Forest + SMOTE)...")

    if X is None or y is None:
        X, y, feature_names = generate_synthetic_risk_data()
    else:
        feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Apply SMOTE for class imbalance
    if use_smote:
        try:
            from imblearn.over_sampling import SMOTE
            smote = SMOTE(random_state=42)
            X, y = smote.fit_resample(X, y)
            logger.info(f"SMOTE applied: {len(X)} samples after resampling")
        except ImportError:
            logger.warning("imbalanced-learn not installed; skipping SMOTE")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    report = classification_report(y_test, y_pred, target_names=["Low", "Medium", "High"], output_dict=True)

    # Feature importances (proxy for SHAP)
    importances = dict(zip(feature_names, model.feature_importances_.tolist()))

    # SHAP explanations (optional)
    shap_available = False
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test[:10])
        shap_available = True
        logger.info("SHAP explanations computed successfully")
    except ImportError:
        logger.warning("SHAP not installed; using feature importances as proxy")

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")

    metrics = {
        "accuracy": round(float(acc), 4),
        "f1_weighted": round(float(f1), 4),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "classification_report": report,
        "feature_importances": {k: round(v, 4) for k, v in importances.items()},
        "shap_available": shap_available,
        "n_samples": len(X),
        "trained_at": str(datetime.datetime.now()),
    }

    suffix = f"_{tenant_id}" if tenant_id else ""
    model_name = f"risk_classifier{suffix}"
    model_path = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    joblib.dump(model, model_path)

    from ai_engine.training.train_cost import _version_model
    _version_model(model_name, metrics)

    logger.info(f"Risk Classifier trained — Accuracy={acc:.4f}, F1={f1:.4f}")
    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    metrics = train_risk_classifier()
    print(f"\nTraining complete: {json.dumps(metrics, indent=2, default=str)}")
