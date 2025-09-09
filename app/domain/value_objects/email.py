"""
Email value object.
"""
from typing import Optional
from ..entities.base import ValueObject
from ...shared.validators import UserValidator
from ...core.exceptions import ValidationException


class Email(ValueObject):
    """Email value object with validation."""

    def __init__(self, email: str):
        """
        Initialize email value object.

        Args:
            email: Email address string

        Raises:
            ValidationException: If email format is invalid
        """
        self._value = UserValidator.validate_email(email)

    @property
    def value(self) -> str:
        """Get email value."""
        return self._value

    @property
    def local_part(self) -> str:
        """Get local part of email (before @)."""
        return self._value.split('@')[0]

    @property
    def domain(self) -> str:
        """Get domain part of email (after @)."""
        return self._value.split('@')[1]

    def mask(self) -> str:
        """Get masked email for privacy."""
        from ...shared.utils import StringUtils
        return StringUtils.mask_email(self._value)

    def is_same_domain(self, other_email: 'Email') -> bool:
        """Check if this email has the same domain as another email."""
        return self.domain.lower() == other_email.domain.lower()

    def __str__(self) -> str:
        """String representation."""
        return self._value

    @classmethod
    def create_optional(cls, email: Optional[str]) -> Optional['Email']:
        """Create optional email value object."""
        if email is None or email.strip() == '':
            return None
        return cls(email)