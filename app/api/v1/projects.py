from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import (
    create_project,
    get_project,
    list_projects,
    update_project,
    delete_project,
    calculate_roi,
)

router = APIRouter(prefix="/projects", tags=["projects"])


from app.schemas.common import PaginatedResponse
from app.utils.pagination import paginate
from sqlalchemy import select


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def read_all_projects(
    page: int = 1,
    size: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.project import Project

    query = select(Project)
    return await paginate(db, query, page, size)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await create_project(db, project_in)


@router.get("/{project_id}/roi")
async def get_project_roi(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Retrieve project metrics and calculate ROI
    project = await get_project(db, project_id)
    roi_value = await calculate_roi(
        revenue=project.revenue, total_cost=project.expenditure
    )
    return {
        "project_id": project.id,
        "actual_roi": roi_value,
        "predicted_roi": 0.0,  # Will be fetched via AI module integration separately
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await update_project(db, project_id, project_in)
