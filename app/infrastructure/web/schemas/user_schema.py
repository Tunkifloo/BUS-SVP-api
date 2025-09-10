"""
User Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import Field, EmailStr, validator
from .base_schema import BaseSchema, BaseResponseSchema


class UserBaseSchema(BaseSchema):
    """Base user schema."""

    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")


class UserCreateSchema(UserBaseSchema):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100, description="User password")
    role: str = Field("user", description="User role")

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'admin', 'company_admin']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v


class UserUpdateSchema(BaseSchema):
    """Schema for updating a user."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserResponseSchema(BaseResponseSchema, UserBaseSchema):
    """Schema for user responses."""

    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    email_verified: bool = Field(..., description="Email verification status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class UserListResponseSchema(BaseSchema):
    """Schema for user list responses."""

    users: list[UserResponseSchema] = Field(..., description="List of users")
