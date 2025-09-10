"""
Create reservation use case.
"""
from typing import Dict, Any
from app.domain.services.reservation_service import ReservationService
from app.domain.repositories.user_repository import UserRepository
from app.core.exceptions import EntityNotFoundException
from app.shared.decorators import log_execution


class CreateReservationUseCase:
    """Use case for creating reservations."""

    def __init__(
        self,
        reservation_service: ReservationService,
        user_repository: UserRepository
    ):
        self._reservation_service = reservation_service
        self._user_repository = user_repository

    @log_execution(log_duration=True)
    async def execute(
        self,
        user_id: str,
        schedule_id: str,
        seat_number: int
    ) -> Dict[str, Any]:
        """
        Execute create reservation use case.

        Args:
            user_id: User ID
            schedule_id: Schedule ID
            seat_number: Seat number

        Returns:
            Created reservation information

        Raises:
            EntityNotFoundException: If user doesn't exist
        """
        # Validate user exists
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)

        if not user.is_active:
            raise EntityNotFoundException("User", user_id)  # Treat inactive as not found

        # Create reservation
        reservation = await self._reservation_service.create_reservation(
            user_id=user_id,
            schedule_id=schedule_id,
            seat_number=seat_number
        )

        return {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "schedule_id": reservation.schedule_id,
            "seat_number": reservation.seat_number.number,
            "price": reservation.price.to_float(),
            "status": reservation.status.value,
            "reservation_code": reservation.reservation_code,
            "created_at": reservation.created_at.isoformat()
        }