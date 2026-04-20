from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.common import PaginatedResponse
from app.utils.pagination import paginate
from app.services.project_service import (
    create_project,
    get_project,
    update_project,
    delete_project,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=PaginatedResponse[ProjectResponse])
async def read_all_projects(
    page: int = 1,
    size: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects with pagination."""
    query = select(Project)
    return await paginate(db, query, page, size)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    """Create a new project - admin only."""
    return await create_project(db, project_in)


@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project_by_id(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific project by ID - accessible by all authenticated users."""
    return await get_project(db, project_id)


@router.get("/{project_id}/roi")
async def get_project_roi(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate and return ROI metrics for a specific project."""
    project = await get_project(db, project_id)
    
    from app.utils.roi_calculator import calc_roi, calc_margin, calc_burn_rate
    import datetime

    roi_value = calc_roi(
        revenue=float(project.revenue), cost=float(project.expenditure)
    )
    margin_value = calc_margin(
        revenue=float(project.revenue), cost=float(project.expenditure)
    )

    months_passed = 1.0
    if project.start_date:
        today = datetime.datetime.now().date()
        # project.start_date is a datetime.date object
        delta = today - project.start_date
        months_passed = max(1.0, delta.days / 30.0)

    burn_rate = calc_burn_rate(
        total_expenses=float(project.expenditure), months_passed=months_passed
    )

    return {
        "project_id": project.id,
        "actual_roi": roi_value,
        "predicted_roi": 0.0,  # Placeholder for future AI integration
        "margin": margin_value,
        "burn_rate": burn_rate,
        "months_passed": months_passed,
        "history": [
            {"date": str(today - datetime.timedelta(days=60)), "roi": roi_value * 0.8},
            {"date": str(today - datetime.timedelta(days=30)), "roi": roi_value * 0.9},
            {"date": str(today), "roi": roi_value},
        ] if project.start_date else []
    }


@router.get("/{project_id}/financial-profile")
async def get_project_financial_profile(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed financial metrics for a specific project."""
    project = await get_project(db, project_id)
    utilization = (
        (project.expenditure / project.budget) * 100 if project.budget > 0 else 0
    )
    return {
        "project_id": project.id,
        "name": project.name,
        "budget": project.budget,
        "expenditure": project.expenditure,
        "revenue": project.revenue,
        "budget_utilization": utilization,
        "risk_score": project.risk_score,
        "dates": {"start": project.start_date, "end": project.end_date},
    }


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_existing_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    """Update project details - admin only."""
    return await update_project(db, project_id, project_in)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    """Delete a project - admin only."""
    await delete_project(db, project_id)
    return None

@router.get("/{project_id}/budget-vs-actual")
async def get_budget_vs_actual(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await get_project(db, project_id)
    utilization = (project.expenditure / project.budget) * 100 if project.budget > 0 else 0
    return {
        "project_id": project.id,
        "budget": project.budget,
        "actual_expenditure": project.expenditure,
        "remaining_budget": project.budget - project.expenditure,
        "utilization_rate": utilization
    }
