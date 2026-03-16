from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.services.alert_service import (
    create_alert,
    get_alert,
    list_active_alerts,
    resolve_alert,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=Sequence[AlertResponse])
async def read_active_alerts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_active_alerts(db, skip=skip, limit=limit)


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
async def mark_alert_resolved(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.finance_manager)),
):
    return await resolve_alert(db, alert_id)


@router.get("/config")
async def get_alert_config(current_user: User = Depends(get_current_user)):
    # Placeholder for alert config extraction
    return {"status": "success", "thresholds": "default"}


@router.put("/config")
async def update_alert_config(
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    # Placeholder for alert updates
    return {"status": "updated", "thresholds": "updated"}
