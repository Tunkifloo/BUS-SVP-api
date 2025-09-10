"""
Bus Pydantic schemas.
"""
from typing import Optional, List
from pydantic import Field, validator
from .base_schema import BaseSchema, BaseResponseSchema


class BusBaseSchema(BaseSchema):
    """Base bus schema."""

    plate_number: str = Field(..., max_length=20, description="Bus plate number")
    capacity: int = Field(..., ge=1, le=60, description="Bus seating capacity")
    model: str = Field(..., min_length=2, max_length=50, description="Bus model")
    year: Optional[int] = Field(None, ge=1980, le=2030, description="Manufacturing year")
    features: Optional[List[str]] = Field(None, description="Bus features")

    @validator('plate_number')
    def validate_plate_number(cls, v):
        import re
        # Peru plate format: ABC-123 or AB-1234
        if not re.match(r'^[A-Z]{2,3}-\d{3,4}$', v.upper()):
            raise ValueError('Invalid Peru plate number format (e.g., ABC-123)')
        return v.upper()


class BusCreateSchema(BusBaseSchema):
    """Schema for creating a bus."""

    company_id: str = Field(..., description="Company ID")


class BusUpdateSchema(BaseSchema):
    """Schema for updating a bus."""

    model: Optional[str] = Field(None, min_length=2, max_length=50)
    year: Optional[int] = Field(None, ge=1980, le=2030)
    features: Optional[List[str]] = Field(None)


class BusResponseSchema(BaseResponseSchema, BusBaseSchema):
    """Schema for bus responses."""

    company_id: str = Field(..., description="Company ID")
    status: str = Field(..., description="Bus status")
    mileage: int = Field(..., ge=0, description="Current mileage")
    last_maintenance_date: Optional[str] = Field(None, description="Last maintenance date")
    next_maintenance_due: Optional[str] = Field(None, description="Next maintenance due date")
