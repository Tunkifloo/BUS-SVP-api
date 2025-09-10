"""
Email templates for the application.
"""
from typing import Dict, Any, Optional


class EmailTemplates:
    """Email template manager."""

    def reservation_confirmation_template(
            self,
            user_name: str,
            reservation_data: Dict[str, Any]
    ) -> str:
        """Generate reservation confirmation email template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confirmación de Reserva</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ background-color: #ea580c; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #f9fafb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>¡Reserva Confirmada!</h1>
                    <p>Código de Reserva: {reservation_data.get('reservation_code', 'N/A')}</p>
                </div>
                <div class="content">
                    <h2>Hola {user_name},</h2>
                    <p>Tu reserva ha sido confirmada exitosamente. Aquí están los detalles de tu viaje:</p>

                    <div class="details">
                        <h3>Detalles del Viaje</h3>
                        <p><strong>Ruta:</strong> {reservation_data.get('route', {}).get('origin', 'N/A')} → {reservation_data.get('route', {}).get('destination', 'N/A')}</p>
                        <p><strong>Fecha:</strong> {reservation_data.get('schedule', {}).get('date', 'N/A')}</p>
                        <p><strong>Hora de Salida:</strong> {reservation_data.get('schedule', {}).get('departure_time', 'N/A')}</p>
                        <p><strong>Asiento:</strong> #{reservation_data.get('seat_number', 'N/A')}</p>
                        <p><strong>Empresa:</strong> {reservation_data.get('company', {}).get('name', 'N/A')}</p>
                        <p><strong>Precio:</strong> S/ {reservation_data.get('price', 'N/A')}</p>
                    </div>

                    <p><strong>Importante:</strong> Presenta este código de reserva en el terminal para abordar.</p>
                    <p>Te recomendamos llegar 30 minutos antes de la hora de salida.</p>
                </div>
                <div class="footer">
                    <p>Bus-SVP - Sistema de Ventas de Pasajes</p>
                    <p>Este es un email automático, no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def reservation_cancellation_template(
            self,
            user_name: str,
            reservation_data: Dict[str, Any],
            cancellation_reason: Optional[str] = None
    ) -> str:
        """Generate reservation cancellation email template."""
        reason_text = f"<p><strong>Motivo:</strong> {cancellation_reason}</p>" if cancellation_reason else ""

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Cancelación de Reserva</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .details {{ background-color: #fef2f2; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #dc2626; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reserva Cancelada</h1>
                    <p>Código de Reserva: {reservation_data.get('reservation_code', 'N/A')}</p>
                </div>
                <div class="content">
                    <h2>Hola {user_name},</h2>
                    <p>Tu reserva ha sido cancelada. Aquí están los detalles:</p>

                    <div class="details">
                        <h3>Detalles de la Reserva Cancelada</h3>
                        <p><strong>Ruta:</strong> {reservation_data.get('route', {}).get('origin', 'N/A')} → {reservation_data.get('route', {}).get('destination', 'N/A')}</p>
                        <p><strong>Fecha:</strong> {reservation_data.get('schedule', {}).get('date', 'N/A')}</p>
                        <p><strong>Hora de Salida:</strong> {reservation_data.get('schedule', {}).get('departure_time', 'N/A')}</p>
                        <p><strong>Asiento:</strong> #{reservation_data.get('seat_number', 'N/A')}</p>
                        {reason_text}
                    </div>

                    <p>Si tienes alguna pregunta sobre el reembolso, por favor contacta a nuestro servicio al cliente.</p>
                </div>
                <div class="footer">
                    <p>Bus-SVP - Sistema de Ventas de Pasajes</p>
                    <p>Este es un email automático, no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def password_reset_template(
            self,
            user_name: str,
            reset_token: str
    ) -> str:
        """Generate password reset email template."""
        # In a real application, this would be a proper URL
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Restablecer Contraseña</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; }}
                .header {{ background-color: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .button {{ background-color: #ea580c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Restablecer Contraseña</h1>
                </div>
                <div class="content">
                    <h2>Hola {user_name},</h2>
                    <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva contraseña:</p>

                    <a href="{reset_url}" class="button">Restablecer Contraseña</a>

                    <p>Si no solicitaste este cambio, puedes ignorar este email. Tu contraseña no será cambiada.</p>
                    <p>Este enlace expirará en 24 horas por motivos de seguridad.</p>
                </div>
                <div class="footer">
                    <p>Bus-SVP - Sistema de Ventas de Pasajes</p>
                    <p>Este es un email automático, no responder.</p>
                </div>
            </div>
        </body>
        </html>
        """