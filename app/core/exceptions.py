"""
Core exceptions module.
Defines custom exceptions for the application.
"""
from typing import Optional, Dict, Any


class BaseException(Exception):
    """Base exception class for all custom exceptions."""

    def __init__(
            self,
            message: str,
            error_code: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DomainException(BaseException):
    """Exception for domain-level business rule violations."""
    pass


class ApplicationException(BaseException):
    """Exception for application-level errors."""
    pass


class InfrastructureException(BaseException):
    """Exception for infrastructure-level errors."""
    pass


# Authentication Exceptions
class AuthenticationException(ApplicationException):
    """Exception for authentication failures."""
    pass


class AuthorizationException(ApplicationException):
    """Exception for authorization failures."""
    pass


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid user credentials."""

    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredException(AuthenticationException):
    """Exception for expired tokens."""

    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED"
        )


class InsufficientPermissionsException(AuthorizationException):
    """Exception for insufficient permissions."""

    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permission": required_permission}
        )


# Domain Exceptions
class EntityNotFoundException(DomainException):
    """Exception for when an entity is not found."""

    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(
            message=f"{entity_type} with id '{entity_id}' not found",
            error_code="ENTITY_NOT_FOUND",
            details={"entity_type": entity_type, "entity_id": entity_id}
        )


class EntityAlreadyExistsException(DomainException):
    """Exception for when an entity already exists."""

    def __init__(self, entity_type: str, identifier: str):
        super().__init__(
            message=f"{entity_type} with identifier '{identifier}' already exists",
            error_code="ENTITY_ALREADY_EXISTS",
            details={"entity_type": entity_type, "identifier": identifier}
        )


class InvalidEntityStateException(DomainException):
    """Exception for invalid entity state."""

    def __init__(self, entity_type: str, current_state: str, required_state: str):
        super().__init__(
            message=f"{entity_type} is in '{current_state}' state, but '{required_state}' is required",
            error_code="INVALID_ENTITY_STATE",
            details={
                "entity_type": entity_type,
                "current_state": current_state,
                "required_state": required_state
            }
        )


# Business Rule Exceptions
class SeatNotAvailableException(DomainException):
    """Exception for when a seat is not available."""

    def __init__(self, seat_number: int):
        super().__init__(
            message=f"Seat {seat_number} is not available",
            error_code="SEAT_NOT_AVAILABLE",
            details={"seat_number": seat_number}
        )


class InsufficientSeatsException(DomainException):
    """Exception for insufficient available seats."""

    def __init__(self, requested_seats: int, available_seats: int):
        super().__init__(
            message=f"Requested {requested_seats} seats, but only {available_seats} available",
            error_code="INSUFFICIENT_SEATS",
            details={
                "requested_seats": requested_seats,
                "available_seats": available_seats
            }
        )


class ReservationNotCancellableException(DomainException):
    """Exception for when a reservation cannot be cancelled."""

    def __init__(self, reservation_id: str, reason: str):
        super().__init__(
            message=f"Reservation {reservation_id} cannot be cancelled: {reason}",
            error_code="RESERVATION_NOT_CANCELLABLE",
            details={"reservation_id": reservation_id, "reason": reason}
        )


class ScheduleConflictException(DomainException):
    """Exception for schedule conflicts."""

    def __init__(self, bus_id: str, conflicting_schedule_id: str):
        super().__init__(
            message=f"Bus {bus_id} has a scheduling conflict with schedule {conflicting_schedule_id}",
            error_code="SCHEDULE_CONFLICT",
            details={"bus_id": bus_id, "conflicting_schedule_id": conflicting_schedule_id}
        )


# Validation Exceptions
class ValidationException(ApplicationException):
    """Exception for validation errors."""

    def __init__(self, field: str, value: Any, message: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": str(value), "validation_message": message}
        )


class EmailValidationException(ValidationException):
    """Exception for email validation errors."""

    def __init__(self, email: str):
        super().__init__(
            field="email",
            value=email,
            message="Invalid email format"
        )


# Infrastructure Exceptions
class DatabaseException(InfrastructureException):
    """Exception for database-related errors."""
    pass


class ExternalServiceException(InfrastructureException):
    """Exception for external service errors."""

    def __init__(self, service_name: str, error_message: str):
        super().__init__(
            message=f"Error from {service_name}: {error_message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service_name": service_name, "error_message": error_message}
        )


class EmailServiceException(ExternalServiceException):
    """Exception for email service errors."""

    def __init__(self, error_message: str):
        super().__init__(service_name="Email Service", error_message=error_message)


class PDFGenerationException(ExternalServiceException):
    """Exception for PDF generation errors."""

    def __init__(self, error_message: str):
        super().__init__(service_name="PDF Generator", error_message=error_message)