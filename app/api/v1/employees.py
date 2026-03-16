from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import (
    create_employee,
    get_employee,
    list_employees,
    update_employee,
    delete_employee,
    calculate_evs,
    compute_employee_metrics,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_new_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await create_employee(db, employee_in)


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def read_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_employee(db, employee_id)


@router.get("/{employee_id}/value-score")
async def read_employee_evs(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Employee Value Score (EVS) and productivity metrics"""
    emp = await compute_employee_metrics(db, employee_id)
    return {
        "employee_id": employee_id, 
        "current_evs": emp.evs_score, 
        "productivity_score": emp.productivity_score,
        "is_underperforming": emp.is_underperforming,
        "history": []
    }


@router.get("/", response_model=Sequence[EmployeeResponse])
async def read_all_employees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_employees(db, skip=skip, limit=limit)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_existing_employee(
    employee_id: int,
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    return await update_employee(db, employee_id, employee_in)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    await delete_employee(db, employee_id)
