"""
RBAC permissions — role-based access control enforcement.

Provides:
- RoleEnum: re-exported from models for convenience
- require_role(*roles): FastAPI dependency factory that restricts access by role
"""

from fastapi import Depends, HTTPException, status

from app.models.user import RoleEnum, User


def require_role(*allowed_roles: RoleEnum):
    """Dependency factory that restricts an endpoint to specific roles.

    Usage in a route:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(RoleEnum.admin))):
            ...

    If the user's role is NOT in allowed_roles, raises HTTP 403.
    The dependency returns the current user object on success.
    """

    async def role_checker(
        current_user: User = Depends(_get_current_user_dependency()),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(r.value for r in allowed_roles)}",
            )
        return current_user

    return role_checker


def _get_current_user_dependency():
    """Late import to avoid circular dependency with deps.py."""
    from app.api.deps import get_current_active_user

    return get_current_active_user
