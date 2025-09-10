"""
User Data Transfer Objects.
"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from ...shared.constants import UserRole


@dataclass
class UserDTO:
    """User data transfer object."""
    id: str
    email: str
    name: str
    role: str
    phone: Optional[str]
    is_active: bool
    email_verified: bool
    last_login: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, user) -> 'UserDTO':
        """Create DTO from User entity."""
        return cls(
            id=user.id,
            email=user.email.value,
            name=user.name,
            role=user.role.value,
            phone=user.phone,
            is_active=user.is_active,
            email_verified=user.email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


@dataclass
class CreateUserDTO:
    """Create user data transfer object."""
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    role: UserRole = UserRole.USER


@dataclass
class UpdateUserDTO:
    """Update user data transfer object."""
    name: Optional[str] = None
    phone: Optional[str] = None