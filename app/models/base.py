"""
SQLAlchemy ORM base classes and mixins.

- Base: DeclarativeBase for all ORM models.
- TimestampMixin: Adds created_at and updated_at to every table.
- IntegerPrimaryKeyMixin: Adds auto-increment integer primary key.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at columns to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IntegerPrimaryKeyMixin:
    """Mixin that adds an auto-increment integer primary key column."""

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


class TenantMixin:
    """Mixin that adds a tenant_id column to tables for multi-tenant schema isolation."""

    tenant_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
        default=1,
    )
