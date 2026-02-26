"""
Base repository — generic async CRUD operations.

All domain repositories inherit from BaseRepo[T] and get:
get(), list(), create(), update(), delete() for free.
"""

from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(Generic[ModelType]):
    """Generic async repository providing CRUD operations.

    Usage:
        class ProjectRepo(BaseRepo[Project]):
            def __init__(self):
                super().__init__(Project)
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, db: AsyncSession, id: int
    ) -> ModelType | None:
        """Get a single record by its primary key."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """List records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count(self, db: AsyncSession) -> int:
        """Count total records."""
        result = await db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()

    async def create(
        self, db: AsyncSession, *, data: dict[str, Any]
    ) -> ModelType:
        """Create a new record from a dict of field values."""
        instance = self.model(**data)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        update_data: dict[str, Any],
    ) -> ModelType:
        """Update an existing record with a dict of new values."""
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self, db: AsyncSession, *, id: int
    ) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        obj = await self.get(db, id)
        if obj is None:
            return False
        await db.delete(obj)
        await db.commit()
        return True
