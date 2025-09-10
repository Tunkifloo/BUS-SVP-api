"""
Reservation Data Transfer Objects.
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReservationDTO:
    """Reservation data transfer object."""
    id: str
    user_id: str
    schedule_id: str
    seat_number: int
    price: float
    status: str
    reservation_code: str
    cancellation_reason: Optional[str]
    cancelled_at: Optional[str]
    completed_at: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, reservation) -> 'ReservationDTO':
        """Create DTO from Reservation entity."""
        return cls(
            id=reservation.id,
            user_id=reservation.user_id,
            schedule_id=reservation.schedule_id,
            seat_number=reservation.seat_number.number,
            price=reservation.price.to_float(),
            status=reservation.status.value,
            reservation_code=reservation.reservation_code,
            cancellation_reason=reservation.cancellation_reason,
            cancelled_at=reservation.cancelled_at,
            completed_at=reservation.completed_at,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at
        )


@dataclass
class CreateReservationDTO:
    """Create reservation data transfer object."""
    user_id: str
    schedule_id: str
    seat_number: int


@dataclass
class CancelReservationDTO:
    """Cancel reservation data transfer object."""
    reservation_id: str
    reason: Optional[str] = None


@dataclass
class ReservationWithDetailsDTO:
    """Reservation with full details data transfer object."""
    reservation: ReservationDTO
    route: Optional[dict]
    company: Optional[dict]
    schedule: Optional[dict]
    bus: Optional[dict]