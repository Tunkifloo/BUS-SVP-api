"""
User repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User
from ..value_objects.email import Email


class UserRepository(ABC):
    """Abstract repository for User entities."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user entity."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email."""
        pass

    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Find all users with pagination."""
        pass

    @abstractmethod
    async def find_by_role(self, role: str, limit: int = 100, offset: int = 0) -> List[User]:
        """Find users by role."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user entity."""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """Count total users."""
        pass