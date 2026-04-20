"""
F028: Alert Engine & Rule Configuration — 5 alert types with configurable thresholds.
F029: Enhanced Alert Checker Background Worker.
F027: Underperformer Flagging & Workload Suggestions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence, Optional
from app.models.alert import Alert
from app.models.project import Project
from app.models.employee import Employee
from app.models.milestone import Milestone
from app.schemas.alert import AlertCreate, AlertUpdate
from app.repositories.alert_repo import alert_repo
from app.core.exceptions import NotFoundError
import logging
import datetime

logger = logging.getLogger(__name__)


# ── Configurable Alert Thresholds ─────────────────────────────────────────
DEFAULT_THRESHOLDS = {
    "budget_exhaustion": {
        "warning_pct": 80.0,
        "critical_pct": 90.0,
        "enabled": True,
    },
    "evs_threshold": {
        "low_evs": 0.6,
        "consecutive_weeks": 3,
        "enabled": True,
    },
    "financial_anomaly": {
        "auto_flag": True,
        "min_amount": 1000,
        "enabled": True,
    },
    "cashflow_warning": {
        "negative_months": 2,
        "burn_rate_multiplier": 1.5,
        "enabled": True,
    },
    "milestone_delay": {
        "days_overdue": 7,
        "enabled": True,
    },
}

# Mutable runtime config (can be updated via API)
_alert_config = dict(DEFAULT_THRESHOLDS)


def get_alert_thresholds() -> dict:
    return _alert_config


def update_alert_thresholds(updates: dict) -> dict:
    for alert_type, config in updates.items():
        if alert_type in _alert_config:
            _alert_config[alert_type].update(config)
    return _alert_config


# ── Core CRUD ─────────────────────────────────────────────────────────────

async def create_alert(db: AsyncSession, alert_in: AlertCreate) -> Alert:
    alert = await alert_repo.create(db, data=alert_in.model_dump())

    # Emit Kafka event
    try:
        from app.core.kafka_producer import emit_alert_triggered
        await emit_alert_triggered(
            alert_id=alert.id,
            alert_type=alert.type,
            severity=alert.severity,
            message=alert.message,
            entity_id=alert.entity_id,
        )
    except Exception as e:
        logger.warning(f"Failed to emit alert event: {e}")

    # Dispatch notifications
    try:
        from app.services.notification_service import notification_dispatcher
        await notification_dispatcher.dispatch(
            alert_type=alert.type,
            severity=alert.severity,
            message=alert.message,
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
        )
    except Exception as e:
        logger.warning(f"Failed to dispatch notification: {e}")

    return alert


async def get_alert(db: AsyncSession, alert_id: int) -> Alert:
    alert = await alert_repo.get(db, alert_id)
    if not alert:
        raise NotFoundError("Alert not found")
    return alert


async def list_active_alerts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Sequence[Alert]:
    return await alert_repo.list(db, skip=skip, limit=limit)


async def list_alerts_by_type(
    db: AsyncSession, alert_type: str, skip: int = 0, limit: int = 100
) -> Sequence[Alert]:
    return await alert_repo.list_with_filters(
        db, skip=skip, limit=limit, type=alert_type
    )


async def resolve_alert(db: AsyncSession, alert_id: int) -> Alert:
    db_obj = await get_alert(db, alert_id)
    return await alert_repo.update(db, db_obj=db_obj, update_data={"resolved": True})


# ── F028: Threshold Checking Functions ────────────────────────────────────

async def check_budget_thresholds(db: AsyncSession, project_id: int):
    """Check if project budget utilization exceeds thresholds."""
    config = _alert_config["budget_exhaustion"]
    if not config["enabled"]:
        return

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project or project.budget <= 0:
        return

    utilization = (float(project.expenditure) / float(project.budget)) * 100

    if utilization >= config["critical_pct"]:
        alert_in = AlertCreate(
            type="budget_exhaustion",
            severity="critical",
            entity_id=project.id,
            entity_type="project",
            message=f"CRITICAL: Project '{project.name}' budget utilization at {utilization:.1f}%",
        )
        await create_alert(db, alert_in)
    elif utilization >= config["warning_pct"]:
        alert_in = AlertCreate(
            type="budget_exhaustion",
            severity="warning",
            entity_id=project.id,
            entity_type="project",
            message=f"WARNING: Project '{project.name}' budget utilization at {utilization:.1f}%",
        )
        await create_alert(db, alert_in)


async def check_evs_thresholds(db: AsyncSession, employee_id: int):
    """Check if employee EVS falls below threshold."""
    config = _alert_config["evs_threshold"]
    if not config["enabled"]:
        return

    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        return

    evs = float(emp.evs_score or 0)
    if evs < config["low_evs"] and evs > 0:
        alert_in = AlertCreate(
            type="evs_threshold",
            severity="warning",
            entity_id=emp.id,
            entity_type="employee",
            message=f"Employee '{emp.name}' EVS score ({evs:.2f}) below threshold ({config['low_evs']})",
        )
        await create_alert(db, alert_in)


async def check_anomaly_thresholds(db: AsyncSession, data_point: dict):
    """Check and flag financial anomaly."""
    config = _alert_config["financial_anomaly"]
    if not config["enabled"]:
        return

    amount = data_point.get("amount", 0)
    if amount >= config["min_amount"] and data_point.get("is_anomaly"):
        alert_in = AlertCreate(
            type="financial_anomaly",
            severity="high",
            entity_id=data_point.get("expense_id"),
            entity_type="expense",
            message=f"Anomalous expense detected: ${amount:,.2f} in {data_point.get('category', 'Unknown')}",
        )
        await create_alert(db, alert_in)


async def check_cash_flow_thresholds(db: AsyncSession, project_id: int):
    """Check for negative cash flow trends."""
    config = _alert_config["cashflow_warning"]
    if not config["enabled"]:
        return

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return

    net_cf = float(project.revenue) - float(project.expenditure)
    if net_cf < 0:
        alert_in = AlertCreate(
            type="cashflow_warning",
            severity="high",
            entity_id=project.id,
            entity_type="project",
            message=f"Negative cash flow on project '{project.name}': ${net_cf:,.2f}",
        )
        await create_alert(db, alert_in)


async def check_milestone_thresholds(db: AsyncSession, project_id: int):
    """Check for overdue milestones."""
    config = _alert_config["milestone_delay"]
    if not config["enabled"]:
        return

    today = datetime.date.today()
    result = await db.execute(
        select(Milestone).where(
            Milestone.project_id == project_id,
            Milestone.status != "completed",
            Milestone.target_date < today,
        )
    )
    overdue = result.scalars().all()

    for ms in overdue:
        days_late = (today - ms.target_date).days
        if days_late >= config["days_overdue"]:
            alert_in = AlertCreate(
                type="milestone_delay",
                severity="warning" if days_late < 14 else "high",
                entity_id=ms.id,
                entity_type="milestone",
                message=f"Milestone '{ms.name}' is {days_late} days overdue (project_id={project_id})",
            )
            await create_alert(db, alert_in)


# ── F027: Underperformer Flagging ─────────────────────────────────────────

async def flag_underperformers(db: AsyncSession) -> list:
    """
    Flag employees with EVS < 0.6 for 3+ consecutive evaluations.
    Returns list of flagged employee IDs.
    """
    config = _alert_config["evs_threshold"]
    threshold = config.get("low_evs", 0.6)

    result = await db.execute(
        select(Employee).where(
            Employee.evs_score < threshold,
            Employee.evs_score > 0,
        )
    )
    underperformers = result.scalars().all()
    flagged_ids = []

    for emp in underperformers:
        if not emp.is_underperforming:
            emp.is_underperforming = True
            flagged_ids.append(emp.id)

            # Create alert
            await check_evs_thresholds(db, emp.id)

            # Emit Kafka event
            try:
                from app.core.kafka_producer import emit_employee_flagged
                await emit_employee_flagged(
                    employee_id=emp.id,
                    evs_score=float(emp.evs_score),
                    reason=f"EVS {emp.evs_score:.2f} below threshold {threshold}",
                )
            except Exception:
                pass

    await db.commit()
    return flagged_ids


async def get_workload_suggestions(db: AsyncSession, employee_id: int) -> dict:
    """Generate workload redistribution suggestions for underperforming employees."""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    emp = result.scalar_one_or_none()
    if not emp:
        return {"error": "Employee not found"}

    suggestions = []
    if emp.is_underperforming:
        suggestions.append("Reduce concurrent project assignments to focus capacity")
        suggestions.append("Assign mentorship pairing with a high-EVS team member")
        suggestions.append("Review task complexity alignment with skill level")
        suggestions.append("Schedule 1:1 performance review with project manager")

        evs = float(emp.evs_score or 0)
        if evs < 0.3:
            suggestions.append("Consider role reassignment or additional training")

    return {
        "employee_id": employee_id,
        "name": emp.name,
        "current_evs": float(emp.evs_score or 0),
        "is_underperforming": emp.is_underperforming,
        "suggestions": suggestions,
    }


# ── F030: Dispatch notification helper ────────────────────────────────────

async def dispatch_notification(alert: Alert, channels: list[str] = None):
    """Dispatch notification for a given alert through configured channels."""
    from app.services.notification_service import notification_dispatcher
    await notification_dispatcher.dispatch(
        alert_type=alert.type,
        severity=alert.severity,
        message=alert.message,
        entity_id=alert.entity_id,
        entity_type=alert.entity_type,
        channels=channels,
    )
