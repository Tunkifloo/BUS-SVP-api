"""
Company Data Transfer Objects.
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CompanyDTO:
    """Company data transfer object."""
    id: str
    name: str
    email: str
    phone: str
    address: Optional[str]
    description: Optional[str]
    status: str
    rating: float
    total_trips: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, company) -> 'CompanyDTO':
        """Create DTO from Company entity."""
        return cls(
            id=company.id,
            name=company.name,
            email=company.email.value,
            phone=company.phone,
            address=company.address,
            description=company.description,
            status=company.status.value,
            rating=company.rating,
            total_trips=company.total_trips,
            created_at=company.created_at,
            updated_at=company.updated_at
        )


@dataclass
class CreateCompanyDTO:
    """Create company data transfer object."""
    name: str
    email: str
    phone: str
    address: Optional[str] = None
    description: Optional[str] = None


@dataclass
class UpdateCompanyDTO:
    """Update company data transfer object."""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None