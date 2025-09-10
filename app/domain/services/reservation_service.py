"""
Reservation domain service.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..entities.reservation import Reservation
from ..entities.schedule import Schedule
from ..entities.route import Route
from ..repositories.reservation_repository import ReservationRepository
from ..repositories.schedule_repository import ScheduleRepository
from ..repositories.route_repository import RouteRepository
from .seat_allocation_service import SeatAllocationService
from ...shared.utils import DateTimeUtils
from ...core.exceptions import (
    ValidationException,
    SeatNotAvailableException,
    ReservationNotCancellableException
)


class ReservationService:
    """Domain service for reservation operations."""

    def __init__(
            self,
            reservation_repository: ReservationRepository,
            schedule_repository: ScheduleRepository,
            route_repository: RouteRepository,
            seat_allocation_service: SeatAllocationService
    ):
        self._reservation_repository = reservation_repository
        self._schedule_repository = schedule_repository
        self._route_repository = route_repository
        self._seat_allocation_service = seat_allocation_service

    async def create_reservation(
            self,
            user_id: str,
            schedule_id: str,
            seat_number: int
    ) -> Reservation:
        """
        Create a new reservation.

        Args:
            user_id: User ID
            schedule_id: Schedule ID
            seat_number: Seat number

        Returns:
            Created reservation

        Raises:
            ValidationException: If validation fails
            SeatNotAvailableException: If seat is not available
        """
        # Get schedule and route
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise ValidationException("schedule_id", schedule_id, "Schedule not found")

        route = await self._route_repository.find_by_id(schedule.route_id)
        if not route:
            raise ValidationException("schedule_id", schedule_id, "Route not found for schedule")

        # Validate schedule can accept reservations
        if not schedule.can_accept_reservations():
            raise ValidationException("schedule_id", schedule_id, "Schedule cannot accept reservations")

        # Validate seat availability
        if not await self._seat_allocation_service.check_seat_availability(schedule_id, seat_number):
            raise SeatNotAvailableException(seat_number)

        # Check for existing reservation
        exists = await self._reservation_repository.exists_seat_reservation(schedule_id, seat_number)
        if exists:
            raise SeatNotAvailableException(seat_number)

        # Reserve the seat
        await self._seat_allocation_service.reserve_seat(schedule_id, seat_number, user_id)

        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            schedule_id=schedule_id,
            seat_number=seat_number,
            bus_capacity=schedule.total_capacity,
            price=route.price.to_float()
        )

        # Save reservation
        saved_reservation = await self._reservation_repository.save(reservation)

        # Update route booking count
        route.record_booking()
        await self._route_repository.update(route)

        return saved_reservation

    async def cancel_reservation(
            self,
            reservation_id: str,
            reason: Optional[str] = None
    ) -> Reservation:
        """
        Cancel a reservation.

        Args:
            reservation_id: Reservation ID
            reason: Cancellation reason

        Returns:
            Cancelled reservation

        Raises:
            ValidationException: If reservation not found
            ReservationNotCancellableException: If cannot be cancelled
        """
        reservation = await self._reservation_repository.find_by_id(reservation_id)
        if not reservation:
            raise ValidationException("reservation_id", reservation_id, "Reservation not found")

        # Get schedule to check timing
        schedule = await self._schedule_repository.find_by_id(reservation.schedule_id)
        if schedule:
            departure_datetime = schedule.get_departure_datetime()

            # Check if cancellation is allowed
            if not reservation.can_be_cancelled(departure_datetime):
                raise ReservationNotCancellableException(
                    reservation_id,
                    "Cancellation deadline has passed"
                )

        # Cancel the reservation
        reservation.cancel(reason)

        # Release the seat
        await self._seat_allocation_service.release_seat(
            reservation.schedule_id,
            reservation.seat_number.number
        )

        # Update reservation
        return await self._reservation_repository.update(reservation)

    async def get_user_reservations_with_details(
            self,
            user_id: str,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user reservations with complete details.

        Args:
            user_id: User ID
            limit: Limit results
            offset: Offset for pagination

        Returns:
            List of reservations with details
        """
        return await self._reservation_repository.find_user_reservations_with_details(
            user_id, limit, offset
        )

    async def complete_trip_reservations(self, schedule_id: str) -> int:
        """
        Mark all active reservations for a schedule as completed.

        Args:
            schedule_id: Schedule ID

        Returns:
            Number of reservations completed
        """
        reservations = await self._reservation_repository.find_active_by_schedule(schedule_id)

        completed_count = 0
        for reservation in reservations:
            reservation.complete()
            await self._reservation_repository.update(reservation)
            completed_count += 1

        return completed_count

    async def expire_old_reservations(self, cutoff_datetime: datetime) -> int:
        """
        Expire reservations for schedules that have passed.

        Args:
            cutoff_datetime: Cutoff datetime for expiration

        Returns:
            Number of reservations expired
        """
        # This would typically be called by a background job
        # For now, we'll implement the basic logic

        # Find active reservations and check their schedules
        active_reservations = await self._reservation_repository.find_by_status("active")

        expired_count = 0
        for reservation in active_reservations:
            schedule = await self._schedule_repository.find_by_id(reservation.schedule_id)
            if schedule:
                departure_datetime = schedule.get_departure_datetime()
                if departure_datetime < cutoff_datetime:
                    reservation.expire()
                    await self._reservation_repository.update(reservation)
                    expired_count += 1

        return expired_count