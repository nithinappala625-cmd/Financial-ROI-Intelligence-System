"""
Alembic environment — async configuration for PostgreSQL (Neon).

Imports all SQLAlchemy models so Alembic can auto-detect schema changes.
Reads DATABASE_URL from config.py.
"""

import asyncio
import ssl
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Add backend root to path so imports work ──────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings  # noqa: E402

# ── Import ALL models so Alembic sees them ────────────────────────────────
from app.models.base import Base  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.expense import Expense  # noqa: E402
from app.models.employee import Employee  # noqa: E402
from app.models.work_log import WorkLog  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.ai_prediction import AIPrediction  # noqa: E402
from app.models.project_assignment import ProjectAssignment  # noqa: E402

# ── Alembic Config ────────────────────────────────────────────────────────
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ── SSL context for Neon (asyncpg requires this instead of sslmode=require) ─
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL script without DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": ssl_context},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — connects to the actual database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
