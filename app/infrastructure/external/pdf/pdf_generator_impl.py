"""
PDF generator implementation using ReportLab.
"""
from typing import Dict, Any, Optional
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import logging

from ....application.interfaces.pdf_generator import PDFGenerator
from ....core.exceptions import PDFGenerationException

logger = logging.getLogger(__name__)


class PDFGeneratorImpl(PDFGenerator):
    """ReportLab PDF generator implementation."""

    async def generate_ticket_pdf(
            self,
            reservation_data: Dict[str, Any],
            route_data: Dict[str, Any],
            company_data: Dict[str, Any],
            schedule_data: Dict[str, Any],
            user_data: Dict[str, Any]
    ) -> bytes:
        """Generate ticket PDF."""
        try:
            buffer = io.BytesIO()

            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Get styles
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#ea580c')
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.HexColor('#1f2937')
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6
            )

            # Build content
            story = []

            # Title
            story.append(Paragraph("BOLETO ELECTRÓNICO", title_style))
            story.append(Spacer(1, 12))

            # Reservation code
            code_style = ParagraphStyle(
                'Code',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                backColor=colors.HexColor('#f3f4f6'),
                borderColor=colors.HexColor('#d1d5db'),
                borderWidth=1,
                borderPadding=8
            )
            story.append(
                Paragraph(f"Código de Reserva: <b>{reservation_data.get('reservation_code', 'N/A')}</b>", code_style))
            story.append(Spacer(1, 20))

            # Route information
            story.append(Paragraph("INFORMACIÓN DEL VIAJE", heading_style))

            route_table_data = [
                ['Origen:', route_data.get('origin', 'N/A')],
                ['Destino:', route_data.get('destination', 'N/A')],
                ['Fecha:', schedule_data.get('date', 'N/A')],
                ['Hora de Salida:', schedule_data.get('departure_time', 'N/A')],
                ['Hora de Llegada:', schedule_data.get('arrival_time', 'N/A')],
                ['Duración:', route_data.get('duration', 'N/A')],
            ]

            route_table = Table(route_table_data, colWidths=[2 * inch, 3 * inch])
            route_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))

            story.append(route_table)
            story.append(Spacer(1, 20))

            # Passenger and company information
            story.append(Paragraph("DETALLES", heading_style))

            details_table_data = [
                ['Pasajero:', user_data.get('name', 'N/A')],
                ['Email:', user_data.get('email', 'N/A')],
                ['Empresa:', company_data.get('name', 'N/A')],
                ['Teléfono Empresa:', company_data.get('phone', 'N/A')],
                ['Asiento:', f"#{reservation_data.get('seat_number', 'N/A')}"],
                ['Precio:', f"S/ {reservation_data.get('price', 'N/A')}"],
            ]

            details_table = Table(details_table_data, colWidths=[2 * inch, 3 * inch])
            details_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
            ]))

            story.append(details_table)
            story.append(Spacer(1, 30))

            # Important notes
            story.append(Paragraph("INSTRUCCIONES IMPORTANTES", heading_style))

            instructions = [
                "• Presentar este boleto electrónico en el terminal",
                "• Llegar 30 minutos antes de la hora de salida",
                "• Traer documento de identidad válido",
                "• El boleto es personal e intransferible",
                "• Cancelaciones deben realizarse 4 horas antes"
            ]

            for instruction in instructions:
                story.append(Paragraph(instruction, normal_style))

            story.append(Spacer(1, 20))

            # QR Code placeholder (in a real implementation, you'd generate a QR code)
            qr_style = ParagraphStyle(
                'QR',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                backColor=colors.HexColor('#f3f4f6'),
                borderColor=colors.HexColor('#d1d5db'),
                borderWidth=1,
                borderPadding=20
            )
            story.append(Paragraph("[ QR CODE PLACEHOLDER ]<br/>Código para escanear en terminal", qr_style))
            story.append(Spacer(1, 20))

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#6b7280')
            )

            generation_time = datetime.now().strftime("%d/%m/%Y %H:%M")
            story.append(
                Paragraph(f"Generado el {generation_time} | Bus-SVP Sistema de Ventas de Pasajes", footer_style))

            # Build PDF
            doc.build(story)

            # Get PDF bytes
            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            logger.error(f"Failed to generate ticket PDF: {str(e)}")
            raise PDFGenerationException(f"Failed to generate ticket PDF: {str(e)}")

    async def generate_report_pdf(
            self,
            title: str,
            data: Dict[str, Any],
            template_name: Optional[str] = None
    ) -> bytes:
        """Generate report PDF."""
        try:
            buffer = io.BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph(title, title_style))

            # Add data based on template or generic format
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    story.append(Paragraph(f"<b>{key}:</b>", styles['Heading3']))
                    story.append(Paragraph(str(value), styles['Normal']))
                else:
                    story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
                story.append(Spacer(1, 6))

            # Generation timestamp
            generation_time = datetime.now().strftime("%d/%m/%Y %H:%M")
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Generado el {generation_time}", styles['Normal']))

            doc.build(story)

            buffer.seek(0)
            return buffer.read()

        except Exception as e:
            logger.error(f"Failed to generate report PDF: {str(e)}")
            raise PDFGenerationException(f"Failed to generate report PDF: {str(e)}")

    def create_pdf_buffer(self, content: bytes) -> io.BytesIO:
        """Create PDF buffer for download."""
        buffer = io.BytesIO(content)
        buffer.seek(0)
        return buffer