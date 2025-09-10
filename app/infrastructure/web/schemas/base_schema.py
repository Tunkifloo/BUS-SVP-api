"""
Base Pydantic schemas.
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=False,
        str_strip_whitespace=True
    )


class BaseResponseSchema(BaseSchema):
    """Base response schema."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginationSchema(BaseSchema):
    """Pagination metadata schema."""

    page: int = Field(1, ge=1, description="Current page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    total_items: int = Field(0, ge=0, description="Total number of items")
    total_pages: int = Field(0, ge=0, description="Total number of pages")
    has_next: bool = Field(False, description="Has next page")
    has_prev: bool = Field(False, description="Has previous page")


class PaginatedResponseSchema(BaseSchema):
    """Generic paginated response schema."""

    items: list = Field(..., description="List of items")
    pagination: PaginationSchema = Field(..., description="Pagination metadata")


class ErrorDetailSchema(BaseSchema):
    """Error detail schema."""

    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ErrorResponseSchema(BaseSchema):
    """Error response schema."""

    error: ErrorDetailSchema = Field(..., description="Error information")


class SuccessResponseSchema(BaseSchema):
    """Success response schema."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
