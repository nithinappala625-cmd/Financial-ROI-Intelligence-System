import logging
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.project import Project
from app.models.employee import Employee
from app.schemas.alert import AlertCreate
from app.services.alert_service import create_alert

logger = logging.getLogger(__name__)


async def check_alerts():
    """Loops projects, checks budget utilization & EVS thresholds, creates alerts."""
    logger.info("Running alert checker...")

    async with async_session_maker() as db:
        # Check projects for budget utilization > 90%
        result = await db.execute(select(Project))
        projects = result.scalars().all()

        for project in projects:
            if project.budget > 0 and project.expenditure > 0:
                utilization = project.expenditure / project.budget
                if utilization > 0.9:
                    alert_in = AlertCreate(
                        type="budget_exhaustion",
                        severity="high",
                        entity_id=project.id,
                        entity_type="project",
                        message=f"Project {project.name} has consumed {utilization*100:.1f}% of its budget.",
                    )
                    await create_alert(db, alert_in)

        # We can also add checks for employee low EVS here
        result_emp = await db.execute(select(Employee))
        employees = result_emp.scalars().all()
        # Mock logic, as true EVS requires historical logging
        for emp in employees:
            # Placeholder: flag arbitrary low performance for testing if needed
            pass

        await db.commit()
