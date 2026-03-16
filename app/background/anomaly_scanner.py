import logging
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.expense import Expense
from app.schemas.alert import AlertCreate
from app.services.alert_service import create_alert
import httpx
from config import settings

logger = logging.getLogger(__name__)
AI_URL = settings.AI_ENGINE_BASE_URL or "http://127.0.0.1:8001"


async def scan_for_anomalies():
    """Fetches new expenses, calls AI engine /anomaly/scan, flags anomalies."""
    logger.info("Running anomaly scanner...")

    async with async_session_maker() as db:
        # For simplicity, we scan expenses that haven't been flagged.
        # A more robust system would track the last scanned timestamp.
        query = select(Expense).where(Expense.flagged_anomaly == False)
        result = await db.execute(query)
        expenses = result.scalars().all()

        if not expenses:
            return

        async with httpx.AsyncClient() as client:
            for expense in expenses:
                try:
                    payload = {
                        "amount": float(expense.amount),
                        "category": expense.category,
                    }
                    resp = await client.post(f"{AI_URL}/anomaly/scan", json=payload)

                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("is_anomaly"):
                            expense.flagged_anomaly = True

                            # Create an alert
                            alert_in = AlertCreate(
                                type="financial_anomaly",
                                severity="high",
                                entity_id=expense.id,
                                entity_type="expense",
                                message=f"Anomaly detected in expense {expense.id} for amount {expense.amount}",
                            )
                            await create_alert(db, alert_in)
                except Exception as e:
                    logger.error(f"Anomaly scan failed for expense {expense.id}: {e}")

        await db.commit()
