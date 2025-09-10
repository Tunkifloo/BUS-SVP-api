"""
Schedule repository implementation.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.entities.schedule import Schedule
from ....domain.repositories.schedule_repository import ScheduleRepository
from ....shared.constants import ScheduleStatus
from ..models.schedule_model import ScheduleModel
from ..models.route_model import RouteModel
from ..models.company_model import CompanyModel
from ..models.bus_model import BusModel
from .base_repository import BaseRepository
from ....shared.decorators import log_execution


class ScheduleRepositoryImpl(BaseRepository[Schedule, ScheduleModel], ScheduleRepository):
    """Schedule repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ScheduleModel)

    def _model_to_entity(self, model: ScheduleModel) -> Schedule:
        """Convert model to entity."""
        schedule = Schedule(
            route_id=model.route_id,
            bus_id=model.bus_id,
            departure_time=model.departure_time,
            arrival_time=model.arrival_time,
            date=model.date,
            available_seats=model.available_seats,
            status=ScheduleStatus(model.status),
            schedule_id=model.id
        )

        # Set internal state
        schedule._occupied_seats = set(model.occupied_seats or [])
        schedule._reserved_seats = set(model.reserved_seats or [])
        schedule._total_capacity = model.total_capacity
        schedule._actual_departure_time = model.actual_departure_time
        schedule._actual_arrival_time = model.actual_arrival_time

        return schedule

    def _entity_to_model(self, entity: Schedule) -> ScheduleModel:
        """Convert entity to model."""
        return ScheduleModel(
            id=entity.id,
            route_id=entity.route_id,
            bus_id=entity.bus_id,
            departure_time=entity.departure_time,
            arrival_time=entity.arrival_time,
            date=entity.date,
            available_seats=entity.available_seats,
            total_capacity=entity.total_capacity,
            status=entity.status.value,
            occupied_seats=list(entity.occupied_seats),
            reserved_seats=list(entity.reserved_seats),
            actual_departure_time=entity.actual_departure_time,
            actual_arrival_time=entity.actual_arrival_time
        )

    @log_execution()
    async def save(self, schedule: Schedule) -> Schedule:
        """Save schedule entity."""
        model = self._entity_to_model(schedule)
        saved_model = await self.save_model(model)
        return self._model_to_entity(saved_model)

    @log_execution()
    async def find_by_id(self, schedule_id: str) -> Optional[Schedule]:
        """Find schedule by ID."""
        model = await self.find_by_id_model(schedule_id)
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_route(self, route_id: str, limit: int = 100, offset: int = 0) -> List[Schedule]:
        """Find schedules by route."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"route_id": route_id}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_bus(self, bus_id: str, limit: int = 100, offset: int = 0) -> List[Schedule]:
        """Find schedules by bus."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"bus_id": bus_id}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_date_range(
            self,
            start_date: str,
            end_date: str,
            limit: int = 100,
            offset: int = 0
    ) -> List[Schedule]:
        """Find schedules within date range."""
        query = select(ScheduleModel).where(
            and_(
                ScheduleModel.date >= start_date,
                ScheduleModel.date <= end_date
            )
        ).order_by(ScheduleModel.date, ScheduleModel.departure_time).limit(limit).offset(offset)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_available_schedules(
            self,
            route_id: Optional[str] = None,
            date: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[Schedule]:
        """Find schedules with available seats."""
        query = select(ScheduleModel).where(
            ScheduleModel.available_seats > 0,
            ScheduleModel.status == "scheduled"
        )

        if route_id:
            query = query.where(ScheduleModel.route_id == route_id)

        if date:
            query = query.where(ScheduleModel.date == date)

        query = query.order_by(ScheduleModel.date, ScheduleModel.departure_time).limit(limit).offset(offset)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def search_schedules(
            self,
            origin: Optional[str] = None,
            destination: Optional[str] = None,
            date: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search schedules with route and company information."""
        query = select(
            ScheduleModel,
            RouteModel,
            CompanyModel,
            BusModel
        ).join(
            RouteModel, ScheduleModel.route_id == RouteModel.id
        ).join(
            CompanyModel, RouteModel.company_id == CompanyModel.id
        ).join(
            BusModel, ScheduleModel.bus_id == BusModel.id
        ).where(
            ScheduleModel.available_seats > 0,
            ScheduleModel.status == "scheduled",
            RouteModel.status == "active"
        )

        if origin:
            query = query.where(RouteModel.origin.ilike(f"%{origin}%"))

        if destination:
            query = query.where(RouteModel.destination.ilike(f"%{destination}%"))

        if date:
            query = query.where(ScheduleModel.date == date)

        query = query.order_by(ScheduleModel.date, ScheduleModel.departure_time).limit(limit).offset(offset)

        result = await self._session.execute(query)

        schedules_with_details = []
        for schedule_model, route_model, company_model, bus_model in result:
            schedules_with_details.append({
                "schedule": self._model_to_entity(schedule_model),
                "route": route_model,
                "company": company_model,
                "bus": bus_model
            })

        return schedules_with_details

    @log_execution()
    async def find_conflicting_schedules(
            self,
            bus_id: str,
            date: str,
            departure_time: str,
            arrival_time: str,
            exclude_schedule_id: Optional[str] = None
    ) -> List[Schedule]:
        """Find conflicting schedules for a bus."""
        query = select(ScheduleModel).where(
            ScheduleModel.bus_id == bus_id,
            ScheduleModel.date == date,
            ScheduleModel.status.in_(["scheduled", "in_progress"]),
            or_(
                # New schedule starts during existing schedule
                and_(
                    ScheduleModel.departure_time <= departure_time,
                    ScheduleModel.arrival_time > departure_time
                ),
                # New schedule ends during existing schedule
                and_(
                    ScheduleModel.departure_time < arrival_time,
                    ScheduleModel.arrival_time >= arrival_time
                ),
                # New schedule encompasses existing schedule
                and_(
                    departure_time <= ScheduleModel.departure_time,
                    arrival_time >= ScheduleModel.arrival_time
                )
            )
        )

        if exclude_schedule_id:
            query = query.where(ScheduleModel.id != exclude_schedule_id)

        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Schedule]:
        """Find all schedules with pagination."""
        models = await self.find_all_models(limit=limit, offset=offset)
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def update(self, schedule: Schedule) -> Schedule:
        """Update schedule entity."""
        existing_model = await self.find_by_id_model(schedule.id)
        if not existing_model:
            raise ValueError(f"Schedule with id {schedule.id} not found")

        # Update model fields
        existing_model.route_id = schedule.route_id
        existing_model.bus_id = schedule.bus_id
        existing_model.departure_time = schedule.departure_time
        existing_model.arrival_time = schedule.arrival_time
        existing_model.date = schedule.date
        existing_model.available_seats = schedule.available_seats
        existing_model.total_capacity = schedule.total_capacity
        existing_model.status = schedule.status.value
        existing_model.occupied_seats = list(schedule.occupied_seats)
        existing_model.reserved_seats = list(schedule.reserved_seats)
        existing_model.actual_departure_time = schedule.actual_departure_time
        existing_model.actual_arrival_time = schedule.actual_arrival_time

        updated_model = await self.update_model(existing_model)
        return self._model_to_entity(updated_model)

    @log_execution()
    async def delete(self, schedule_id: str) -> bool:
        """Delete schedule by ID."""
        return await self.delete_model(schedule_id)

    @log_execution()
    async def count_by_route(self, route_id: str) -> int:
        """Count schedules by route."""
        return await self.count_models(filters={"route_id": route_id})

    @log_execution()
    async def count_total(self) -> int:
        """Count total schedules."""
        return await self.count_models()