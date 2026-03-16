from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.work_log import WorkLog
from app.schemas.work_log import WorkLogCreate, WorkLogUpdate
from app.repositories.work_log_repo import work_log_repo
from app.core.exceptions import NotFoundError


async def submit_work_log(db: AsyncSession, work_log_in: WorkLogCreate) -> WorkLog:
    wl = await work_log_repo.create(db, data=work_log_in.model_dump())
    
    from app.services.employee_service import compute_employee_metrics
    await compute_employee_metrics(db, wl.employee_id)
    
    return wl


async def get_work_log(db: AsyncSession, log_id: int) -> WorkLog:
    wl = await work_log_repo.get(db, log_id)
    if not wl:
        raise NotFoundError("Work log not found")
    return wl


async def list_work_logs(
    db: AsyncSession,
    employee_id: int | None = None,
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[WorkLog]:
    return await work_log_repo.list_with_filters(
        db, skip=skip, limit=limit, employee_id=employee_id, project_id=project_id
    )


async def update_work_log(
    db: AsyncSession, log_id: int, log_in: WorkLogUpdate
) -> WorkLog:
    db_obj = await get_work_log(db, log_id)
    update_data = log_in.model_dump(exclude_unset=True)
    wl = await work_log_repo.update(db, db_obj=db_obj, update_data=update_data)
    
    from app.services.employee_service import compute_employee_metrics
    await compute_employee_metrics(db, wl.employee_id)
    
    return wl


async def delete_work_log(db: AsyncSession, log_id: int) -> bool:
    wl = await get_work_log(db, log_id)
    success = await work_log_repo.delete(db, id=log_id)
    if not success:
        raise NotFoundError("Work log not found")
        
    from app.services.employee_service import compute_employee_metrics
    await compute_employee_metrics(db, wl.employee_id)
    return success


# Future addition per System Design: aggregate_hours(), compute_contribution_value()
