"""
Cancel reservation use case.
"""
from typing import Dict, Any, Optional
from app.domain.services.reservation_service import ReservationService
from app.shared.decorators import log_execution


class CancelReservationUseCase:
    """Use case for cancelling reservations."""

    def __init__(self, reservation_service: ReservationService):
        self._reservation_service = reservation_service

    @log_execution(log_duration=True)
    async def execute(
        self,
        reservation_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute cancel reservation use case.

        Args:
            reservation_id: Reservation ID
            reason: Cancellation reason (optional)

        Returns:
            Cancelled reservation information
        """
        # Cancel reservation
        reservation = await self._reservation_service.cancel_reservation(
            reservation_id=reservation_id,
            reason=reason
        )

        return {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "schedule_id": reservation.schedule_id,
            "seat_number": reservation.seat_number.number,
            "price": reservation.price.to_float(),
            "status": reservation.status.value,
            "reservation_code": reservation.reservation_code,
            "cancellation_reason": reservation.cancellation_reason,
            "cancelled_at": reservation.cancelled_at,
            "updated_at": reservation.updated_at.isoformat()
        }