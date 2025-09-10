"""
Company Pydantic schemas.
"""
from typing import Optional
from pydantic import Field, EmailStr
from .base_schema import BaseSchema, BaseResponseSchema


class CompanyBaseSchema(BaseSchema):
    """Base company schema."""

    name: str = Field(..., min_length=3, max_length=100, description="Company name")
    email: EmailStr = Field(..., description="Company email")
    phone: str = Field(..., max_length=20, description="Company phone")
    address: Optional[str] = Field(None, max_length=500, description="Company address")
    description: Optional[str] = Field(None, max_length=1000, description="Company description")


class CompanyCreateSchema(CompanyBaseSchema):
    """Schema for creating a company."""
    pass


class CompanyUpdateSchema(BaseSchema):
    """Schema for updating a company."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)


class CompanyResponseSchema(BaseResponseSchema, CompanyBaseSchema):
    """Schema for company responses."""

    status: str = Field(..., description="Company status")
    rating: float = Field(..., ge=0, le=5, description="Company rating")
    total_trips: int = Field(..., ge=0, description="Total completed trips")
