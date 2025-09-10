"""
Seat allocation domain service.
"""
from typing import List, Set, Optional, Dict, Any
from ..entities.schedule import Schedule
from ..entities.reservation import Reservation
from ..value_objects.seat_number import SeatNumber
from ..repositories.schedule_repository import ScheduleRepository
from ..repositories.reservation_repository import ReservationRepository
from ...core.exceptions import (
    SeatNotAvailableException,
    InsufficientSeatsException
)


class SeatAllocationService:
    """Domain service for seat allocation operations."""

    def __init__(
            self,
            schedule_repository: ScheduleRepository,
            reservation_repository: ReservationRepository
    ):
        self._schedule_repository = schedule_repository
        self._reservation_repository = reservation_repository

    async def check_seat_availability(
            self,
            schedule_id: str,
            seat_number: int
    ) -> bool:
        """
        Check if a specific seat is available.

        Args:
            schedule_id: Schedule ID
            seat_number: Seat number to check

        Returns:
            True if seat is available
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            return False

        return schedule.is_seat_available(seat_number)

    async def get_available_seats(
            self,
            schedule_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all available seats for a schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            List of available seats with details
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            return []

        available_seat_numbers = schedule.get_available_seat_numbers()
        available_seats = []

        for seat_num in sorted(available_seat_numbers):
            seat = SeatNumber(seat_num, schedule.total_capacity)
            available_seats.append({
                'number': seat_num,
                'display': seat.format_display(),
                'is_window': seat.is_window_seat(),
                'is_aisle': seat.is_aisle_seat(),
                'row': seat.get_row_number(),
                'position': seat.get_position_in_row()
            })

        return available_seats

    async def reserve_seat(
            self,
            schedule_id: str,
            seat_number: int,
            user_id: str
    ) -> bool:
        """
        Reserve a specific seat.

        Args:
            schedule_id: Schedule ID
            seat_number: Seat number to reserve
            user_id: User making the reservation

        Returns:
            True if reservation was successful

        Raises:
            SeatNotAvailableException: If seat is not available
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise SeatNotAvailableException(seat_number)

        # Check if seat is available
        if not schedule.is_seat_available(seat_number):
            raise SeatNotAvailableException(seat_number)

        # Reserve the seat in the schedule
        schedule.reserve_seat(seat_number)

        # Update schedule
        await self._schedule_repository.update(schedule)

        return True

    async def release_seat(
            self,
            schedule_id: str,
            seat_number: int
    ) -> bool:
        """
        Release a reserved seat.

        Args:
            schedule_id: Schedule ID
            seat_number: Seat number to release

        Returns:
            True if release was successful
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            return False

        schedule.release_seat(seat_number)
        await self._schedule_repository.update(schedule)

        return True

    async def get_seat_map_with_status(
            self,
            schedule_id: str
    ) -> Dict[str, Any]:
        """
        Get complete seat map with availability status.

        Args:
            schedule_id: Schedule ID

        Returns:
            Seat map with availability information
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            return {}

        return schedule.get_seat_map_with_availability()

    async def find_best_available_seats(
            self,
            schedule_id: str,
            count: int = 1,
            prefer_window: bool = False,
            prefer_front: bool = False
    ) -> List[int]:
        """
        Find best available seats based on preferences.

        Args:
            schedule_id: Schedule ID
            count: Number of seats needed
            prefer_window: Prefer window seats
            prefer_front: Prefer front section seats

        Returns:
            List of recommended seat numbers

        Raises:
            InsufficientSeatsException: If not enough seats available
        """
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise InsufficientSeatsException(count, 0)

        available_seats = list(schedule.get_available_seat_numbers())

        if len(available_seats) < count:
            raise InsufficientSeatsException(count, len(available_seats))

        # Score seats based on preferences
        seat_scores = []
        for seat_num in available_seats:
            seat = SeatNumber(seat_num, schedule.total_capacity)
            score = 0

            # Base score (lower seat numbers preferred)
            score += (schedule.total_capacity - seat_num) * 0.1

            # Window preference
            if prefer_window and seat.is_window_seat():
                score += 10

            # Front preference
            if prefer_front and seat.is_front_section():
                score += 5

            seat_scores.append((seat_num, score))

        # Sort by score (highest first)
        seat_scores.sort(key=lambda x: x[1], reverse=True)

        # Try to find contiguous seats if multiple needed
        if count > 1:
            best_seats = self._find_contiguous_seats(seat_scores, count)
            if best_seats:
                return best_seats

        # Return top scoring individual seats
        return [seat_num for seat_num, _ in seat_scores[:count]]

    def _find_contiguous_seats(
            self,
            seat_scores: List[tuple],
            count: int,
            seats_per_row: int = 4
    ) -> Optional[List[int]]:
        """Find contiguous seats in the same row."""
        available_seats = [seat_num for seat_num, _ in seat_scores]
        available_seats.sort()

        for i in range(len(available_seats) - count + 1):
            seats_group = available_seats[i:i + count]

            # Check if seats are in same row and contiguous
            first_seat = SeatNumber(seats_group[0])
            last_seat = SeatNumber(seats_group[-1])

            if (first_seat.get_row_number(seats_per_row) ==
                    last_seat.get_row_number(seats_per_row)):

                # Check if seats are contiguous
                if seats_group[-1] - seats_group[0] == count - 1:
                    return seats_group

        return None