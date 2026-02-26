"""
Common Pydantic schemas shared across all domains.

Models: ErrorResponse, HealthCheck, PaginatedResponse, SortOrder.
"""

import enum
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


class HealthCheck(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str


class SortOrder(str, enum.Enum):
    """Sort direction for list queries."""

    asc = "asc"
    desc = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int
