"""
Authentication service interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AuthService(ABC):
    """Abstract authentication service interface."""

    @abstractmethod
    async def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create access token for user.

        Args:
            user_data: User information

        Returns:
            JWT access token
        """
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode access token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token data or None if invalid
        """
        pass

    @abstractmethod
    async def create_password_reset_token(self, user_id: str) -> str:
        """
        Create password reset token.

        Args:
            user_id: User ID

        Returns:
            Password reset token
        """
        pass

    @abstractmethod
    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        Verify password reset token.

        Args:
            token: Reset token to verify

        Returns:
            User ID if token is valid, None otherwise
        """
        pass

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """
        Hash password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        pass

    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password is correct
        """
        pass