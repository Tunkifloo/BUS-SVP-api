"""
Reservation Pydantic schemas.
"""
from typing import Optional, Dict, Any
from pydantic import Field, validator
from datetime import datetime
from .base_schema import BaseSchema, BaseResponseSchema


class ReservationBaseSchema(BaseSchema):
    """Base reservation schema."""

    seat_number: int = Field(..., ge=1, le=60, description="Seat number")


class ReservationCreateSchema(ReservationBaseSchema):
    """Schema for creating a reservation."""

    schedule_id: str = Field(..., description="Schedule ID")


class ReservationUpdateSchema(BaseSchema):
    """Schema for updating a reservation."""

    pass  # Reservations typically can't be updated, only cancelled


class ReservationCancelSchema(BaseSchema):
    """Schema for cancelling a reservation."""

    reason: Optional[str] = Field(None, max_length=500, description="Cancellation reason")


class ReservationResponseSchema(BaseResponseSchema, ReservationBaseSchema):
    """Schema for reservation responses."""

    user_id: str = Field(..., description="User ID")
    schedule_id: str = Field(..., description="Schedule ID")
    price: float = Field(..., description="Reservation price")
    status: str = Field(..., description="Reservation status")
    reservation_code: str = Field(..., description="Unique reservation code")
    cancellation_reason: Optional[str] = Field(None, description="Cancellation reason")
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class ReservationWithDetailsSchema(BaseSchema):
    """Schema for reservation with complete details."""

    reservation: ReservationResponseSchema = Field(..., description="Reservation info")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Schedule info")
    route: Optional[Dict[str, Any]] = Field(None, description="Route info")
    company: Optional[Dict[str, Any]] = Field(None, description="Company info")
    bus: Optional[Dict[str, Any]] = Field(None, description="Bus info")
