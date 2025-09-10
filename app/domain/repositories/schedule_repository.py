"""
Schedule repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..entities.schedule import Schedule


class ScheduleRepository(ABC):
    """Abstract repository for Schedule entities."""

    @abstractmethod
    async def save(self, schedule: Schedule) -> Schedule:
        """Save schedule entity."""
        pass

    @abstractmethod
    async def find_by_id(self, schedule_id: str) -> Optional[Schedule]:
        """Find schedule by ID."""
        pass

    @abstractmethod
    async def find_by_route(
        self,
        route_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Schedule]:
        """Find schedules by route."""
        pass

    @abstractmethod
    async def find_by_bus(
        self,
        bus_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Schedule]:
        """Find schedules by bus."""
        pass

    @abstractmethod
    async def find_by_date_range(
        self,
        start_date: str,
        end_date: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Schedule]:
        """Find schedules within date range."""
        pass

    @abstractmethod
    async def find_available_schedules(
        self,
        route_id: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Schedule]:
        """Find schedules with available seats."""
        pass

    @abstractmethod
    async def search_schedules(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search schedules with route and company information."""
        pass

    @abstractmethod
    async def find_conflicting_schedules(
        self,
        bus_id: str,
        date: str,
        departure_time: str,
        arrival_time: str,
        exclude_schedule_id: Optional[str] = None
    ) -> List[Schedule]:
        """Find conflicting schedules for a bus."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Schedule]:
        """Find all schedules with pagination."""
        pass

    @abstractmethod
    async def update(self, schedule: Schedule) -> Schedule:
        """Update schedule entity."""
        pass

    @abstractmethod
    async def delete(self, schedule_id: str) -> bool:
        """Delete schedule by ID."""
        pass

    @abstractmethod
    async def count_by_route(self, route_id: str) -> int:
        """Count schedules by route."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total schedules."""
        pass