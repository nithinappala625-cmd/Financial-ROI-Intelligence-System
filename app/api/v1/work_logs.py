from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.work_log import WorkLogCreate, WorkLogResponse, WorkLogUpdate
from app.services.work_log_service import (
    submit_work_log,
    get_work_log,
    list_work_logs,
    update_work_log,
    delete_work_log,
)

router = APIRouter(prefix="/work-logs", tags=["work-logs"])


@router.get("/", response_model=Sequence[WorkLogResponse])
async def read_all_work_logs(
    employee_id: int | None = None,
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Base functionality according to endpoint matching standard parameters filtering
    return await list_work_logs(
        db, employee_id=employee_id, project_id=project_id, skip=skip, limit=limit
    )


@router.post("/", response_model=WorkLogResponse, status_code=status.HTTP_201_CREATED)
async def create_new_work_log(
    work_log_in: WorkLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await submit_work_log(db, work_log_in)


@router.get("/{work_log_id}", response_model=WorkLogResponse)
async def read_work_log(
    work_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_work_log(db, work_log_id)


@router.put("/{work_log_id}", response_model=WorkLogResponse)
async def update_existing_work_log(
    work_log_id: int,
    work_log_in: WorkLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_work_log(db, work_log_id, work_log_in)


@router.delete("/{work_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_work_log(
    work_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    await delete_work_log(db, work_log_id)
