"""
Auth service — business logic for user registration, authentication, and token refresh.

Called by auth routes. Calls user_repo for data access and security module for JWT/passwords.
"""

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import RoleEnum, User
from app.repositories.user_repo import user_repo
from app.schemas.auth import TokenResponse, UserCreate, UserRead


async def register_user(db: AsyncSession, user_data: UserCreate) -> UserRead:
    """Register a new user.

    - Checks for duplicate email
    - Hashes the password
    - Creates the user record
    - Returns the user profile (without password)
    """
    existing = await user_repo.get_by_email(db, user_data.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = await user_repo.create(
        db,
        data={
            "email": user_data.email,
            "hashed_password": hash_password(user_data.password),
            "full_name": user_data.full_name,
            "role": user_data.role,
        },
    )

    return UserRead.model_validate(user)


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> TokenResponse:
    """Authenticate a user by email/password and return JWT tokens.

    - Looks up user by email
    - Verifies password
    - Creates access + refresh tokens
    """
    user = await user_repo.get_by_email(db, email)

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token_data = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_access_token(
    db: AsyncSession, refresh_token_str: str
) -> TokenResponse:
    """Issue a new access token from a valid refresh token.

    - Decodes the refresh token
    - Validates it's a refresh type
    - Fetches the user to ensure they still exist and are active
    - Creates a new access token
    """
    try:
        payload = decode_access_token(refresh_token_str)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    user = await user_repo.get(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    token_data = {"sub": str(user.id), "role": user.role.value}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
