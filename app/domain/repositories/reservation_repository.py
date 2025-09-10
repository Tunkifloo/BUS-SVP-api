"""
Reservation repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.reservation import Reservation


class ReservationRepository(ABC):
    """Abstract repository for Reservation entities."""

    @abstractmethod
    async def save(self, reservation: Reservation) -> Reservation:
        """Save reservation entity."""
        pass

    @abstractmethod
    async def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Find reservation by ID."""
        pass

    @abstractmethod
    async def find_by_code(self, reservation_code: str) -> Optional[Reservation]:
        """Find reservation by reservation code."""
        pass

    @abstractmethod
    async def find_by_user(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Reservation]:
        """Find reservations by user."""
        pass

    @abstractmethod
    async def find_by_schedule(
        self,
        schedule_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Reservation]:
        """Find reservations by schedule."""
        pass

    @abstractmethod
    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Reservation]:
        """Find reservations by status."""
        pass

    @abstractmethod
    async def find_active_by_schedule(self, schedule_id: str) -> List[Reservation]:
        """Find active reservations for a schedule."""
        pass

    @abstractmethod
    async def find_user_reservations_with_details(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find user reservations with schedule, route, and company details."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Reservation]:
        """Find all reservations with pagination."""
        pass

    @abstractmethod
    async def update(self, reservation: Reservation) -> Reservation:
        """Update reservation entity."""
        pass

    @abstractmethod
    async def delete(self, reservation_id: str) -> bool:
        """Delete reservation by ID."""
        pass

    @abstractmethod
    async def exists_seat_reservation(
        self,
        schedule_id: str,
        seat_number: int
    ) -> bool:
        """Check if seat is already reserved for a schedule."""
        pass

    @abstractmethod
    async def count_by_schedule(self, schedule_id: str) -> int:
        """Count reservations by schedule."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """Count reservations by user."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total reservations."""
        pass