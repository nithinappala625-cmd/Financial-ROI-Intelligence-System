from app.repositories.base_repo import BaseRepo
from app.models.expense import Expense


class ExpenseRepo(BaseRepo[Expense]):
    """Expense operations implementation class mappings."""

    def __init__(self):
        super().__init__(Expense)


expense_repo = ExpenseRepo()
