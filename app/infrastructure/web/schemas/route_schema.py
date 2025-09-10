"""
Route Pydantic schemas.
"""
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from .base_schema import BaseSchema, BaseResponseSchema


class RouteBaseSchema(BaseSchema):
    """Base route schema."""

    origin: str = Field(..., min_length=2, max_length=50, description="Origin city")
    destination: str = Field(..., min_length=2, max_length=50, description="Destination city")
    price: float = Field(..., gt=0, description="Route price")
    duration: str = Field(..., description="Trip duration (e.g., '2h 30m')")
    distance_km: Optional[int] = Field(None, gt=0, description="Distance in kilometers")
    description: Optional[str] = Field(None, max_length=1000, description="Route description")

    @validator('origin', 'destination')
    def validate_city_names(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('City name must be at least 2 characters')
        return v.strip().title()


class RouteCreateSchema(RouteBaseSchema):
    """Schema for creating a route."""

    company_id: str = Field(..., description="Company ID")


class RouteUpdateSchema(BaseSchema):
    """Schema for updating a route."""

    price: Optional[float] = Field(None, gt=0)
    duration: Optional[str] = Field(None)
    distance_km: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=1000)


class RouteResponseSchema(BaseResponseSchema, RouteBaseSchema):
    """Schema for route responses."""

    company_id: str = Field(..., description="Company ID")
    status: str = Field(..., description="Route status")
    total_bookings: int = Field(..., ge=0, description="Total bookings")
    popularity_score: float = Field(..., ge=0, description="Popularity score")


class RouteSearchSchema(BaseSchema):
    """Schema for route search."""

    origin: Optional[str] = Field(None, description="Origin city")
    destination: Optional[str] = Field(None, description="Destination city")
    date: Optional[str] = Field(None, description="Travel date (YYYY-MM-DD)")
    min_seats: int = Field(1, ge=1, description="Minimum available seats")


class RouteWithSchedulesSchema(BaseSchema):
    """Schema for route with schedules."""

    route: RouteResponseSchema = Field(..., description="Route information")
    company: Optional[Dict[str, Any]] = Field(None, description="Company information")
    schedules: List[Dict[str, Any]] = Field(..., description="Available schedules")
    schedule_count: int = Field(..., description="Number of schedules")
