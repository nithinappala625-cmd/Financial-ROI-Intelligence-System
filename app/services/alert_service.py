from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate
from app.repositories.alert_repo import alert_repo
from app.core.exceptions import NotFoundError


async def create_alert(db: AsyncSession, alert_in: AlertCreate) -> Alert:
    return await alert_repo.create(db, data=alert_in.model_dump())


async def get_alert(db: AsyncSession, alert_id: int) -> Alert:
    alert = await alert_repo.get(db, alert_id)
    if not alert:
        raise NotFoundError("Alert not found")
    return alert


async def list_active_alerts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[Alert]:
    # Custom business logic query - would ideally be in alert_repo.list_active
    return await alert_repo.list(db, skip=skip, limit=limit)


async def resolve_alert(db: AsyncSession, alert_id: int) -> Alert:
    db_obj = await get_alert(db, alert_id)
    return await alert_repo.update(db, db_obj=db_obj, update_data={"resolved": True})


# Future Additions as per System Design (Section 11)
async def check_budget_thresholds(db: AsyncSession, project_id: int):
    # Dummy implementation for checking budget thresholds
    pass

async def check_evs_thresholds(db: AsyncSession, employee_id: int):
    # Dummy implementation for checking EVS thresholds 
    pass

async def check_anomaly_thresholds(db: AsyncSession, data_point: dict):
    # Dummy implementation for anomaly detection
    pass

async def check_cash_flow_thresholds(db: AsyncSession, project_id: int):
    # Dummy implementation for checking cash flow dips
    pass

async def check_milestone_thresholds(db: AsyncSession, project_id: int):
    # Dummy implementation for checking milestone delays
    pass

async def dispatch_notification(alert: Alert, channels: list[str] = ["email", "push"]):
    # Dummy implementation for notification dispatching
    pass
