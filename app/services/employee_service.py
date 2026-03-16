from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.repositories.employee_repo import employee_repo
from app.core.exceptions import NotFoundError


async def create_employee(db: AsyncSession, employee_in: EmployeeCreate) -> Employee:
    return await employee_repo.create(db, data=employee_in.model_dump())


async def get_employee(db: AsyncSession, employee_id: int) -> Employee:
    emp = await employee_repo.get(db, employee_id)
    if not emp:
        raise NotFoundError("Employee not found")
    return emp


async def list_employees(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[Employee]:
    return await employee_repo.list(db, skip=skip, limit=limit)


async def update_employee(
    db: AsyncSession, employee_id: int, employee_in: EmployeeUpdate
) -> Employee:
    db_obj = await get_employee(db, employee_id)
    update_data = employee_in.model_dump(exclude_unset=True)
    return await employee_repo.update(db, db_obj=db_obj, update_data=update_data)


async def delete_employee(db: AsyncSession, employee_id: int) -> bool:
    success = await employee_repo.delete(db, id=employee_id)
    if not success:
        raise NotFoundError("Employee not found")
    return success


# Business Logic Rule (per Section 4.3 System Design)
async def calculate_evs(
    project_contribution_value: float, salary_cost: float
) -> float:
    """EVS = Project Contribution Financial Value / Salary Cost"""
    if salary_cost <= 0:
        return 0.0
    return project_contribution_value / salary_cost


async def flag_underperformers(evs_score: float) -> bool:
    """Flag employee if EVS consistently low (< 1.0 indicates less value generated vs cost)"""
    if evs_score < 1.0:
        return True
    return False

async def compute_employee_metrics(db: AsyncSession, employee_id: int) -> Employee:
    emp = await get_employee(db, employee_id)
    
    from app.services.work_log_service import list_work_logs
    work_logs = await list_work_logs(db, employee_id=employee_id, limit=1000)
    
    total_contribution = sum(wl.contribution_value for wl in work_logs)
    salary_cost = float(emp.salary)
    
    evs_score = await calculate_evs(total_contribution, salary_cost)
    
    tasks_completed = len(work_logs)
    average_time = sum(wl.hours for wl in work_logs) / tasks_completed if tasks_completed > 0 else 0.0
    complexity = 0.5 
    work_logs_count = tasks_completed
    
    from app.services.ai_service import evaluate_employee_performance
    ai_metrics = await evaluate_employee_performance(
        db, 
        tasks_completed=tasks_completed, 
        average_time=average_time,
        complexity=complexity,
        work_logs_count=work_logs_count
    )
    
    is_underperforming = ai_metrics.get("performance_status") == "Underperforming"
    productivity_score = tasks_completed * 10.0 + total_contribution * 0.1
    
    update_data = EmployeeUpdate(
        evs_score=evs_score,
        productivity_score=productivity_score,
        is_underperforming=is_underperforming
    )
    
    updated_emp = await update_employee(db, employee_id, update_data)
    return updated_emp

