"""
Auth routes — JWT authentication endpoints.

POST /auth/register  — Create a new user
POST /auth/login     — OAuth2 password flow → JWT tokens
POST /auth/refresh   — Refresh access token
POST /auth/logout    — Placeholder (token blacklist deferred)
GET  /auth/me        — Get current user profile
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account.

    - Public users can only register as `employee` (default role).
    - Admin users can create accounts with any role via the admin panel.
    """
    return await auth_service.register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login — OAuth2 password flow",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password.

    Returns access_token and refresh_token (Bearer type).
    Uses OAuth2 password flow for compatibility with Swagger UI's Authorize button.
    """
    return await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Issue a new access token using a valid refresh token."""
    return await auth_service.refresh_access_token(db, body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout (placeholder)",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """Logout the current user.

    TODO: Implement token blacklisting via Redis.
    Currently a no-op — the client should discard the JWT locally.
    """
    return {"detail": "Successfully logged out."}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Return the profile of the currently authenticated user."""
    return UserRead.model_validate(current_user)
