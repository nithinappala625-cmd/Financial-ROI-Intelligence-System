from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repositories.project_repo import project_repo
from app.core.exceptions import NotFoundError


async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
    return await project_repo.create(db, data=project_in.model_dump())


async def get_project(db: AsyncSession, project_id: int) -> Project:
    project = await project_repo.get(db, project_id)
    if not project:
        raise NotFoundError("Project not found")
    return project


async def list_projects(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[Project]:
    return await project_repo.list(db, skip=skip, limit=limit)


async def update_project(
    db: AsyncSession, project_id: int, project_in: ProjectUpdate
) -> Project:
    db_obj = await get_project(db, project_id)
    update_data = project_in.model_dump(exclude_unset=True)
    return await project_repo.update(db, db_obj=db_obj, update_data=update_data)


async def delete_project(db: AsyncSession, project_id: int) -> bool:
    success = await project_repo.delete(db, id=project_id)
    if not success:
        raise NotFoundError("Project not found")
    return success


# Business Logic Rule (per Section 4.1 System Design)
async def calculate_roi(revenue: float, total_cost: float) -> float:
    """ROI = (Revenue - Total Cost) / Total Cost x 100%"""
    if total_cost <= 0:
        return 0.0
    return ((revenue - total_cost) / total_cost) * 100


async def update_expenditure(
    db: AsyncSession, project_id: int, added_expense: float
) -> Project:
    """Update total aggregate project expenditure upon an expense post"""
    project = await get_project(db, project_id)
    new_expenditure = float(project.expenditure) + added_expense

    # Pass changes to the rep
    return await project_repo.update(
        db, db_obj=project, update_data={"expenditure": new_expenditure}
    )
