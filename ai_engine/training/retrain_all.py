"""
F014: Weekly retrain orchestrator — runs all training pipelines with cron scheduling.
"""

import os
import json
import logging
import datetime

logger = logging.getLogger(__name__)


def run_full_training_pipeline(tenant_id: int = None) -> dict:
    """Execute complete model retraining pipeline."""
    logger.info("=" * 60)
    logger.info("Starting Full Model Training Pipeline")
    logger.info(f"Timestamp: {datetime.datetime.now()}")
    logger.info(f"Tenant: {tenant_id or 'Global'}")
    logger.info("=" * 60)

    results = {}

    # 1. Cost Predictor (XGBoost)
    try:
        from ai_engine.training.train_cost import train_cost_predictor
        results["cost_predictor"] = train_cost_predictor(tenant_id=tenant_id)
        logger.info("✅ Cost Predictor training complete")
    except Exception as e:
        results["cost_predictor"] = {"error": str(e)}
        logger.error(f"❌ Cost Predictor training failed: {e}")

    # 2. Revenue Forecaster (LightGBM)
    try:
        from ai_engine.training.train_revenue import train_revenue_forecaster
        results["revenue_forecaster"] = train_revenue_forecaster(tenant_id=tenant_id)
        logger.info("✅ Revenue Forecaster training complete")
    except Exception as e:
        results["revenue_forecaster"] = {"error": str(e)}
        logger.error(f"❌ Revenue Forecaster training failed: {e}")

    # 3. Risk Classifier (Random Forest + SMOTE)
    try:
        from ai_engine.training.train_risk import train_risk_classifier
        results["risk_classifier"] = train_risk_classifier(tenant_id=tenant_id)
        logger.info("✅ Risk Classifier training complete")
    except Exception as e:
        results["risk_classifier"] = {"error": str(e)}
        logger.error(f"❌ Risk Classifier training failed: {e}")

    # 4. Employee Classifier (Logistic Regression)
    try:
        from ai_engine.training.train_employee import train_employee_classifier
        results["employee_classifier"] = train_employee_classifier(tenant_id=tenant_id)
        logger.info("✅ Employee Classifier training complete")
    except Exception as e:
        results["employee_classifier"] = {"error": str(e)}
        logger.error(f"❌ Employee Classifier training failed: {e}")

    # 5. CashFlow LSTM
    try:
        from ai_engine.training.train_cashflow_lstm import train_cashflow_lstm
        results["cashflow_lstm"] = train_cashflow_lstm(epochs=50)
        logger.info("✅ CashFlow LSTM training complete")
    except Exception as e:
        results["cashflow_lstm"] = {"error": str(e)}
        logger.error(f"❌ CashFlow LSTM training failed: {e}")

    logger.info("=" * 60)
    logger.info("Training Pipeline Complete")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = run_full_training_pipeline()
    print(json.dumps(results, indent=2, default=str))
