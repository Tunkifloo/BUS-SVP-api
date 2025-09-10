"""
Manage buses use case.
"""
from typing import List, Dict, Any, Optional
from app.domain.entities.bus import Bus
from app.domain.repositories.bus_repository import BusRepository
from app.domain.repositories.company_repository import CompanyRepository
from app.core.exceptions import EntityNotFoundException, EntityAlreadyExistsException
from app.shared.decorators import log_execution


class ManageBusesUseCase:
    """Use case for managing buses."""

    def __init__(
        self,
        bus_repository: BusRepository,
        company_repository: CompanyRepository
    ):
        self._bus_repository = bus_repository
        self._company_repository = company_repository

    @log_execution(log_duration=True)
    async def create_bus(
        self,
        company_id: str,
        plate_number: str,
        capacity: int,
        model: str,
        year: Optional[int] = None,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new bus.

        Args:
            company_id: Company ID
            plate_number: Bus plate number
            capacity: Seating capacity
            model: Bus model
            year: Manufacturing year (optional)
            features: List of features (optional)

        Returns:
            Created bus information

        Raises:
            EntityNotFoundException: If company doesn't exist
            EntityAlreadyExistsException: If plate number already exists
        """
        # Validate company exists
        company = await self._company_repository.find_by_id(company_id)
        if not company:
            raise EntityNotFoundException("Company", company_id)

        # Check if plate number already exists
        existing_bus = await self._bus_repository.find_by_plate_number(plate_number)
        if existing_bus:
            raise EntityAlreadyExistsException("Bus", plate_number)

        # Create bus entity
        bus = Bus(
            company_id=company_id,
            plate_number=plate_number,
            capacity=capacity,
            model=model,
            year=year,
            features=features or []
        )

        # Save bus
        saved_bus = await self._bus_repository.save(bus)

        return {
            "id": saved_bus.id,
            "company_id": saved_bus.company_id,
            "plate_number": saved_bus.plate_number,
            "capacity": saved_bus.capacity,
            "model": saved_bus.model,
            "year": saved_bus.year,
            "features": saved_bus.features,
            "status": saved_bus.status.value,
            "created_at": saved_bus.created_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def update_bus(
        self,
        bus_id: str,
        model: Optional[str] = None,
        year: Optional[int] = None,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update bus information.

        Args:
            bus_id: Bus ID
            model: New model (optional)
            year: New year (optional)
            features: New features (optional)

        Returns:
            Updated bus information

        Raises:
            EntityNotFoundException: If bus doesn't exist
        """
        # Find bus
        bus = await self._bus_repository.find_by_id(bus_id)
        if not bus:
            raise EntityNotFoundException("Bus", bus_id)

        # Update basic info
        bus.update_basic_info(
            model=model,
            year=year,
            features=features
        )

        # Save updated bus
        updated_bus = await self._bus_repository.update(bus)

        return {
            "id": updated_bus.id,
            "company_id": updated_bus.company_id,
            "plate_number": updated_bus.plate_number,
            "capacity": updated_bus.capacity,
            "model": updated_bus.model,
            "year": updated_bus.year,
            "features": updated_bus.features,
            "status": updated_bus.status.value,
            "updated_at": updated_bus.updated_at.isoformat()
        }

    @log_execution(log_duration=True)
    async def get_buses(
        self,
        company_id: Optional[str] = None,
        available_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get list of buses.

        Args:
            company_id: Filter by company (optional)
            available_only: Only return available buses
            limit: Limit results
            offset: Offset for pagination

        Returns:
            List of buses
        """
        if company_id:
            buses = await self._bus_repository.find_by_company(
                company_id, limit=limit, offset=offset
            )
        elif available_only:
            buses = await self._bus_repository.find_available_for_service(
                limit=limit, offset=offset
            )
        else:
            buses = await self._bus_repository.find_all(limit=limit, offset=offset)

        return [
            {
                "id": bus.id,
                "company_id": bus.company_id,
                "plate_number": bus.plate_number,
                "capacity": bus.capacity,
                "model": bus.model,
                "year": bus.year,
                "features": bus.features,
                "status": bus.status.value,
                "mileage": bus._mileage,
                "last_maintenance_date": bus._last_maintenance_date if bus._last_maintenance_date else None,
                "next_maintenance_due": bus._next_maintenance_due if bus._next_maintenance_due else None,
                "created_at": bus.created_at.isoformat(),
                "updated_at": bus.updated_at.isoformat()
            }
            for bus in buses
        ]

    @log_execution(log_duration=True)
    async def delete_bus(self, bus_id: str) -> bool:
        """
        Delete a bus.

        Args:
            bus_id: Bus ID

        Returns:
            True if deletion was successful

        Raises:
            EntityNotFoundException: If bus doesn't exist
        """
        # Find bus
        bus = await self._bus_repository.find_by_id(bus_id)
        if not bus:
            raise EntityNotFoundException("Bus", bus_id)

        # Soft delete
        bus.mark_as_deleted()
        await self._bus_repository.update(bus)

        return True