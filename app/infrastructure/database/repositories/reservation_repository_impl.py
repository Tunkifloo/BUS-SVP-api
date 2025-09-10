# app/infrastructure/database/repositories/reservation_repository_impl.py
"""
Reservation repository implementation - CORRECTED VERSION.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.entities.reservation import Reservation
from ....domain.repositories.reservation_repository import ReservationRepository
from ....shared.constants import ReservationStatus
from ..models.reservation_model import ReservationModel
from ..models.schedule_model import ScheduleModel
from ..models.route_model import RouteModel
from ..models.company_model import CompanyModel
from ..models.bus_model import BusModel
from ..models.user_model import UserModel
from .base_repository import BaseRepository
from ....shared.decorators import log_execution


class ReservationRepositoryImpl(BaseRepository[Reservation, ReservationModel], ReservationRepository):
    """Reservation repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ReservationModel)

    def _model_to_entity(self, model: ReservationModel) -> Reservation:
        """Convert model to entity."""
        return Reservation(
            user_id=model.user_id,
            schedule_id=model.schedule_id,
            seat_number=model.seat_number,
            bus_capacity=50,  # Default capacity, should be fetched from bus
            price=model.price,
            status=ReservationStatus(model.status),
            reservation_code=model.reservation_code,
            reservation_id=model.id
        )

    def _entity_to_model(self, entity: Reservation) -> ReservationModel:
        """Convert entity to model."""
        return ReservationModel(
            id=entity.id,
            user_id=entity.user_id,
            schedule_id=entity.schedule_id,
            seat_number=entity.seat_number.number,
            price=entity.price.to_float(),
            status=entity.status.value,
            reservation_code=entity.reservation_code,
            cancellation_reason=entity.cancellation_reason,
            cancelled_at=entity.cancelled_at,
            completed_at=entity.completed_at
        )

    @log_execution()
    async def save(self, reservation: Reservation) -> Reservation:
        """Save reservation entity."""
        model = self._entity_to_model(reservation)
        saved_model = await self.save_model(model)
        return self._model_to_entity(saved_model)

    @log_execution()
    async def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Find reservation by ID."""
        model = await self.find_by_id_model(reservation_id)
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_code(self, reservation_code: str) -> Optional[Reservation]:
        """Find reservation by reservation code."""
        result = await self._session.execute(
            select(ReservationModel).where(ReservationModel.reservation_code == reservation_code)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Reservation]:
        """Find reservations by user."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"user_id": user_id},
            order_by="created_at"
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_schedule(self, schedule_id: str, limit: int = 100, offset: int = 0) -> List[Reservation]:
        """Find reservations by schedule."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"schedule_id": schedule_id}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_status(self, status: str, limit: int = 100, offset: int = 0) -> List[Reservation]:
        """Find reservations by status."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"status": status}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_active_by_schedule(self, schedule_id: str) -> List[Reservation]:
        """Find active reservations for a schedule."""
        models = await self.find_all_models(
            filters={"schedule_id": schedule_id, "status": "active"}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_user_reservations_with_details(
            self,
            user_id: str,
            limit: int = 100,
            offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find user reservations with schedule, route, and company details."""
        query = select(
            ReservationModel,
            ScheduleModel,
            RouteModel,
            CompanyModel,
            BusModel
        ).join(
            ScheduleModel, ReservationModel.schedule_id == ScheduleModel.id
        ).join(
            RouteModel, ScheduleModel.route_id == RouteModel.id
        ).join(
            CompanyModel, RouteModel.company_id == CompanyModel.id
        ).join(
            BusModel, ScheduleModel.bus_id == BusModel.id
        ).where(
            ReservationModel.user_id == user_id
        ).order_by(
            ReservationModel.created_at.desc()
        ).limit(limit).offset(offset)

        result = await self._session.execute(query)

        reservations_with_details = []
        for reservation_model, schedule_model, route_model, company_model, bus_model in result:
            reservations_with_details.append({
                "id": reservation_model.id,
                "user_id": reservation_model.user_id,
                "schedule_id": reservation_model.schedule_id,
                "seat_number": reservation_model.seat_number,
                "price": reservation_model.price,
                "status": reservation_model.status,
                "reservation_code": reservation_model.reservation_code,
                "cancellation_reason": reservation_model.cancellation_reason,
                "cancelled_at": reservation_model.cancelled_at.isoformat() if reservation_model.cancelled_at else None,
                "completed_at": reservation_model.completed_at.isoformat() if reservation_model.completed_at else None,
                "created_at": reservation_model.created_at.isoformat(),
                "schedule": {
                    "id": schedule_model.id,
                    "departure_time": schedule_model.departure_time,
                    "arrival_time": schedule_model.arrival_time,
                    "date": schedule_model.date
                },
                "route": {
                    "id": route_model.id,
                    "origin": route_model.origin,
                    "destination": route_model.destination,
                    "duration": route_model.duration,
                    "price": route_model.price
                },
                "company": {
                    "id": company_model.id,
                    "name": company_model.name,
                    "phone": company_model.phone,
                    "email": company_model.email
                },
                "bus": {
                    "id": bus_model.id,
                    "plate_number": bus_model.plate_number,
                    "model": bus_model.model
                }
            })

        return reservations_with_details

    @log_execution()
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Reservation]:
        """Find all reservations with pagination."""
        models = await self.find_all_models(limit=limit, offset=offset)
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def update(self, reservation: Reservation) -> Reservation:
        """Update reservation entity."""
        existing_model = await self.find_by_id_model(reservation.id)
        if not existing_model:
            raise ValueError(f"Reservation with id {reservation.id} not found")

        # Update model fields
        existing_model.user_id = reservation.user_id
        existing_model.schedule_id = reservation.schedule_id
        existing_model.seat_number = reservation.seat_number.number
        existing_model.price = reservation.price.to_float()
        existing_model.status = reservation.status.value
        existing_model.reservation_code = reservation.reservation_code
        existing_model.cancellation_reason = reservation.cancellation_reason
        existing_model.cancelled_at = reservation.cancelled_at
        existing_model.completed_at = reservation.completed_at

        updated_model = await self.update_model(existing_model)
        return self._model_to_entity(updated_model)

    @log_execution()
    async def delete(self, reservation_id: str) -> bool:
        """Delete reservation by ID."""
        return await self.delete_model(reservation_id)

    @log_execution()
    async def exists_seat_reservation(self, schedule_id: str, seat_number: int) -> bool:
        """Check if seat is already reserved for a schedule."""
        result = await self._session.execute(
            select(ReservationModel.id).where(
                and_(
                    ReservationModel.schedule_id == schedule_id,
                    ReservationModel.seat_number == seat_number,
                    ReservationModel.status == "active"
                )
            )
        )
        return result.scalar_one_or_none() is not None

    @log_execution()
    async def count_by_schedule(self, schedule_id: str) -> int:
        """Count reservations by schedule."""
        return await self.count_models(filters={"schedule_id": schedule_id})

    @log_execution()
    async def count_by_user(self, user_id: str) -> int:
        """Count reservations by user."""
        return await self.count_models(filters={"user_id": user_id})

    @log_execution()
    async def count_total(self) -> int:
        """Count total reservations."""
        return await self.count_models()