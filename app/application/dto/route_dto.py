"""
Route Data Transfer Objects.
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RouteDTO:
    """Route data transfer object."""
    id: str
    company_id: str
    origin: str
    destination: str
    price: float
    duration: str
    status: str
    distance_km: Optional[int]
    description: Optional[str]
    total_bookings: int
    popularity_score: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, route) -> 'RouteDTO':
        """Create DTO from Route entity."""
        return cls(
            id=route.id,
            company_id=route.company_id,
            origin=route.origin,
            destination=route.destination,
            price=route.price.to_float(),
            duration=route.duration,
            status=route.status.value,
            distance_km=route.distance_km,
            description=route.description,
            total_bookings=route.total_bookings,
            popularity_score=route.popularity_score,
            created_at=route.created_at,
            updated_at=route.updated_at
        )


@dataclass
class CreateRouteDTO:
    """Create route data transfer object."""
    company_id: str
    origin: str
    destination: str
    price: float
    duration: str
    distance_km: Optional[int] = None
    description: Optional[str] = None


@dataclass
class UpdateRouteDTO:
    """Update route data transfer object."""
    price: Optional[float] = None
    duration: Optional[str] = None
    distance_km: Optional[int] = None
    description: Optional[str] = None