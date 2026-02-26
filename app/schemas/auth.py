"""
Auth Pydantic schemas — request/response models for authentication endpoints.

Models: UserCreate, UserRead, TokenResponse, RefreshTokenRequest.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import RoleEnum


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: RoleEnum = RoleEnum.employee


class UserRead(BaseModel):
    """Schema for returning user data (without password)."""

    id: int
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for login/refresh response — contains JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str
