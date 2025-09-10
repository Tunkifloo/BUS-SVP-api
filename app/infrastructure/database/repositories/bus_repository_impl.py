"""
Bus repository implementation.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.entities.bus import Bus
from ....domain.repositories.bus_repository import BusRepository
from ....shared.constants import BusStatus
from ..models.bus_model import BusModel
from .base_repository import BaseRepository
from ....shared.decorators import log_execution


class BusRepositoryImpl(BaseRepository[Bus, BusModel], BusRepository):
    """Bus repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BusModel)

    def _model_to_entity(self, model: BusModel) -> Bus:
        """Convert model to entity."""
        return Bus(
            company_id=model.company_id,
            plate_number=model.plate_number,
            capacity=model.capacity,
            model=model.model,
            status=BusStatus(model.status),
            features=model.features or [],
            year=model.year,
            bus_id=model.id
        )

    def _entity_to_model(self, entity: Bus) -> BusModel:
        """Convert entity to model."""
        return BusModel(
            id=entity.id,
            company_id=entity.company_id,
            plate_number=entity.plate_number,
            capacity=entity.capacity,
            model=entity.model,
            status=entity.status.value,
            features=entity.features,
            year=entity.year,
            mileage=entity.mileage,
            last_maintenance_date=entity.last_maintenance_date,
            next_maintenance_due=entity.next_maintenance_due
        )

    @log_execution()
    async def save(self, bus: Bus) -> Bus:
        """Save bus entity."""
        model = self._entity_to_model(bus)
        saved_model = await self.save_model(model)
        return self._model_to_entity(saved_model)

    @log_execution()
    async def find_by_id(self, bus_id: str) -> Optional[Bus]:
        """Find bus by ID."""
        model = await self.find_by_id_model(bus_id)
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_plate_number(self, plate_number: str) -> Optional[Bus]:
        """Find bus by plate number."""
        result = await self._session.execute(
            select(BusModel).where(BusModel.plate_number == plate_number)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_company(self, company_id: str, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find buses by company."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"company_id": company_id}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find all buses with pagination."""
        models = await self.find_all_models(limit=limit, offset=offset)
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_available_for_service(self, limit: int = 100, offset: int = 0) -> List[Bus]:
        """Find buses available for service."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"status": "active"}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def update(self, bus: Bus) -> Bus:
        """Update bus entity."""
        existing_model = await self.find_by_id_model(bus.id)
        if not existing_model:
            raise ValueError(f"Bus with id {bus.id} not found")

        # Update model fields
        existing_model.company_id = bus.company_id
        existing_model.plate_number = bus.plate_number
        existing_model.capacity = bus.capacity
        existing_model.model = bus.model
        existing_model.status = bus.status.value
        existing_model.features = bus.features
        existing_model.year = bus.year
        existing_model.mileage = bus.mileage
        existing_model.last_maintenance_date = bus.last_maintenance_date
        existing_model.next_maintenance_due = bus.next_maintenance_due

        updated_model = await self.update_model(existing_model)
        return self._model_to_entity(updated_model)

    @log_execution()
    async def delete(self, bus_id: str) -> bool:
        """Delete bus by ID."""
        return await self.delete_model(bus_id)

    @log_execution()
    async def exists_by_plate_number(self, plate_number: str) -> bool:
        """Check if bus exists by plate number."""
        result = await self._session.execute(
            select(BusModel.id).where(BusModel.plate_number == plate_number)
        )
        return result.scalar_one_or_none() is not None

    @log_execution()
    async def count_by_company(self, company_id: str) -> int:
        """Count buses by company."""
        return await self.count_models(filters={"company_id": company_id})

    @log_execution()
    async def count_total(self) -> int:
        """Count total buses."""
        return await self.count_models()
