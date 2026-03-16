from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.ai import AIPredictionResponse
from app.services.ai_service import (
    get_cashflow_forecast,
    get_risk_score,
    get_anomalies,
    get_recommendations,
    run_simulation,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/forecast/cashflow")
async def cashflow_forecast(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get 90-day AI cash flow forecast"""
    return await get_cashflow_forecast(db)


@router.get("/forecast/budget-exhaustion/{project_id}")
async def budget_exhaustion_forecast(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Simulated endpoint implementation as per 14.2
    return {
        "status": "success",
        "project_id": project_id,
        "exhaustion_prediction": "placeholder",
    }


@router.get("/anomalies")
async def list_flagged_anomalies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.finance_manager)),
):
    """List all flagged financial anomalies"""
    return await get_anomalies(db)


@router.post("/simulate")
async def ai_scenario_simulation(
    scenario_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """'what-if' scenario modeling"""
    return await run_simulation(db, scenario_data)


@router.get("/risk/{project_id}")
async def project_risk(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_risk_score(db, project_id)


@router.get("/recommendations")
async def budget_recommendations(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await get_recommendations(db)
