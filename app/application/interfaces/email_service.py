"""
Email service interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class EmailService(ABC):
    """Abstract email service interface."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        content_type: str = "text/html",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email content
            content_type: Content type (text/plain or text/html)
            attachments: List of attachments (optional)

        Returns:
            True if email was sent successfully
        """
        pass

    @abstractmethod
    async def send_reservation_confirmation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """
        Send reservation confirmation email.

        Args:
            user_email: User email address
            user_name: User name
            reservation_data: Reservation details

        Returns:
            True if email was sent successfully
        """
        pass

    @abstractmethod
    async def send_reservation_cancellation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any],
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """
        Send reservation cancellation email.

        Args:
            user_email: User email address
            user_name: User name
            reservation_data: Reservation details
            cancellation_reason: Reason for cancellation

        Returns:
            True if email was sent successfully
        """
        pass

    @abstractmethod
    async def send_password_reset(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """
        Send password reset email.

        Args:
            user_email: User email address
            user_name: User name
            reset_token: Password reset token

        Returns:
            True if email was sent successfully
        """
        pass