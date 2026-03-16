from app.repositories.base_repo import BaseRepo
from app.models.employee import Employee


class EmployeeRepo(BaseRepo[Employee]):
    """Employee repository basic entity mapping."""

    def __init__(self):
        super().__init__(Employee)


employee_repo = EmployeeRepo()
