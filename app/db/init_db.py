"""
Database initialisation — runs on first startup.

Per Section 14.2: "Creates tables on first run, seeds roles, creates default admin user."
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base
from app.models.user import RoleEnum, User
from app.core.security import hash_password
from app.db.session import async_session_maker, engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Create all tables and seed initial data."""

    # ── Create tables ─────────────────────────────────────────────────
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (if not existing).")

    # ── Seed default admin user ───────────────────────────────────────
    async with async_session_maker() as session:
        await _seed_admin(session)


async def _seed_admin(session: AsyncSession) -> None:
    """Create default admin user if not already present."""
    result = await session.execute(
        select(User).where(User.email == "admin@financial-roi.com")
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin is not None:
        logger.info("Default admin user already exists — skipping seed.")
        return

    # bcrypt max is 72 bytes — truncate seed password to be safe
    seed_password = "admin123"[:72]
    admin = User(
        email="admin@financial-roi.com",
        hashed_password=hash_password(seed_password),
        full_name="System Administrator",
        role=RoleEnum.admin,
        is_active=True,
    )
    session.add(admin)
    await session.commit()
    logger.info("Default admin user seeded: admin@financial-roi.com")
