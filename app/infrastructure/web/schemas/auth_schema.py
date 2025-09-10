"""
Authentication Pydantic schemas.
"""
from typing import Optional
from pydantic import Field, EmailStr
from .base_schema import BaseSchema
from .user_schema import UserResponseSchema


class LoginSchema(BaseSchema):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")


class RegisterSchema(BaseSchema):
    """Schema for user registration."""

    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")


class TokenResponseSchema(BaseSchema):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    user: UserResponseSchema = Field(..., description="User information")


class PasswordResetSchema(BaseSchema):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email")


class PasswordChangeSchema(BaseSchema):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
