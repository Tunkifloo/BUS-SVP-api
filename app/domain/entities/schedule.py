"""
Schedule domain entity.
"""
from typing import Optional, Dict, Any, Set
from datetime import datetime, time
from .base import AggregateRoot, DomainEvent
from ..value_objects import SeatNumber
from ...shared.constants import ScheduleStatus
from ...shared.validators import ScheduleValidator
from ...shared.utils import DateTimeUtils
from ...core.exceptions import (
    InvalidEntityStateException,
    ValidationException,
    SeatNotAvailableException,
    InsufficientSeatsException
)


class Schedule(AggregateRoot):
    """Schedule entity representing specific trip schedules."""

    def __init__(
            self,
            route_id: str,
            bus_id: str,
            departure_time: str,
            arrival_time: str,
            date: str,
            available_seats: int,
            status: ScheduleStatus = ScheduleStatus.SCHEDULED,
            schedule_id: Optional[str] = None
    ):
        """
        Initialize Schedule entity.

        Args:
            route_id: ID of the route
            bus_id: ID of the bus
            departure_time: Departure time (HH:MM format)
            arrival_time: Arrival time (HH:MM format)
            date: Travel date (YYYY-MM-DD format)
            available_seats: Number of available seats
            status: Schedule status (default: SCHEDULED)
            schedule_id: Schedule ID (optional, will be generated if not provided)
        """
        super().__init__(schedule_id)

        # Validate and set properties
        self._route_id = route_id
        self._bus_id = bus_id
        self._departure_time = ScheduleValidator.validate_departure_time(departure_time)
        self._arrival_time = ScheduleValidator.validate_arrival_time(arrival_time)
        self._date = ScheduleValidator.validate_date(date)
        self._available_seats = available_seats
        self._status = status

        # Validate schedule times
        ScheduleValidator.validate_schedule_times(self._departure_time, self._arrival_time)

        # Internal state
        self._occupied_seats: Set[int] = set()
        self._reserved_seats: Set[int] = set()
        self._total_capacity = available_seats  # Store original capacity
        self._actual_departure_time: Optional[str] = None
        self._actual_arrival_time: Optional[str] = None

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.Created",
                entity_id=self.id,
                data={
                    "route_id": self._route_id,
                    "bus_id": self._bus_id,
                    "departure_time": self._departure_time,
                    "date": self._date,
                    "available_seats": self._available_seats
                }
            )
        )

    @property
    def route_id(self) -> str:
        """Get route ID."""
        return self._route_id

    @property
    def bus_id(self) -> str:
        """Get bus ID."""
        return self._bus_id

    @property
    def departure_time(self) -> str:
        """Get departure time."""
        return self._departure_time

    @property
    def arrival_time(self) -> str:
        """Get arrival time."""
        return self._arrival_time

    @property
    def date(self) -> str:
        """Get travel date."""
        return self._date

    @property
    def available_seats(self) -> int:
        """Get available seats count."""
        return self._available_seats

    @property
    def status(self) -> ScheduleStatus:
        """Get schedule status."""
        return self._status

    @property
    def occupied_seats(self) -> Set[int]:
        """Get occupied seat numbers."""
        return self._occupied_seats.copy()

    @property
    def reserved_seats(self) -> Set[int]:
        """Get reserved seat numbers."""
        return self._reserved_seats.copy()

    @property
    def total_capacity(self) -> int:
        """Get total bus capacity."""
        return self._total_capacity

    @property
    def actual_departure_time(self) -> Optional[str]:
        """Get actual departure time."""
        return self._actual_departure_time

    @property
    def actual_arrival_time(self) -> Optional[str]:
        """Get actual arrival time."""
        return self._actual_arrival_time

    def update_schedule_times(
            self,
            departure_time: Optional[str] = None,
            arrival_time: Optional[str] = None
    ) -> None:
        """
        Update schedule times.

        Args:
            departure_time: New departure time (optional)
            arrival_time: New arrival time (optional)
        """
        if self._status not in [ScheduleStatus.SCHEDULED]:
            raise InvalidEntityStateException(
                "Schedule",
                self._status.value,
                "scheduled"
            )

        old_departure = self._departure_time
        old_arrival = self._arrival_time

        new_departure = departure_time if departure_time else self._departure_time
        new_arrival = arrival_time if arrival_time else self._arrival_time

        # Validate new times
        ScheduleValidator.validate_departure_time(new_departure)
        ScheduleValidator.validate_arrival_time(new_arrival)
        ScheduleValidator.validate_schedule_times(new_departure, new_arrival)

        if departure_time:
            self._departure_time = new_departure

        if arrival_time:
            self._arrival_time = new_arrival

        if old_departure != self._departure_time or old_arrival != self._arrival_time:
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="Schedule.TimesUpdated",
                    entity_id=self.id,
                    data={
                        "old_departure": old_departure,
                        "old_arrival": old_arrival,
                        "new_departure": self._departure_time,
                        "new_arrival": self._arrival_time
                    }
                )
            )

    def reserve_seat(self, seat_number: int) -> SeatNumber:
        """
        Reserve a specific seat.

        Args:
            seat_number: Seat number to reserve

        Returns:
            SeatNumber object

        Raises:
            SeatNotAvailableException: If seat is not available
        """
        if not self.can_accept_reservations():
            raise InvalidEntityStateException(
                "Schedule",
                self._status.value,
                "scheduled"
            )

        # Validate seat number
        seat = SeatNumber(seat_number, self._total_capacity)

        # Check if seat is available
        if not self.is_seat_available(seat_number):
            raise SeatNotAvailableException(seat_number)

        # Reserve the seat
        self._reserved_seats.add(seat_number)
        self._available_seats -= 1
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.SeatReserved",
                entity_id=self.id,
                data={
                    "seat_number": seat_number,
                    "available_seats": self._available_seats
                }
            )
        )

        return seat

    def occupy_seat(self, seat_number: int) -> None:
        """
        Mark a seat as occupied (confirmed reservation).

        Args:
            seat_number: Seat number to occupy
        """
        if seat_number in self._reserved_seats:
            self._reserved_seats.remove(seat_number)
        elif seat_number in self._occupied_seats:
            return  # Already occupied
        else:
            # Direct occupation (should validate availability first)
            if not self.is_seat_available(seat_number):
                raise SeatNotAvailableException(seat_number)
            self._available_seats -= 1

        self._occupied_seats.add(seat_number)
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.SeatOccupied",
                entity_id=self.id,
                data={
                    "seat_number": seat_number,
                    "available_seats": self._available_seats
                }
            )
        )

    def release_seat(self, seat_number: int) -> None:
        """
        Release a reserved or occupied seat.

        Args:
            seat_number: Seat number to release
        """
        released = False

        if seat_number in self._reserved_seats:
            self._reserved_seats.remove(seat_number)
            released = True

        if seat_number in self._occupied_seats:
            self._occupied_seats.remove(seat_number)
            released = True

        if released:
            self._available_seats += 1
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Schedule.SeatReleased",
                    entity_id=self.id,
                    data={
                        "seat_number": seat_number,
                        "available_seats": self._available_seats
                    }
                )
            )

    def is_seat_available(self, seat_number: int) -> bool:
        """
        Check if a seat is available for reservation.

        Args:
            seat_number: Seat number to check

        Returns:
            True if seat is available
        """
        return (seat_number not in self._reserved_seats and
                seat_number not in self._occupied_seats and
                1 <= seat_number <= self._total_capacity)

    def get_available_seat_numbers(self) -> Set[int]:
        """Get set of available seat numbers."""
        all_seats = set(range(1, self._total_capacity + 1))
        unavailable = self._reserved_seats | self._occupied_seats
        return all_seats - unavailable

    def start_trip(self, actual_departure_time: Optional[str] = None) -> None:
        """
        Start the trip.

        Args:
            actual_departure_time: Actual departure time (optional, defaults to current time)
        """
        if self._status != ScheduleStatus.SCHEDULED:
            raise InvalidEntityStateException(
                "Schedule",
                self._status.value,
                "scheduled"
            )

        self._status = ScheduleStatus.IN_PROGRESS
        self._actual_departure_time = actual_departure_time or DateTimeUtils.now_peru().strftime("%H:%M")
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.TripStarted",
                entity_id=self.id,
                data={
                    "scheduled_departure": self._departure_time,
                    "actual_departure": self._actual_departure_time
                }
            )
        )

    def complete_trip(self, actual_arrival_time: Optional[str] = None) -> None:
        """
        Complete the trip.

        Args:
            actual_arrival_time: Actual arrival time (optional, defaults to current time)
        """
        if self._status != ScheduleStatus.IN_PROGRESS:
            raise InvalidEntityStateException(
                "Schedule",
                self._status.value,
                "in_progress"
            )

        self._status = ScheduleStatus.COMPLETED
        self._actual_arrival_time = actual_arrival_time or DateTimeUtils.now_peru().strftime("%H:%M")
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.TripCompleted",
                entity_id=self.id,
                data={
                    "scheduled_arrival": self._arrival_time,
                    "actual_arrival": self._actual_arrival_time,
                    "passengers_count": len(self._occupied_seats)
                }
            )
        )

    def cancel_schedule(self, reason: Optional[str] = None) -> None:
        """
        Cancel the schedule.

        Args:
            reason: Reason for cancellation (optional)
        """
        if self._status in [ScheduleStatus.COMPLETED, ScheduleStatus.CANCELLED]:
            raise InvalidEntityStateException(
                "Schedule",
                self._status.value,
                "scheduled or in_progress"
            )

        old_status = self._status
        self._status = ScheduleStatus.CANCELLED

        # Release all reserved and occupied seats
        reserved_count = len(self._reserved_seats)
        occupied_count = len(self._occupied_seats)

        self._reserved_seats.clear()
        self._occupied_seats.clear()
        self._available_seats = self._total_capacity

        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Schedule.Cancelled",
                entity_id=self.id,
                data={
                    "old_status": old_status.value,
                    "reason": reason,
                    "affected_reservations": reserved_count,
                    "affected_passengers": occupied_count
                }
            )
        )

    def can_accept_reservations(self) -> bool:
        """Check if schedule can accept new reservations."""
        return (self._status == ScheduleStatus.SCHEDULED and
                self._available_seats > 0 and
                not self.is_deleted)

    def is_full(self) -> bool:
        """Check if schedule is fully booked."""
        return self._available_seats == 0

    def is_departure_today(self) -> bool:
        """Check if departure is today."""
        today = DateTimeUtils.now_peru().date()
        try:
            schedule_date = datetime.strptime(self._date, "%Y-%m-%d").date()
            return schedule_date == today
        except ValueError:
            return False

    def is_departure_in_past(self) -> bool:
        """Check if departure time has passed."""
        try:
            schedule_datetime = datetime.strptime(f"{self._date} {self._departure_time}", "%Y-%m-%d %H:%M")
            peru_schedule_time = DateTimeUtils.to_utc(schedule_datetime)
            return DateTimeUtils.now_utc() > peru_schedule_time
        except ValueError:
            return False

    def get_departure_datetime(self) -> datetime:
        """Get departure as datetime object."""
        return datetime.strptime(f"{self._date} {self._departure_time}", "%Y-%m-%d %H:%M")

    def get_arrival_datetime(self) -> datetime:
        """Get arrival as datetime object."""
        arrival_date = self._date
        # Handle overnight trips
        dep_time = datetime.strptime(self._departure_time, "%H:%M").time()
        arr_time = datetime.strptime(self._arrival_time, "%H:%M").time()

        if arr_time < dep_time:
            # Arrival is next day
            schedule_date = datetime.strptime(self._date, "%Y-%m-%d").date()
            from datetime import timedelta
            arrival_date = (schedule_date + timedelta(days=1)).strftime("%Y-%m-%d")

        return datetime.strptime(f"{arrival_date} {self._arrival_time}", "%Y-%m-%d %H:%M")

    def get_occupancy_rate(self) -> float:
        """Get occupancy rate as percentage."""
        if self._total_capacity == 0:
            return 0.0

        occupied_count = len(self._occupied_seats) + len(self._reserved_seats)
        return (occupied_count / self._total_capacity) * 100

    def get_status_display(self) -> str:
        """Get status display name."""
        status_map = {
            ScheduleStatus.SCHEDULED: "Programado",
            ScheduleStatus.IN_PROGRESS: "En Progreso",
            ScheduleStatus.COMPLETED: "Completado",
            ScheduleStatus.CANCELLED: "Cancelado"
        }
        return status_map.get(self._status, self._status.value)

    def get_seat_map_with_availability(self, seats_per_row: int = 4) -> Dict[str, Any]:
        """
        Get seat map with availability information.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Dictionary with seat layout and availability
        """
        seat_map = SeatNumber.generate_seat_map(self._total_capacity, seats_per_row)

        # Add availability information
        for row in seat_map['rows']:
            for seat_info in row['seats']:
                seat_num = seat_info['number']
                if seat_num in self._occupied_seats:
                    seat_info['status'] = 'occupied'
                elif seat_num in self._reserved_seats:
                    seat_info['status'] = 'reserved'
                else:
                    seat_info['status'] = 'available'

        seat_map['availability'] = {
            'total_seats': self._total_capacity,
            'available_seats': self._available_seats,
            'occupied_seats': len(self._occupied_seats),
            'reserved_seats': len(self._reserved_seats),
            'occupancy_rate': self.get_occupancy_rate()
        }

        return seat_map

    def get_display_summary(self) -> Dict[str, Any]:
        """Get summary for display purposes."""
        return {
            "date": self._date,
            "departure_time": self._departure_time,
            "arrival_time": self._arrival_time,
            "available_seats": self._available_seats,
            "total_capacity": self._total_capacity,
            "status": self.get_status_display(),
            "occupancy_rate": f"{self.get_occupancy_rate():.1f}%",
            "can_book": self.can_accept_reservations(),
            "is_full": self.is_full()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert schedule to dictionary representation."""
        return {
            'id': self.id,
            'route_id': self._route_id,
            'bus_id': self._bus_id,
            'departure_time': self._departure_time,
            'arrival_time': self._arrival_time,
            'date': self._date,
            'available_seats': self._available_seats,
            'status': self._status.value,
            'occupied_seats': list(self._occupied_seats),
            'reserved_seats': list(self._reserved_seats),
            'total_capacity': self._total_capacity,
            'actual_departure_time': self._actual_departure_time,
            'actual_arrival_time': self._actual_arrival_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }