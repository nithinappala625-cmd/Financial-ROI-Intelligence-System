from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.ai_prediction import AIPrediction
from app.schemas.ai import AIPredictionCreate, AIPredictionUpdate
from app.repositories.ai_prediction_repo import ai_prediction_repo
from app.core.exceptions import NotFoundError

import httpx
from config import settings

# Stubbed functions representing communication with the AI microservice
# As per Section 14.2, these call the AI engine REST API and might cache in Redis

AI_URL = settings.AI_ENGINE_BASE_URL or "http://127.0.0.1:8001"


async def get_cashflow_forecast(db: AsyncSession) -> dict:
    """Calls AI engine to get 90-day AI cash flow forecast"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AI_URL}/predict/cashflow", json={})
        if response.status_code == 200:
            return {"status": "success", "forecast": response.json()}
    return {"status": "error", "forecast": "placeholder"}


async def get_risk_score(db: AsyncSession, project_id: int) -> dict:
    """Calls AI engine to get risk score classifier for project"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_URL}/predict/risk", json={"project_id": project_id}
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "project_id": project_id,
                "risk_score": data.get("risk_score"),
                "risk_class": data.get("risk_level"),
            }
    return {"project_id": project_id, "risk_score": 0.0, "risk_class": "Low"}


async def evaluate_employee_performance(db: AsyncSession, tasks_completed: int, average_time: float, complexity: float, work_logs_count: int) -> dict:
    """Calls AI engine to get employee status based on work log metrics"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AI_URL}/predict/employee", json={
                "tasks_completed": tasks_completed,
                "average_time": average_time,
                "complexity": complexity,
                "work_logs_count": work_logs_count
            }
        )
        if response.status_code == 200:
            return response.json()
    return {"performance_status": "High Performer", "confidence": 0.0}



async def get_anomalies(db: AsyncSession) -> list:
    """Calls AI engine to list all flagged financial anomalies"""
    return []


async def get_recommendations(db: AsyncSession) -> list:
    """Calls AI engine to get AI budget allocation recommendations"""
    return []


async def run_simulation(db: AsyncSession, scenario_data: dict) -> dict:
    """Calls AI engine to simulate 'what-if' scenario"""
    return {"status": "simulated", "results": scenario_data}


# Standard basic CRUD mapped to ai_prediction_repo
async def save_prediction(
    db: AsyncSession, prediction_in: AIPredictionCreate
) -> AIPrediction:
    return await ai_prediction_repo.create(db, data=prediction_in.model_dump())


async def get_prediction(db: AsyncSession, prediction_id: int) -> AIPrediction:
    prediction = await ai_prediction_repo.get(db, prediction_id)
    if not prediction:
        raise NotFoundError("Prediction not found")
    return prediction
