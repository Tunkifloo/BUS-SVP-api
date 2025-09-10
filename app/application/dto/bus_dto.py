"""
Bus Data Transfer Objects.
"""
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BusDTO:
    """Bus data transfer object."""
    id: str
    company_id: str
    plate_number: str
    capacity: int
    model: str
    status: str
    features: List[str]
    year: Optional[int]
    mileage: int
    last_maintenance_date: Optional[str]
    next_maintenance_due: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, bus) -> 'BusDTO':
        """Create DTO from Bus entity."""
        return cls(
            id=bus.id,
            company_id=bus.company_id,
            plate_number=bus.plate_number,
            capacity=bus.capacity,
            model=bus.model,
            status=bus.status.value,
            features=bus.features,
            year=bus.year,
            mileage=bus.mileage,
            last_maintenance_date=bus.last_maintenance_date,
            next_maintenance_due=bus.next_maintenance_due,
            created_at=bus.created_at,
            updated_at=bus.updated_at
        )


@dataclass
class CreateBusDTO:
    """Create bus data transfer object."""
    company_id: str
    plate_number: str
    capacity: int
    model: str
    year: Optional[int] = None
    features: Optional[List[str]] = None


@dataclass
class UpdateBusDTO:
    """Update bus data transfer object."""
    model: Optional[str] = None
    year: Optional[int] = None
    features: Optional[List[str]] = None