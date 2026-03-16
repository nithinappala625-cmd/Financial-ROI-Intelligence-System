"""Pagination utility functions."""

from typing import TypeVar, Sequence
from typing import Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func, select

T = TypeVar("T")


async def paginate(db: AsyncSession, query: Select, page: int, size: int) -> dict:
    """Execute a query with pagination and return paginated results."""
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one_or_none() or 0

    # Calculate skip
    skip = (page - 1) * size if page > 0 else 0

    # Get items
    paginated_query = query.offset(skip).limit(size)
    items_result = await db.execute(paginated_query)

    # To support scalars vs tuples based on query formulation
    items = items_result.scalars().all()

    pages = (total + size - 1) // size if size > 0 else 0

    return {"items": items, "total": total, "page": page, "size": size, "pages": pages}
