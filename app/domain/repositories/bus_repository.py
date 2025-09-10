"""
Bus repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.bus import Bus


class BusRepository(ABC):
    """Abstract repository for Bus entities."""

    @abstractmethod
    async def save(self, bus: Bus) -> Bus:
        """Save bus entity."""
        pass

    @abstractmethod
    async def find_by_id(self, bus_id: str) -> Optional[Bus]:
        """Find bus by ID."""
        pass

    @abstractmethod
    async def find_by_plate_number(self, plate_number: str) -> Optional[Bus]:
        """Find bus by plate number."""
        pass

    @abstractmethod
    async def find_by_company(self, company_id: str, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find buses by company."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find all buses with pagination."""
        pass

    @abstractmethod
    async def find_available_for_service(self, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find buses available for service."""
        pass

    @abstractmethod
    async def update(self, bus: Bus) -> Bus:
        """Update bus entity."""
        pass

    @abstractmethod
    async def delete(self, bus_id: str) -> bool:
        """Delete bus by ID."""
        pass

    @abstractmethod
    async def exists_by_plate_number(self, plate_number: str) -> bool:
        """Check if bus exists by plate number."""
        pass

    @abstractmethod
    async def count_by_company(self, company_id: str) -> int:
        """Count buses by company."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total buses."""
        pass