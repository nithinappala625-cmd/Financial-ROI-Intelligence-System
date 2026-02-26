"""
Async database session factory and dependency.

Provides:
- engine: AsyncEngine connected to PostgreSQL
- async_session_maker: Session factory for creating async sessions
- get_db(): FastAPI dependency that yields an async session
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency — yields an async database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
