"""
Manage schedules use case.
"""
from typing import List, Dict, Any, Optional
from app.domain.entities.schedule import Schedule
from app.domain.repositories.schedule_repository import ScheduleRepository
from app.domain.repositories.route_repository import RouteRepository
from app.domain.repositories.bus_repository import BusRepository
from app.core.exceptions import EntityNotFoundException, ScheduleConflictException
from app.shared.decorators import log_execution


class ManageSchedulesUseCase:
    """Use case for managing schedules."""

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        route_repository: RouteRepository,
        bus_repository: BusRepository
    ):
        self._schedule_repository = schedule_repository
        self._route_repository = route_repository
        self._bus_repository = bus_repository

    @log_execution(log_duration=True)
    async def create_schedule(
        self,
        route_id: str,
        bus_id: str,
        departure_time: str,
        arrival_time: str,
        date: str,
        available_seats: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new schedule.

        Args:
            route_id: Route ID
            bus_id: Bus ID
            departure_time: Departure time
            arrival_time: Arrival time
            date: Travel date
            available_seats: Available seats (optional, defaults to bus capacity)

        Returns:
            Created schedule information

        Raises:
            EntityNotFoundException: If route or bus doesn't exist
            ScheduleConflictException: If bus has conflicting schedule
        """
        # Validate route exists
        route = await self._route_repository.find_by_id(route_id)
        if not route:
            raise EntityNotFoundException("Route", route_id)

        # Validate bus exists and is available
        bus = await self._bus_repository.find_by_id(bus_id)
        if not bus:
            raise EntityNotFoundException("Bus", bus_id)

        if not bus.is_available_for_service():
            raise EntityNotFoundException("Bus", bus_id)  # Treat unavailable as not found

        # Check for schedule conflicts
        conflicts = await self._schedule_repository.find_conflicting_schedules(
            bus_id=bus_id,
            date=date,
            departure_time=departure_time,
            arrival_time=arrival_time
        )

        if conflicts:
            raise ScheduleConflictException(bus_id, conflicts[0].id)

        # Set available seats to bus capacity if not provided
        if available_seats is None:
            available_seats = bus.capacity

        # Create schedule entity
        schedule = Schedule(
            route_id=route_id,
            bus_id=bus_id,
            departure_time=departure_time,
            arrival_time=arrival_time,
            date=date,
            available_seats=available_seats
        )

        # Save schedule
        saved_schedule = await self._schedule_repository.save(schedule)

        return {
            "id": saved_schedule.id,
            "route_id": saved_schedule.route_id,
            "bus_id": saved_schedule.bus_id,
            "departure_time": saved_schedule.departure_time,
            "arrival_time": saved_schedule.arrival_time,
            "date": saved_schedule.date,
            "available_seats": saved_schedule.available_seats,
            "total_capacity": saved_schedule.total_capacity,
            "status": saved_schedule.status.value,
            "created_at": saved_schedule.created_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def update_schedule(
        self,
        schedule_id: str,
        departure_time: Optional[str] = None,
        arrival_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update schedule times.

        Args:
            schedule_id: Schedule ID
            departure_time: New departure time (optional)
            arrival_time: New arrival time (optional)

        Returns:
            Updated schedule information

        Raises:
            EntityNotFoundException: If schedule doesn't exist
        """
        # Find schedule
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise EntityNotFoundException("Schedule", schedule_id)

        # Update schedule times
        schedule.update_schedule_times(
            departure_time=departure_time,
            arrival_time=arrival_time
        )

        # Save updated schedule
        updated_schedule = await self._schedule_repository.update(schedule)

        return {
            "id": updated_schedule.id,
            "route_id": updated_schedule.route_id,
            "bus_id": updated_schedule.bus_id,
            "departure_time": updated_schedule.departure_time,
            "arrival_time": updated_schedule.arrival_time,
            "date": updated_schedule.date,
            "available_seats": updated_schedule.available_seats,
            "total_capacity": updated_schedule.total_capacity,
            "status": updated_schedule.status.value,
            "updated_at": updated_schedule.updated_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def get_schedules(
        self,
        route_id: Optional[str] = None,
        bus_id: Optional[str] = None,
        date: Optional[str] = None,
        available_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get list of schedules.

        Args:
            route_id: Filter by route (optional)
            bus_id: Filter by bus (optional)
            date: Filter by date (optional)
            available_only: Only return available schedules
            limit: Limit results
            offset: Offset for pagination

        Returns:
            List of schedules
        """
        if available_only:
            schedules = await self._schedule_repository.find_available_schedules(
                route_id=route_id,
                date=date,
                limit=limit,
                offset=offset
            )
        elif route_id:
            schedules = await self._schedule_repository.find_by_route(
                route_id, limit=limit, offset=offset
            )
        elif bus_id:
            schedules = await self._schedule_repository.find_by_bus(
                bus_id, limit=limit, offset=offset
            )
        else:
            schedules = await self._schedule_repository.find_all(limit=limit, offset=offset)

        return [
            {
                "id": schedule.id,
                "route_id": schedule.route_id,
                "bus_id": schedule.bus_id,
                "departure_time": schedule.departure_time,
                "arrival_time": schedule.arrival_time,
                "date": schedule.date,
                "available_seats": schedule.available_seats,
                "total_capacity": schedule.total_capacity,
                "status": schedule.status.value,
                "occupancy_rate": schedule.get_occupancy_rate(),
                "created_at": schedule.created_at.isoformat()
            }
            for schedule in schedules
        ]

    @log_execution(log_duration=True)
    async def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a schedule.

        Args:
            schedule_id: Schedule ID

        Returns:
            True if deletion was successful

        Raises:
            EntityNotFoundException: If schedule doesn't exist
        """
        # Find schedule
        schedule = await self._schedule_repository.find_by_id(schedule_id)
        if not schedule:
            raise EntityNotFoundException("Schedule", schedule_id)

        # Cancel schedule (this will handle seat releases)
        schedule.cancel_schedule("Deleted by administrator")
        await self._schedule_repository.update(schedule)

        return True