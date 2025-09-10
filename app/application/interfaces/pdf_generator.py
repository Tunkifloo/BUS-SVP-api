"""
PDF generator interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import io


class PDFGenerator(ABC):
    """Abstract PDF generator interface."""

    @abstractmethod
    async def generate_ticket_pdf(
        self,
        reservation_data: Dict[str, Any],
        route_data: Dict[str, Any],
        company_data: Dict[str, Any],
        schedule_data: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> bytes:
        """
        Generate ticket PDF.

        Args:
            reservation_data: Reservation information
            route_data: Route information
            company_data: Company information
            schedule_data: Schedule information
            user_data: User information

        Returns:
            PDF content as bytes
        """
        pass

    @abstractmethod
    async def generate_report_pdf(
        self,
        title: str,
        data: Dict[str, Any],
        template_name: Optional[str] = None
    ) -> bytes:
        """
        Generate report PDF.

        Args:
            title: Report title
            data: Report data
            template_name: Template name (optional)

        Returns:
            PDF content as bytes
        """
        pass

    @abstractmethod
    def create_pdf_buffer(self, content: bytes) -> io.BytesIO:
        """
        Create PDF buffer for download.

        Args:
            content: PDF content as bytes

        Returns:
            BytesIO buffer
        """
        pass