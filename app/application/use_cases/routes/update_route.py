"""
Update route use case.
"""
from typing import Dict, Any, Optional
from app.domain.repositories.route_repository import RouteRepository
from app.core.exceptions import EntityNotFoundException
from app.shared.decorators import log_execution


class UpdateRouteUseCase:
    """Use case for updating routes."""

    def __init__(self, route_repository: RouteRepository):
        self._route_repository = route_repository

    @log_execution(log_duration=True)
    async def execute(
        self,
        route_id: str,
        price: Optional[float] = None,
        duration: Optional[str] = None,
        distance_km: Optional[int] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute update route use case.

        Args:
            route_id: Route ID
            price: New price (optional)
            duration: New duration (optional)
            distance_km: New distance (optional)
            description: New description (optional)

        Returns:
            Updated route information

        Raises:
            EntityNotFoundException: If route doesn't exist
        """
        # Find route
        route = await self._route_repository.find_by_id(route_id)
        if not route:
            raise EntityNotFoundException("Route", route_id)

        # Update price if provided
        if price is not None:
            route.update_price(price)

        # Update basic info if provided
        route.update_basic_info(
            duration=duration,
            distance_km=distance_km,
            description=description
        )

        # Save updated route
        updated_route = await self._route_repository.update(route)

        return {
            "id": updated_route.id,
            "company_id": updated_route.company_id,
            "origin": updated_route.origin,
            "destination": updated_route.destination,
            "price": updated_route.price.to_float(),
            "duration": updated_route.duration,
            "distance_km": updated_route.distance_km,
            "description": updated_route.description,
            "status": updated_route.status.value,
            "updated_at": updated_route.updated_at.isoformat()
        }