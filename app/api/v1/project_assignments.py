from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.project_assignment import (
    ProjectAssignmentCreate,
    ProjectAssignmentResponse,
    ProjectAssignmentUpdate,
)
from app.services.project_assignment_service import (
    assign_employee_to_project,
    get_project_assignment,
    list_project_assignments,
    update_project_assignment,
    delete_project_assignment,
)

router = APIRouter(prefix="/project-assignments", tags=["project_assignments"])


@router.get("/", response_model=Sequence[ProjectAssignmentResponse])
async def read_project_assignments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_project_assignments(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=ProjectAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_assignment(
    assignment_in: ProjectAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await assign_employee_to_project(db, assignment_in)


@router.get("/{assignment_id}", response_model=ProjectAssignmentResponse)
async def read_project_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_project_assignment(db, assignment_id)


@router.put("/{assignment_id}", response_model=ProjectAssignmentResponse)
async def update_existing_project_assignment(
    assignment_id: int,
    assignment_in: ProjectAssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await update_project_assignment(db, assignment_id, assignment_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    await delete_project_assignment(db, assignment_id)
