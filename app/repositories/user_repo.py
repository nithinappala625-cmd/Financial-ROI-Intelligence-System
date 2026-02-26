"""
User repository — data access for the users table.

Inherits generic CRUD from BaseRepo[User].
Adds: get_by_email() for auth lookups.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repo import BaseRepo


class UserRepo(BaseRepo[User]):
    """Repository for the users table."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(
        self, db: AsyncSession, email: str
    ) -> User | None:
        """Look up a user by email address. Returns None if not found."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


# Singleton instance for dependency injection
user_repo = UserRepo()
