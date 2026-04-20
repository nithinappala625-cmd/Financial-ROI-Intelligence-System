from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.milestone import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.services.milestone_service import (
    create_milestone,
    get_milestone,
    list_milestones,
    update_milestone,
    delete_milestone,
)

router = APIRouter(prefix="/milestones", tags=["milestones"])

@router.get("/", response_model=Sequence[MilestoneResponse])
async def read_milestones(
    project_id: int | None = Query(None, description="Filter by project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_milestones(db, project_id=project_id, skip=skip, limit=limit)

@router.post("/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_new_milestone(
    milestone_in: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_milestone(db, milestone_in)

@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def read_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_milestone(db, milestone_id)

@router.put("/{milestone_id}", response_model=MilestoneResponse)
async def update_existing_milestone(
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_milestone(db, milestone_id, milestone_in)

@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    await delete_milestone(db, milestone_id)
