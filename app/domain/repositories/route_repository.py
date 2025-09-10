"""
Route repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.route import Route


class RouteRepository(ABC):
    """Abstract repository for Route entities."""

    @abstractmethod
    async def save(self, route: Route) -> Route:
        """Save route entity."""
        pass

    @abstractmethod
    async def find_by_id(self, route_id: str) -> Optional[Route]:
        """Find route by ID."""
        pass

    @abstractmethod
    async def find_by_company(self, company_id: str, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find routes by company."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find all routes with pagination."""
        pass

    @abstractmethod
    async def find_active(self, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find active routes."""
        pass

    @abstractmethod
    async def search_routes(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Route]:
        """Search routes by origin and destination."""
        pass

    @abstractmethod
    async def find_by_origin_destination(
        self,
        origin: str,
        destination: str,
        company_id: Optional[str] = None
    ) -> List[Route]:
        """Find routes by exact origin and destination."""
        pass

    @abstractmethod
    async def find_popular_routes(self, limit: int = 10) -> List[Route]:
        """Find most popular routes."""
        pass

    @abstractmethod
    async def update(self, route: Route) -> Route:
        """Update route entity."""
        pass

    @abstractmethod
    async def delete(self, route_id: str) -> bool:
        """Delete route by ID."""
        pass

    @abstractmethod
    async def get_unique_cities(self) -> Dict[str, List[str]]:
        """Get unique origin and destination cities."""
        pass

    @abstractmethod
    async def count_by_company(self, company_id: str) -> int:
        """Count routes by company."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total routes."""
        pass