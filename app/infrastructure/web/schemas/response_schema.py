"""
Response schemas for API responses.
"""
from typing import Optional, Any, Dict, List
from pydantic import Field
from .base_schema import BaseSchema


class ApiResponseSchema(BaseSchema):
    """Standard API response schema."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class PaginatedApiResponseSchema(BaseSchema):
    """Paginated API response schema."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: List[Any] = Field(..., description="Response data items")
    pagination: Dict[str, Any] = Field(..., description="Pagination metadata")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class HealthResponseSchema(BaseSchema):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    database: Optional[str] = Field(None, description="Database status")
    environment: Optional[str] = Field(None, description="Environment")


class TokenValidationSchema(BaseSchema):
    """Token validation response schema."""

    valid: bool = Field(..., description="Token validity")
    user_id: Optional[str] = Field(None, description="User ID")
    role: Optional[str] = Field(None, description="User role")
    expires_at: Optional[str] = Field(None, description="Token expiration")


class FileUploadResponseSchema(BaseSchema):
    """File upload response schema."""

    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    file_url: str = Field(..., description="File access URL")
    uploaded_at: str = Field(..., description="Upload timestamp")


class BulkOperationResponseSchema(BaseSchema):
    """Bulk operation response schema."""

    total_items: int = Field(..., description="Total items processed")
    successful_items: int = Field(..., description="Successfully processed items")
    failed_items: int = Field(..., description="Failed items")
    errors: List[str] = Field(..., description="Error details for failed items")
