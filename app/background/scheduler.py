import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.background.anomaly_scanner import scan_for_anomalies
from app.background.alert_checker import check_alerts

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler():
    logger.info("Initializing background scheduler...")

    # Run every 15 minutes
    scheduler.add_job(scan_for_anomalies, "interval", minutes=15, id="anomaly_scanner")

    # Run every 1 hour
    scheduler.add_job(check_alerts, "interval", hours=1, id="alert_checker")

    scheduler.start()
    logger.info("Scheduler started successfully.")


def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler shut down successfully.")
