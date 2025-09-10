"""
Company repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.company import Company
from ..value_objects.email import Email


class CompanyRepository(ABC):
    """Abstract repository for Company entities."""

    @abstractmethod
    async def save(self, company: Company) -> Company:
        """Save company entity."""
        pass

    @abstractmethod
    async def find_by_id(self, company_id: str) -> Optional[Company]:
        """Find company by ID."""
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[Company]:
        """Find company by email."""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Company]:
        """Find company by name."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Company]:
        """Find all companies with pagination."""
        pass

    @abstractmethod
    async def find_active(self, limit: int = 100, offset: int = 0) -> List[Company]:
        """Find active companies."""
        pass

    @abstractmethod
    async def update(self, company: Company) -> Company:
        """Update company entity."""
        pass

    @abstractmethod
    async def delete(self, company_id: str) -> bool:
        """Delete company by ID."""
        pass

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Check if company exists by name."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if company exists by email."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total companies."""
        pass