"""
Route repository implementation - COMPLETE VERSION.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.entities.route import Route
from ....domain.repositories.route_repository import RouteRepository
from ....shared.constants import RouteStatus
from ..models.route_model import RouteModel
from .base_repository import BaseRepository
from ....shared.decorators import log_execution


class RouteRepositoryImpl(BaseRepository[Route, RouteModel], RouteRepository):
    """Route repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RouteModel)

    def _model_to_entity(self, model: RouteModel) -> Route:
        """Convert model to entity."""
        entity = Route(
            company_id=model.company_id,
            origin=model.origin,
            destination=model.destination,
            price=model.price,
            duration=model.duration,
            status=RouteStatus(model.status),
            distance_km=model.distance_km,
            description=model.description,
            route_id=model.id
        )

        # Set additional properties that aren't in constructor
        entity._total_bookings = model.total_bookings
        entity._popularity_score = model.popularity_score
        entity._created_at = model.created_at
        entity._updated_at = model.updated_at

        return entity

    def _entity_to_model(self, entity: Route) -> RouteModel:
        """Convert entity to model."""
        return RouteModel(
            id=entity.id,
            company_id=entity.company_id,
            origin=entity.origin,
            destination=entity.destination,
            price=entity.price.to_float(),
            duration=entity.duration,
            status=entity.status.value,
            distance_km=entity.distance_km,
            description=entity.description,
            total_bookings=entity.total_bookings,
            popularity_score=entity.popularity_score
        )

    @log_execution()
    async def save(self, route: Route) -> Route:
        """Save route entity."""
        model = self._entity_to_model(route)
        saved_model = await self.save_model(model)
        return self._model_to_entity(saved_model)

    @log_execution()
    async def find_by_id(self, route_id: str) -> Optional[Route]:
        """Find route by ID."""
        model = await self.find_by_id_model(route_id)
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_company(self, company_id: str, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find routes by company."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"company_id": company_id},
            order_by="created_at"
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find all routes with pagination."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            order_by="created_at"
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_active(self, limit: int = 100, offset: int = 0) -> List[Route]:
        """Find active routes."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"status": "active"},
            order_by="popularity_score"
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def search_routes(
            self,
            origin: Optional[str] = None,
            destination: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[Route]:
        """Search routes by origin and destination."""
        query = select(RouteModel).where(RouteModel.status == "active")

        if origin:
            query = query.where(RouteModel.origin.ilike(f"%{origin}%"))

        if destination:
            query = query.where(RouteModel.destination.ilike(f"%{destination}%"))

        query = query.order_by(RouteModel.popularity_score.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_origin_destination(
            self,
            origin: str,
            destination: str,
            company_id: Optional[str] = None
    ) -> List[Route]:
        """Find routes by exact origin and destination."""
        query = select(RouteModel).where(
            RouteModel.origin == origin,
            RouteModel.destination == destination,
            RouteModel.status == "active"
        )

        if company_id:
            query = query.where(RouteModel.company_id == company_id)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_popular_routes(self, limit: int = 10) -> List[Route]:
        """Find most popular routes."""
        query = select(RouteModel).where(
            RouteModel.status == "active"
        ).order_by(
            RouteModel.popularity_score.desc()
        ).limit(limit)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def update(self, route: Route) -> Route:
        """Update route entity."""
        existing_model = await self.find_by_id_model(route.id)
        if not existing_model:
            raise ValueError(f"Route with id {route.id} not found")

        # Update model fields
        existing_model.company_id = route.company_id
        existing_model.origin = route.origin
        existing_model.destination = route.destination
        existing_model.price = route.price.to_float()
        existing_model.duration = route.duration
        existing_model.status = route.status.value
        existing_model.distance_km = route.distance_km
        existing_model.description = route.description
        existing_model.total_bookings = route.total_bookings
        existing_model.popularity_score = route.popularity_score

        updated_model = await self.update_model(existing_model)
        return self._model_to_entity(updated_model)

    @log_execution()
    async def delete(self, route_id: str) -> bool:
        """Delete route by ID."""
        return await self.delete_model(route_id)

    @log_execution()
    async def get_unique_cities(self) -> Dict[str, List[str]]:
        """Get unique origin and destination cities."""
        try:
            # Get unique origins
            origin_result = await self._session.execute(
                select(RouteModel.origin).distinct().where(RouteModel.status == "active")
            )
            origins = [row[0] for row in origin_result.fetchall()]

            # Get unique destinations
            dest_result = await self._session.execute(
                select(RouteModel.destination).distinct().where(RouteModel.status == "active")
            )
            destinations = [row[0] for row in dest_result.fetchall()]

            return {
                "origins": sorted(origins),
                "destinations": sorted(destinations)
            }
        except Exception as e:
            # Return empty lists if there's an error
            return {
                "origins": [],
                "destinations": []
            }

    @log_execution()
    async def count_by_company(self, company_id: str) -> int:
        """Count routes by company."""
        return await self.count_models(filters={"company_id": company_id})

    @log_execution()
    async def count_total(self) -> int:
        """Count total routes."""
        return await self.count_models()