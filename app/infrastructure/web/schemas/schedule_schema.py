"""
Schedule Pydantic schemas.
"""
from typing import Optional, Set, Dict, Any, List
from pydantic import Field, validator
from .base_schema import BaseSchema, BaseResponseSchema
from datetime import datetime, time


class ScheduleBaseSchema(BaseSchema):
    """Base schedule schema."""

    departure_time: str = Field(..., description="Departure time (HH:MM)")
    arrival_time: str = Field(..., description="Arrival time (HH:MM)")
    date: str = Field(..., description="Travel date (YYYY-MM-DD)")

    @validator('departure_time', 'arrival_time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError('Invalid time format. Use HH:MM format (e.g., 14:30)')
        return v

    @validator('date')
    def validate_date_format(cls, v):
        try:
            date_obj = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD format')

        # Check if date is in the future
        from datetime import date
        today = date.today()
        if date_obj < today:
            raise ValueError('Schedule date must be today or in the future')

        return v


class ScheduleCreateSchema(ScheduleBaseSchema):
    """Schema for creating a schedule."""

    route_id: str = Field(..., description="Route ID")
    bus_id: str = Field(..., description="Bus ID")
    available_seats: Optional[int] = Field(None, ge=1, description="Available seats")


class ScheduleUpdateSchema(BaseSchema):
    """Schema for updating a schedule."""

    departure_time: Optional[str] = Field(None, description="New departure time")
    arrival_time: Optional[str] = Field(None, description="New arrival time")

    @validator('departure_time', 'arrival_time')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, "%H:%M")
            except ValueError:
                raise ValueError('Invalid time format. Use HH:MM format')
        return v


class ScheduleResponseSchema(BaseResponseSchema, ScheduleBaseSchema):
    """Schema for schedule responses."""

    route_id: str = Field(..., description="Route ID")
    bus_id: str = Field(..., description="Bus ID")
    available_seats: int = Field(..., ge=0, description="Available seats")
    total_capacity: int = Field(..., ge=1, description="Total bus capacity")
    status: str = Field(..., description="Schedule status")
    occupied_seats: Set[int] = Field(..., description="Occupied seat numbers")
    reserved_seats: Set[int] = Field(..., description="Reserved seat numbers")
    actual_departure_time: Optional[str] = Field(None, description="Actual departure time")
    actual_arrival_time: Optional[str] = Field(None, description="Actual arrival time")


class SeatMapSchema(BaseSchema):
    """Schema for seat map."""

    seat_number: int = Field(..., description="Seat number")
    status: str = Field(..., description="Seat status (available/occupied/reserved)")
    is_window: bool = Field(..., description="Is window seat")
    is_aisle: bool = Field(..., description="Is aisle seat")
    row: int = Field(..., description="Row number")
    position: str = Field(..., description="Position in row")


class ScheduleWithSeatMapSchema(ScheduleResponseSchema):
    """Schema for schedule with seat map."""

    seat_map: List[SeatMapSchema] = Field(..., description="Seat availability map")
    occupancy_rate: float = Field(..., description="Occupancy rate percentage")
