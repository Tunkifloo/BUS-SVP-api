"""
Schedule Data Transfer Objects.
"""
from typing import Optional, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScheduleDTO:
    """Schedule data transfer object."""
    id: str
    route_id: str
    bus_id: str
    departure_time: str
    arrival_time: str
    date: str
    available_seats: int
    total_capacity: int
    status: str
    occupied_seats: Set[int]
    reserved_seats: Set[int]
    actual_departure_time: Optional[str]
    actual_arrival_time: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, schedule) -> 'ScheduleDTO':
        """Create DTO from Schedule entity."""
        return cls(
            id=schedule.id,
            route_id=schedule.route_id,
            bus_id=schedule.bus_id,
            departure_time=schedule.departure_time,
            arrival_time=schedule.arrival_time,
            date=schedule.date,
            available_seats=schedule.available_seats,
            total_capacity=schedule.total_capacity,
            status=schedule.status.value,
            occupied_seats=schedule.occupied_seats,
            reserved_seats=schedule.reserved_seats,
            actual_departure_time=schedule.actual_departure_time,
            actual_arrival_time=schedule.actual_arrival_time,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at
        )


@dataclass
class CreateScheduleDTO:
    """Create schedule data transfer object."""
    route_id: str
    bus_id: str
    departure_time: str
    arrival_time: str
    date: str
    available_seats: Optional[int] = None


@dataclass
class UpdateScheduleDTO:
    """Update schedule data transfer object."""
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None