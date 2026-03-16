from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.project_assignment import ProjectAssignment
from app.schemas.project_assignment import (
    ProjectAssignmentCreate,
    ProjectAssignmentUpdate,
)
from app.repositories.project_assignment_repo import project_assignment_repo
from app.core.exceptions import NotFoundError


async def assign_employee_to_project(
    db: AsyncSession, assignment_in: ProjectAssignmentCreate
) -> ProjectAssignment:
    return await project_assignment_repo.create(db, data=assignment_in.model_dump())


async def get_project_assignment(
    db: AsyncSession, assignment_id: int
) -> ProjectAssignment:
    assignment = await project_assignment_repo.get(db, id=assignment_id)
    if not assignment:
        raise NotFoundError("Project assignment not found")
    return assignment


async def list_project_assignments(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[ProjectAssignment]:
    return await project_assignment_repo.list(db, skip=skip, limit=limit)


async def update_project_assignment(
    db: AsyncSession, assignment_id: int, assignment_in: ProjectAssignmentUpdate
) -> ProjectAssignment:
    db_obj = await get_project_assignment(db, assignment_id)
    update_data = assignment_in.model_dump(exclude_unset=True)
    return await project_assignment_repo.update(
        db, db_obj=db_obj, update_data=update_data
    )


async def delete_project_assignment(db: AsyncSession, assignment_id: int) -> bool:
    success = await project_assignment_repo.delete(db, id=assignment_id)
    if not success:
        raise NotFoundError("Project assignment not found")
    return success
