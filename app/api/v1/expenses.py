from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, RoleEnum
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.expense_service import (
    add_expense,
    get_expense,
    list_expenses,
    update_expense,
    delete_expense,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_model=Sequence[ExpenseResponse])
async def read_expenses(
    project_id: int | None = Query(None, description="Filter by project ID"),
    category: str | None = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List categorized expenses with filters, perfectly matching Section 8 API Design"""
    return await list_expenses(
        db, project_id=project_id, category=category, skip=skip, limit=limit
    )


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_new_expense(
    expense_in: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await add_expense(db, expense_in)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def read_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_expense(db, expense_id)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin)),
):
    await delete_expense(db, expense_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_existing_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_expense(db, expense_id, expense_in)
