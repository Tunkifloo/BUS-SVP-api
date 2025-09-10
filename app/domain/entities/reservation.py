"""
Reservation domain entity.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from .base import AggregateRoot, DomainEvent
from ..value_objects import SeatNumber, Money
from ...shared.constants import ReservationStatus
from ...shared.validators import ReservationValidator
from ...shared.utils import DateTimeUtils, BusinessUtils
from ...core.exceptions import (
    InvalidEntityStateException,
    ValidationException,
    ReservationNotCancellableException
)


class Reservation(AggregateRoot):
    """Reservation entity representing bus ticket reservations."""

    def __init__(
            self,
            user_id: str,
            schedule_id: str,
            seat_number: int,
            bus_capacity: int,
            price: float,
            status: ReservationStatus = ReservationStatus.ACTIVE,
            reservation_code: Optional[str] = None,
            reservation_id: Optional[str] = None
    ):
        """
        Initialize Reservation entity.

        Args:
            user_id: ID of the user making the reservation
            schedule_id: ID of the schedule being booked
            seat_number: Reserved seat number
            bus_capacity: Bus capacity for seat validation
            price: Reservation price
            status: Reservation status (default: ACTIVE)
            reservation_code: Unique reservation code (optional, will be generated)
            reservation_id: Reservation ID (optional, will be generated if not provided)
        """
        super().__init__(reservation_id)

        # Validate and set properties
        self._user_id = user_id
        self._schedule_id = schedule_id
        self._seat_number = SeatNumber(seat_number, bus_capacity)
        self._price = Money(price)
        self._status = status
        self._reservation_code = reservation_code or BusinessUtils.generate_reservation_code()
        self._cancellation_reason: Optional[str] = None
        self._cancelled_at: Optional[str] = None
        self._completed_at: Optional[str] = None

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="Reservation.Created",
                entity_id=self.id,
                data={
                    "user_id": self._user_id,
                    "schedule_id": self._schedule_id,
                    "seat_number": self._seat_number.number,
                    "price": self._price.to_float(),
                    "reservation_code": self._reservation_code
                }
            )
        )

    @property
    def user_id(self) -> str:
        """Get user ID."""
        return self._user_id

    @property
    def schedule_id(self) -> str:
        """Get schedule ID."""
        return self._schedule_id

    @property
    def seat_number(self) -> SeatNumber:
        """Get seat number."""
        return self._seat_number

    @property
    def price(self) -> Money:
        """Get reservation price."""
        return self._price

    @property
    def status(self) -> ReservationStatus:
        """Get reservation status."""
        return self._status

    @property
    def reservation_code(self) -> str:
        """Get reservation code."""
        return self._reservation_code

    @property
    def cancellation_reason(self) -> Optional[str]:
        """Get cancellation reason."""
        return self._cancellation_reason

    @property
    def cancelled_at(self) -> Optional[str]:
        """Get cancellation timestamp."""
        return self._cancelled_at

    @property
    def completed_at(self) -> Optional[str]:
        """Get completion timestamp."""
        return self._completed_at

    def cancel(self, reason: Optional[str] = None) -> None:
        """
        Cancel the reservation.

        Args:
            reason: Reason for cancellation (optional)

        Raises:
            ReservationNotCancellableException: If reservation cannot be cancelled
        """
        if self._status != ReservationStatus.ACTIVE:
            raise ReservationNotCancellableException(
                self.id,
                f"Reservation is in '{self._status.value}' status"
            )

        old_status = self._status
        self._status = ReservationStatus.CANCELLED
        self._cancellation_reason = reason
        self._cancelled_at = DateTimeUtils.now_utc().isoformat()
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Reservation.Cancelled",
                entity_id=self.id,
                data={
                    "old_status": old_status.value,
                    "new_status": self._status.value,
                    "reason": reason,
                    "cancelled_at": self._cancelled_at,
                    "seat_number": self._seat_number.number
                }
            )
        )

    def complete(self) -> None:
        """Mark reservation as completed (trip finished)."""
        if self._status != ReservationStatus.ACTIVE:
            raise InvalidEntityStateException(
                "Reservation",
                self._status.value,
                "active"
            )

        old_status = self._status
        self._status = ReservationStatus.COMPLETED
        self._completed_at = DateTimeUtils.now_utc().isoformat()
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Reservation.Completed",
                entity_id=self.id,
                data={
                    "old_status": old_status.value,
                    "new_status": self._status.value,
                    "completed_at": self._completed_at
                }
            )
        )

    def expire(self) -> None:
        """Mark reservation as expired."""
        if self._status not in [ReservationStatus.ACTIVE]:
            return  # Already processed

        old_status = self._status
        self._status = ReservationStatus.EXPIRED
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Reservation.Expired",
                entity_id=self.id,
                data={
                    "old_status": old_status.value,
                    "new_status": self._status.value,
                    "seat_number": self._seat_number.number
                }
            )
        )

    def update_price(self, new_price: float) -> None:
        """
        Update reservation price (admin only).

        Args:
            new_price: New price amount
        """
        if self._status != ReservationStatus.ACTIVE:
            raise InvalidEntityStateException(
                "Reservation",
                self._status.value,
                "active"
            )

        old_price = self._price.to_float()
        self._price = Money(new_price)
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Reservation.PriceUpdated",
                entity_id=self.id,
                data={
                    "old_price": old_price,
                    "new_price": new_price,
                    "reservation_code": self._reservation_code
                }
            )
        )

    def is_active(self) -> bool:
        """Check if reservation is active."""
        return self._status == ReservationStatus.ACTIVE

    def is_cancelled(self) -> bool:
        """Check if reservation is cancelled."""
        return self._status == ReservationStatus.CANCELLED

    def is_completed(self) -> bool:
        """Check if reservation is completed."""
        return self._status == ReservationStatus.COMPLETED

    def is_expired(self) -> bool:
        """Check if reservation is expired."""
        return self._status == ReservationStatus.EXPIRED

    def can_be_cancelled(self, departure_datetime: datetime) -> bool:
        """
        Check if reservation can be cancelled based on timing.

        Args:
            departure_datetime: Schedule departure datetime

        Returns:
            True if cancellation is allowed
        """
        if not self.is_active():
            return False

        return DateTimeUtils.is_cancellation_allowed(departure_datetime)

    def get_seat_display(self, seats_per_row: int = 4) -> str:
        """Get formatted seat display."""
        return self._seat_number.format_display(seats_per_row)

    def get_status_display(self) -> str:
        """Get status display name."""
        status_map = {
            ReservationStatus.ACTIVE: "Activa",
            ReservationStatus.CANCELLED: "Cancelada",
            ReservationStatus.COMPLETED: "Completada",
            ReservationStatus.EXPIRED: "Expirada"
        }
        return status_map.get(self._status, self._status.value)

    def calculate_refund_amount(self, fee_percentage: float = 0.1) -> Money:
        """
        Calculate refund amount for cancellation.

        Args:
            fee_percentage: Cancellation fee percentage (default: 10%)

        Returns:
            Refund amount as Money object
        """
        if not self.is_cancelled():
            return Money.zero()

        fee = self._price.percentage(fee_percentage * 100)
        refund = self._price.subtract(fee)
        return refund

    def get_display_summary(self) -> Dict[str, Any]:
        """Get summary for display purposes."""
        return {
            "reservation_code": self._reservation_code,
            "seat_number": self._seat_number.number,
            "seat_display": self.get_seat_display(),
            "price": self._price.to_string(),
            "status": self.get_status_display(),
            "is_active": self.is_active(),
            "created_at": self.created_at.isoformat(),
            "cancellation_reason": self._cancellation_reason
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert reservation to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self._user_id,
            'schedule_id': self._schedule_id,
            'seat_number': self._seat_number.number,
            'price': self._price.to_float(),
            'status': self._status.value,
            'reservation_code': self._reservation_code,
            'cancellation_reason': self._cancellation_reason,
            'cancelled_at': self._cancelled_at,
            'completed_at': self._completed_at,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }