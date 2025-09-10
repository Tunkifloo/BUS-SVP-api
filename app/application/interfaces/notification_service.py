"""
Notification service interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ...shared.constants import NotificationType


class NotificationService(ABC):
    """Abstract notification service interface."""

    @abstractmethod
    async def send_notification(
        self,
        recipient: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification.

        Args:
            recipient: Recipient identifier (email, phone, etc.)
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data (optional)

        Returns:
            True if notification was sent successfully
        """
        pass

    @abstractmethod
    async def send_bulk_notification(
        self,
        recipients: List[str],
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send bulk notifications.

        Args:
            recipients: List of recipient identifiers
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data (optional)

        Returns:
            Dictionary mapping recipients to success status
        """
        pass

    @abstractmethod
    async def send_reservation_notification(
        self,
        user_email: str,
        notification_type: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """
        Send reservation-specific notification.

        Args:
            user_email: User email
            notification_type: Type of reservation notification
            reservation_data: Reservation data

        Returns:
            True if notification was sent successfully
        """
        pass