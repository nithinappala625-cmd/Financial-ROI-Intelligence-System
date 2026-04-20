"""
Async database session factory and dependency.

Provides:
- engine: AsyncEngine connected to PostgreSQL (Neon)
- async_session_maker: Session factory for creating async sessions
- get_db(): FastAPI dependency that yields an async session
"""

import ssl

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# Build SSL context for Neon (asyncpg requires connect_args, not URL params)
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"ssl": _ssl_ctx},
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency — yields an async database session (Primary)."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# Read-Replica Configuration for Analytics
ro_engine = None
ro_session_maker = None

if getattr(settings, "RO_DATABASE_URL", None):
    ro_engine = create_async_engine(
        settings.RO_DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"ssl": _ssl_ctx},
    )
    ro_session_maker = async_sessionmaker(
        ro_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_ro_db():
    """Yields an async read-replica database session for analytics.
    Falls back to primary database if no replica URL is configured.
    """
    if ro_session_maker is None:
        async for session in get_db():
            yield session
        return

    async with ro_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
