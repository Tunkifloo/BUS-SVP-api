"""
Get user reservations use case.
"""
from typing import List, Dict, Any
from app.domain.services.reservation_service import ReservationService
from app.domain.repositories.user_repository import UserRepository
from app.core.exceptions import EntityNotFoundException
from app.shared.decorators import log_execution


class GetUserReservationsUseCase:
    """Use case for getting user reservations."""

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
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Execute get user reservations use case.

        Args:
            user_id: User ID
            limit: Limit results
            offset: Offset for pagination

        Returns:
            List of user reservations with details

        Raises:
            EntityNotFoundException: If user doesn't exist
        """
        # Validate user exists
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", user_id)

        # Get reservations with details
        reservations = await self._reservation_service.get_user_reservations_with_details(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return reservations