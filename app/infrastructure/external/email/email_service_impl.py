"""
Email service implementation.
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import logging

from ....application.interfaces.email_service import EmailService
from ....core.config import settings
from ....core.exceptions import EmailServiceException
from .email_templates import EmailTemplates

logger = logging.getLogger(__name__)


class EmailServiceImpl(EmailService):
    """SMTP email service implementation."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email or settings.smtp_username
        self.templates = EmailTemplates()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        content_type: str = "text/html",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email via SMTP."""
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject

            # Attach content
            message.attach(MIMEText(content, content_type))

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    # Implementation for attachments would go here
                    pass

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=True
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise EmailServiceException(f"Failed to send email: {str(e)}")

    async def send_reservation_confirmation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """Send reservation confirmation email."""
        try:
            subject = f"Confirmación de Reserva #{reservation_data['reservation_code']}"
            content = self.templates.reservation_confirmation_template(
                user_name=user_name,
                reservation_data=reservation_data
            )

            return await self.send_email(user_email, subject, content)

        except Exception as e:
            logger.error(f"Failed to send reservation confirmation to {user_email}: {str(e)}")
            return False

    async def send_reservation_cancellation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any],
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Send reservation cancellation email."""
        try:
            subject = f"Cancelación de Reserva #{reservation_data['reservation_code']}"
            content = self.templates.reservation_cancellation_template(
                user_name=user_name,
                reservation_data=reservation_data,
                cancellation_reason=cancellation_reason
            )

            return await self.send_email(user_email, subject, content)

        except Exception as e:
            logger.error(f"Failed to send cancellation email to {user_email}: {str(e)}")
            return False

    async def send_password_reset(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email."""
        try:
            subject = "Restablecer Contraseña - Bus-SVP"
            content = self.templates.password_reset_template(
                user_name=user_name,
                reset_token=reset_token
            )

            return await self.send_email(user_email, subject, content)

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
            return False