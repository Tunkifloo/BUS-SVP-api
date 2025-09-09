"""
Custom validators for the application.
"""
from typing import Any, Optional, List
from datetime import datetime, time
from .utils import ValidationUtils, DateTimeUtils
from .constants import BusinessRules
from ..core.exceptions import ValidationException


class BaseValidator:
    """Base validator class."""

    @staticmethod
    def validate_required(value: Any, field_name: str) -> Any:
        """Validate that a field is not None or empty."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationException(field_name, value, "Field is required")
        return value

    @staticmethod
    def validate_length(
            value: str,
            field_name: str,
            min_length: Optional[int] = None,
            max_length: Optional[int] = None
    ) -> str:
        """Validate string length."""
        if min_length and len(value) < min_length:
            raise ValidationException(
                field_name,
                value,
                f"Must be at least {min_length} characters long"
            )

        if max_length and len(value) > max_length:
            raise ValidationException(
                field_name,
                value,
                f"Must be no more than {max_length} characters long"
            )

        return value

    @staticmethod
    def validate_range(
            value: float,
            field_name: str,
            min_value: Optional[float] = None,
            max_value: Optional[float] = None
    ) -> float:
        """Validate numeric range."""
        if min_value is not None and value < min_value:
            raise ValidationException(
                field_name,
                value,
                f"Must be at least {min_value}"
            )

        if max_value is not None and value > max_value:
            raise ValidationException(
                field_name,
                value,
                f"Must be no more than {max_value}"
            )

        return value


class UserValidator(BaseValidator):
    """Validator for user-related data."""

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format."""
        cls.validate_required(email, "email")

        if not ValidationUtils.validate_email_format(email):
            raise ValidationException("email", email, "Invalid email format")

        return email.lower().strip()

    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password strength."""
        cls.validate_required(password, "password")

        if not ValidationUtils.is_strong_password(password):
            validations = ValidationUtils.validate_password_strength(password)
            errors = []

            if not validations['length']:
                errors.append(f"at least {BusinessRules.MIN_PASSWORD_LENGTH} characters")
            if not validations['uppercase']:
                errors.append("one uppercase letter")
            if not validations['lowercase']:
                errors.append("one lowercase letter")
            if not validations['digit']:
                errors.append("one digit")

            error_msg = f"Password must contain: {', '.join(errors)}"
            raise ValidationException("password", "***", error_msg)

        return password

    @classmethod
    def validate_name(cls, name: str) -> str:
        """Validate user name."""
        cls.validate_required(name, "name")
        cls.validate_length(name, "name", min_length=2, max_length=100)

        # Check for valid characters (letters, spaces, and common name characters)
        import re
        if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s\-\.]+$', name):
            raise ValidationException(
                "name",
                name,
                "Name can only contain letters, spaces, hyphens, and periods"
            )

        return ValidationUtils.sanitize_string(name)

    @classmethod
    def validate_phone(cls, phone: Optional[str]) -> Optional[str]:
        """Validate phone number."""
        if not phone:
            return None

        if not ValidationUtils.validate_phone_number(phone):
            raise ValidationException(
                "phone",
                phone,
                "Invalid Peru phone number format"
            )

        return phone.strip()


class CompanyValidator(BaseValidator):
    """Validator for company-related data."""

    @classmethod
    def validate_company_name(cls, name: str) -> str:
        """Validate company name."""
        cls.validate_required(name, "name")
        cls.validate_length(
            name,
            "name",
            min_length=BusinessRules.MIN_COMPANY_NAME_LENGTH,
            max_length=BusinessRules.MAX_COMPANY_NAME_LENGTH
        )

        return ValidationUtils.sanitize_string(name)

    @classmethod
    def validate_company_email(cls, email: str) -> str:
        """Validate company email."""
        return UserValidator.validate_email(email)

    @classmethod
    def validate_company_phone(cls, phone: str) -> str:
        """Validate company phone."""
        cls.validate_required(phone, "phone")

        if not ValidationUtils.validate_phone_number(phone):
            raise ValidationException(
                "phone",
                phone,
                "Invalid Peru phone number format"
            )

        return phone.strip()


class BusValidator(BaseValidator):
    """Validator for bus-related data."""

    @classmethod
    def validate_plate_number(cls, plate_number: str) -> str:
        """Validate bus plate number."""
        cls.validate_required(plate_number, "plate_number")

        if not ValidationUtils.validate_plate_number(plate_number):
            raise ValidationException(
                "plate_number",
                plate_number,
                "Invalid Peru plate number format (e.g., ABC-123)"
            )

        return plate_number.upper().strip()

    @classmethod
    def validate_capacity(cls, capacity: int) -> int:
        """Validate bus capacity."""
        cls.validate_range(
            capacity,
            "capacity",
            min_value=BusinessRules.MIN_SEAT_NUMBER,
            max_value=BusinessRules.MAX_SEAT_NUMBER
        )

        return capacity

    @classmethod
    def validate_model(cls, model: str) -> str:
        """Validate bus model."""
        cls.validate_required(model, "model")
        cls.validate_length(model, "model", min_length=2, max_length=50)

        return ValidationUtils.sanitize_string(model)


class RouteValidator(BaseValidator):
    """Validator for route-related data."""

    @classmethod
    def validate_city_name(cls, city: str, field_name: str) -> str:
        """Validate city name."""
        cls.validate_required(city, field_name)
        cls.validate_length(city, field_name, min_length=2, max_length=50)

        # Check for valid characters (letters, spaces, and common city name characters)
        import re
        if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s\-\.]+$', city):
            raise ValidationException(
                field_name,
                city,
                "City name can only contain letters, spaces, hyphens, and periods"
            )

        return ValidationUtils.sanitize_string(city).title()

    @classmethod
    def validate_origin(cls, origin: str) -> str:
        """Validate route origin."""
        return cls.validate_city_name(origin, "origin")

    @classmethod
    def validate_destination(cls, destination: str) -> str:
        """Validate route destination."""
        return cls.validate_city_name(destination, "destination")

    @classmethod
    def validate_price(cls, price: float) -> float:
        """Validate route price."""
        cls.validate_range(
            price,
            "price",
            min_value=BusinessRules.MIN_ROUTE_PRICE,
            max_value=BusinessRules.MAX_ROUTE_PRICE
        )

        return round(price, 2)

    @classmethod
    def validate_duration(cls, duration: str) -> str:
        """Validate route duration format."""
        cls.validate_required(duration, "duration")

        # Accept formats like "2h", "30m", "2h 30m", "22h"
        import re
        duration_pattern = r'^(\d{1,2}h)?(\s?\d{1,2}m)?$'

        if not re.match(duration_pattern, duration.strip()):
            raise ValidationException(
                "duration",
                duration,
                "Invalid duration format. Use formats like '2h', '30m', or '2h 30m'"
            )

        return duration.strip()

    @classmethod
    def validate_different_cities(cls, origin: str, destination: str) -> None:
        """Validate that origin and destination are different."""
        if origin.lower() == destination.lower():
            raise ValidationException(
                "destination",
                destination,
                "Origin and destination must be different cities"
            )


class ScheduleValidator(BaseValidator):
    """Validator for schedule-related data."""

    @classmethod
    def validate_time_format(cls, time_str: str, field_name: str) -> str:
        """Validate time format (HH:MM)."""
        cls.validate_required(time_str, field_name)

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            raise ValidationException(
                field_name,
                time_str,
                "Invalid time format. Use HH:MM format (e.g., 14:30)"
            )

        return time_str

    @classmethod
    def validate_departure_time(cls, departure_time: str) -> str:
        """Validate departure time."""
        return cls.validate_time_format(departure_time, "departure_time")

    @classmethod
    def validate_arrival_time(cls, arrival_time: str) -> str:
        """Validate arrival time."""
        return cls.validate_time_format(arrival_time, "arrival_time")

    @classmethod
    def validate_date(cls, date_str: str) -> str:
        """Validate date format and future date."""
        cls.validate_required(date_str, "date")

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationException(
                "date",
                date_str,
                "Invalid date format. Use YYYY-MM-DD format"
            )

        # Check if date is in the future
        today = DateTimeUtils.now_peru().date()
        if date_obj < today:
            raise ValidationException(
                "date",
                date_str,
                "Schedule date must be today or in the future"
            )

        return date_str

    @classmethod
    def validate_available_seats(cls, available_seats: int, bus_capacity: int) -> int:
        """Validate available seats against bus capacity."""
        cls.validate_range(
            available_seats,
            "available_seats",
            min_value=0,
            max_value=bus_capacity
        )

        return available_seats

    @classmethod
    def validate_schedule_times(cls, departure_time: str, arrival_time: str) -> None:
        """Validate that schedule times are logical."""
        dep_time = datetime.strptime(departure_time, "%H:%M").time()
        arr_time = datetime.strptime(arrival_time, "%H:%M").time()

        # For overnight trips, arrival can be earlier than departure
        # But for same-day trips, arrival should be after departure
        if dep_time == arr_time:
            raise ValidationException(
                "arrival_time",
                arrival_time,
                "Arrival time cannot be the same as departure time"
            )


class ReservationValidator(BaseValidator):
    """Validator for reservation-related data."""

    @classmethod
    def validate_seat_number(cls, seat_number: int, bus_capacity: int) -> int:
        """Validate seat number."""
        cls.validate_range(
            seat_number,
            "seat_number",
            min_value=BusinessRules.MIN_SEAT_NUMBER,
            max_value=bus_capacity
        )

        return seat_number

    @classmethod
    def validate_booking_time(cls, departure_datetime: datetime) -> None:
        """Validate booking timing constraints."""
        if not DateTimeUtils.is_booking_allowed(departure_datetime):
            min_hours = BusinessRules.MIN_BOOKING_HOURS_ADVANCE
            max_days = BusinessRules.MAX_BOOKING_DAYS_ADVANCE

            raise ValidationException(
                "schedule",
                departure_datetime.isoformat(),
                f"Booking must be made between {min_hours} hours and {max_days} days in advance"
            )

    @classmethod
    def validate_cancellation_time(cls, departure_datetime: datetime) -> None:
        """Validate cancellation timing constraints."""
        if not DateTimeUtils.is_cancellation_allowed(departure_datetime):
            deadline_hours = BusinessRules.CANCELLATION_DEADLINE_HOURS

            raise ValidationException(
                "schedule",
                departure_datetime.isoformat(),
                f"Cancellation must be made at least {deadline_hours} hours before departure"
            )