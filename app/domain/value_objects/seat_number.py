"""
Seat number value object.
"""
from typing import Optional
from ..entities.base import ValueObject
from ...shared.constants import BusinessRules
from ...core.exceptions import ValidationException


class SeatNumber(ValueObject):
    """Seat number value object with validation."""

    def __init__(self, number: int, bus_capacity: Optional[int] = None):
        """
        Initialize seat number value object.

        Args:
            number: Seat number
            bus_capacity: Maximum capacity of the bus (for validation)

        Raises:
            ValidationException: If seat number is invalid
        """
        if not isinstance(number, int):
            raise ValidationException("seat_number", number, "Seat number must be an integer")

        if number < BusinessRules.MIN_SEAT_NUMBER:
            raise ValidationException(
                "seat_number",
                number,
                f"Seat number must be at least {BusinessRules.MIN_SEAT_NUMBER}"
            )

        max_seat = bus_capacity or BusinessRules.MAX_SEAT_NUMBER
        if number > max_seat:
            raise ValidationException(
                "seat_number",
                number,
                f"Seat number cannot exceed {max_seat}"
            )

        self._number = number
        self._bus_capacity = bus_capacity

    @property
    def number(self) -> int:
        """Get seat number."""
        return self._number

    @property
    def bus_capacity(self) -> Optional[int]:
        """Get bus capacity used for validation."""
        return self._bus_capacity

    def is_window_seat(self, seats_per_row: int = 4) -> bool:
        """
        Check if this is a window seat.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            True if it's a window seat
        """
        # Calculate position in row (0-based)
        position_in_row = (self._number - 1) % seats_per_row

        # Window seats are typically at positions 0 and (seats_per_row - 1)
        return position_in_row == 0 or position_in_row == (seats_per_row - 1)

    def is_aisle_seat(self, seats_per_row: int = 4) -> bool:
        """
        Check if this is an aisle seat.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            True if it's an aisle seat
        """
        return not self.is_window_seat(seats_per_row)

    def get_row_number(self, seats_per_row: int = 4) -> int:
        """
        Get the row number for this seat.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Row number (1-based)
        """
        return ((self._number - 1) // seats_per_row) + 1

    def get_position_in_row(self, seats_per_row: int = 4) -> int:
        """
        Get the position within the row.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Position in row (1-based)
        """
        return ((self._number - 1) % seats_per_row) + 1

    def get_seat_type(self, seats_per_row: int = 4) -> str:
        """
        Get seat type description.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Seat type ("window" or "aisle")
        """
        return "window" if self.is_window_seat(seats_per_row) else "aisle"

    def get_adjacent_seats(self, seats_per_row: int = 4) -> list['SeatNumber']:
        """
        Get adjacent seats in the same row.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            List of adjacent SeatNumber objects
        """
        row_start = ((self._number - 1) // seats_per_row) * seats_per_row + 1
        row_end = row_start + seats_per_row - 1

        adjacent = []

        # Previous seat in row
        if self._number > row_start:
            adjacent.append(SeatNumber(self._number - 1, self._bus_capacity))

        # Next seat in row
        if self._number < row_end and (not self._bus_capacity or self._number < self._bus_capacity):
            adjacent.append(SeatNumber(self._number + 1, self._bus_capacity))

        return adjacent

    def distance_from_front(self, seats_per_row: int = 4) -> int:
        """
        Calculate distance from the front of the bus.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Number of rows from the front (0-based)
        """
        return (self._number - 1) // seats_per_row

    def is_front_section(self, seats_per_row: int = 4, front_rows: int = 3) -> bool:
        """
        Check if seat is in the front section of the bus.

        Args:
            seats_per_row: Number of seats per row (default: 4)
            front_rows: Number of rows considered "front section" (default: 3)

        Returns:
            True if seat is in front section
        """
        return self.get_row_number(seats_per_row) <= front_rows

    def is_back_section(self, seats_per_row: int = 4, back_rows: int = 3) -> bool:
        """
        Check if seat is in the back section of the bus.

        Args:
            seats_per_row: Number of seats per row (default: 4)
            back_rows: Number of rows considered "back section" (default: 3)

        Returns:
            True if seat is in back section
        """
        if not self._bus_capacity:
            return False

        total_rows = (self._bus_capacity + seats_per_row - 1) // seats_per_row
        seat_row = self.get_row_number(seats_per_row)

        return seat_row > (total_rows - back_rows)

    def format_display(self, seats_per_row: int = 4) -> str:
        """
        Format seat for display purposes.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Formatted string like "Row 1, Seat A (Window)"
        """
        row = self.get_row_number(seats_per_row)
        position = self.get_position_in_row(seats_per_row)
        seat_type = self.get_seat_type(seats_per_row)

        # Convert position to letter (A, B, C, D, etc.)
        seat_letter = chr(ord('A') + position - 1)

        return f"Row {row}, Seat {seat_letter} ({seat_type.title()})"

    def __str__(self) -> str:
        """String representation."""
        return str(self._number)

    def __int__(self) -> int:
        """Integer representation."""
        return self._number

    def __lt__(self, other: 'SeatNumber') -> bool:
        """Less than comparison."""
        return self._number < other._number

    def __le__(self, other: 'SeatNumber') -> bool:
        """Less than or equal comparison."""
        return self._number <= other._number

    def __gt__(self, other: 'SeatNumber') -> bool:
        """Greater than comparison."""
        return self._number > other._number

    def __ge__(self, other: 'SeatNumber') -> bool:
        """Greater than or equal comparison."""
        return self._number >= other._number

    @classmethod
    def generate_seat_map(cls, capacity: int, seats_per_row: int = 4) -> dict:
        """
        Generate a complete seat map for a bus.

        Args:
            capacity: Bus capacity
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Dictionary with seat layout information
        """
        if capacity <= 0:
            raise ValidationException("capacity", capacity, "Capacity must be positive")

        total_rows = (capacity + seats_per_row - 1) // seats_per_row
        seat_map = {
            'capacity': capacity,
            'seats_per_row': seats_per_row,
            'total_rows': total_rows,
            'rows': []
        }

        seat_number = 1
        for row_num in range(1, total_rows + 1):
            row_data = {
                'row_number': row_num,
                'seats': []
            }

            for position in range(1, seats_per_row + 1):
                if seat_number <= capacity:
                    seat = cls(seat_number, capacity)
                    seat_info = {
                        'number': seat_number,
                        'position': position,
                        'is_window': seat.is_window_seat(seats_per_row),
                        'is_aisle': seat.is_aisle_seat(seats_per_row),
                        'display': seat.format_display(seats_per_row)
                    }
                    row_data['seats'].append(seat_info)
                    seat_number += 1
                else:
                    break

            if row_data['seats']:  # Only add rows that have seats
                seat_map['rows'].append(row_data)

        return seat_map

    @classmethod
    def from_row_and_position(
            cls,
            row: int,
            position: int,
            seats_per_row: int = 4,
            bus_capacity: Optional[int] = None
    ) -> 'SeatNumber':
        """
        Create SeatNumber from row and position.

        Args:
            row: Row number (1-based)
            position: Position in row (1-based)
            seats_per_row: Number of seats per row (default: 4)
            bus_capacity: Bus capacity for validation

        Returns:
            SeatNumber object
        """
        if row < 1:
            raise ValidationException("row", row, "Row number must be at least 1")

        if position < 1 or position > seats_per_row:
            raise ValidationException(
                "position",
                position,
                f"Position must be between 1 and {seats_per_row}"
            )

        seat_number = (row - 1) * seats_per_row + position
        return cls(seat_number, bus_capacity)