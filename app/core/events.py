"""
Application lifecycle events — startup and shutdown.

Per Section 14.5: on_startup() initialises the async DB engine, runs init_db().
on_shutdown() closes the DB pool.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.init_db import init_db
from app.db.session import engine
from app.background.scheduler import start_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager — startup and shutdown logic."""

    # ── Startup ───────────────────────────────────────────────────────
    logger.info("Starting up — initialising database...")
    await init_db()
    logger.info("Database initialised. Application ready.")

    start_scheduler()

    yield

    # ── Shutdown ──────────────────────────────────────────────────────
    shutdown_scheduler()
    logger.info("Shutting down — disposing database engine...")
    await engine.dispose()
    logger.info("Database engine disposed. Goodbye.")
