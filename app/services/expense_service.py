from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.repositories.expense_repo import expense_repo
from app.core.exceptions import NotFoundError
from app.services.project_service import update_expenditure


async def add_expense(db: AsyncSession, expense_in: ExpenseCreate) -> Expense:
    """According to step 14.4 add_expense checks budget,
    calculates utilization & updates expenditure logic directly!"""

    # Run the transaction mapping
    expense = await expense_repo.create(db, data=expense_in.model_dump())

    # Route logic to project budget updates
    await update_expenditure(
        db, project_id=expense_in.project_id, added_expense=expense_in.amount
    )

    return expense


async def get_expense(db: AsyncSession, expense_id: int) -> Expense:
    expense = await expense_repo.get(db, expense_id)
    if not expense:
        raise NotFoundError("Expense not found")
    return expense


async def list_expenses(
    db: AsyncSession,
    project_id: int | None = None,
    category: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[Expense]:
    return await expense_repo.list_with_filters(
        db, skip=skip, limit=limit, project_id=project_id, category=category
    )


async def update_expense(
    db: AsyncSession, expense_id: int, expense_in: ExpenseUpdate
) -> Expense:
    db_obj = await get_expense(db, expense_id)
    update_data = expense_in.model_dump(exclude_unset=True)
    return await expense_repo.update(db, db_obj=db_obj, update_data=update_data)


async def delete_expense(db: AsyncSession, expense_id: int) -> bool:
    success = await expense_repo.delete(db, id=expense_id)
    if not success:
        raise NotFoundError("Expense not found")
    return success
