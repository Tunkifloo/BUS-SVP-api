"""
Create route use case.
"""
from typing import Dict, Any, Optional
from app.domain.entities.route import Route
from app.domain.repositories.route_repository import RouteRepository
from app.domain.repositories.company_repository import CompanyRepository
from app.core.exceptions import ValidationException
from app.shared.decorators import log_execution


class CreateRouteUseCase:
    """Use case for creating new routes."""

    def __init__(
        self,
        route_repository: RouteRepository,
        company_repository: CompanyRepository
    ):
        self._route_repository = route_repository
        self._company_repository = company_repository

    @log_execution(log_duration=True)
    async def execute(
        self,
        company_id: str,
        origin: str,
        destination: str,
        price: float,
        duration: str,
        distance_km: Optional[int] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute create route use case.

        Args:
            company_id: Company ID
            origin: Origin city
            destination: Destination city
            price: Route price
            duration: Trip duration
            distance_km: Distance in kilometers (optional)
            description: Route description (optional)

        Returns:
            Created route information

        Raises:
            ValidationException: If company doesn't exist
        """
        # Validate company exists
        company = await self._company_repository.find_by_id(company_id)
        if not company:
            raise ValidationException("company_id", company_id, "Company not found")

        if not company.can_operate():
            raise ValidationException("company_id", company_id, "Company cannot operate")

        # Create route entity
        route = Route(
            company_id=company_id,
            origin=origin,
            destination=destination,
            price=price,
            duration=duration,
            distance_km=distance_km,
            description=description
        )

        # Save route
        saved_route = await self._route_repository.save(route)

        return {
            "id": saved_route.id,
            "company_id": saved_route.company_id,
            "origin": saved_route.origin,
            "destination": saved_route.destination,
            "price": saved_route.price.to_float(),
            "duration": saved_route.duration,
            "distance_km": saved_route.distance_km,
            "description": saved_route.description,
            "status": saved_route.status.value,
            "created_at": saved_route.created_at.isoformat()
        }