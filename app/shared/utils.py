"""
Shared utility functions.
"""
import re
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from email_validator import validate_email, EmailNotValidError
import pytz
from .constants import TimezoneConstants, BusinessRules
from ..core.exceptions import ValidationException


class DateTimeUtils:
    """Utility functions for date and time operations."""

    @staticmethod
    def now_utc() -> datetime:
        """Get current UTC datetime."""
        return datetime.utcnow()

    @staticmethod
    def now_peru() -> datetime:
        """Get current Peru timezone datetime."""
        peru_tz = pytz.timezone(TimezoneConstants.DEFAULT_TIMEZONE)
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now.astimezone(peru_tz)

    @staticmethod
    def to_utc(dt: datetime, source_timezone: str = TimezoneConstants.DEFAULT_TIMEZONE) -> datetime:
        """Convert datetime to UTC."""
        if dt.tzinfo is None:
            source_tz = pytz.timezone(source_timezone)
            dt = source_tz.localize(dt)
        return dt.astimezone(pytz.utc)

    @staticmethod
    def to_peru_timezone(dt: datetime) -> datetime:
        """Convert UTC datetime to Peru timezone."""
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        peru_tz = pytz.timezone(TimezoneConstants.DEFAULT_TIMEZONE)
        return dt.astimezone(peru_tz)

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string."""
        return dt.strftime(format_str)

    @staticmethod
    def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Parse string to datetime."""
        return datetime.strptime(date_str, format_str)

    @staticmethod
    def is_booking_allowed(departure_time: datetime) -> bool:
        """Check if booking is allowed based on departure time."""
        now = DateTimeUtils.now_utc()
        time_diff = departure_time - now
        min_advance = timedelta(hours=BusinessRules.MIN_BOOKING_HOURS_ADVANCE)
        max_advance = timedelta(days=BusinessRules.MAX_BOOKING_DAYS_ADVANCE)

        return min_advance <= time_diff <= max_advance

    @staticmethod
    def is_cancellation_allowed(departure_time: datetime) -> bool:
        """Check if cancellation is allowed based on departure time."""
        now = DateTimeUtils.now_utc()
        time_diff = departure_time - now
        deadline = timedelta(hours=BusinessRules.CANCELLATION_DEADLINE_HOURS)

        return time_diff >= deadline


class ValidationUtils:
    """Utility functions for validation."""

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format."""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, bool]:
        """Validate password strength and return detailed results."""
        validations = {
            'length': len(password) >= BusinessRules.MIN_PASSWORD_LENGTH,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'digit': bool(re.search(r'\d', password)),
            'special_char': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }

        return validations

    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check if password meets strength requirements."""
        validations = ValidationUtils.validate_password_strength(password)
        # Require at least length, one uppercase, one lowercase, and one digit
        required_checks = ['length', 'uppercase', 'lowercase', 'digit']
        return all(validations[check] for check in required_checks)

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate Peru phone number format."""
        # Peru mobile: +51 9XX XXX XXX or 9XX XXX XXX
        # Peru landline: +51 XX XXX XXXX or XX XXX XXXX
        peru_mobile_pattern = r'^(\+51\s?)?9\d{8}$'
        peru_landline_pattern = r'^(\+51\s?)?\d{2}\s?\d{6,7}$'

        phone_clean = re.sub(r'\s+', '', phone)

        return (bool(re.match(peru_mobile_pattern, phone_clean)) or
                bool(re.match(peru_landline_pattern, phone_clean)))

    @staticmethod
    def validate_plate_number(plate: str) -> bool:
        """Validate Peru vehicle plate number format."""
        # Peru format: ABC-123 or AB-1234
        plate_pattern = r'^[A-Z]{2,3}-\d{3,4}$'
        return bool(re.match(plate_pattern, plate.upper()))

    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize and clean string input."""
        if not text:
            return ""

        # Remove leading/trailing whitespace and normalize spaces
        cleaned = re.sub(r'\s+', ' ', text.strip())

        # Truncate if max_length is specified
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        return cleaned


class StringUtils:
    """Utility functions for string operations."""

    @staticmethod
    def generate_uuid() -> str:
        """Generate a new UUID string."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a short random ID."""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to URL-friendly slug."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to specified length with optional suffix."""
        if len(text) <= max_length:
            return text

        truncated_length = max_length - len(suffix)
        return text[:truncated_length] + suffix

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for privacy (e.g., j***@example.com)."""
        if '@' not in email:
            return email

        local, domain = email.split('@', 1)
        if len(local) <= 2:
            return email

        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number for privacy."""
        if len(phone) <= 4:
            return phone

        return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]


class ListUtils:
    """Utility functions for list operations."""

    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split list into chunks of specified size."""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
        """Flatten a nested list."""
        return [item for sublist in nested_list for item in sublist]

    @staticmethod
    def remove_duplicates(lst: List[Any], key_func=None) -> List[Any]:
        """Remove duplicates from list, optionally using a key function."""
        if key_func is None:
            return list(dict.fromkeys(lst))

        seen = set()
        result = []
        for item in lst:
            key = key_func(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    @staticmethod
    def paginate_list(lst: List[Any], page: int, page_size: int) -> Dict[str, Any]:
        """Paginate a list and return pagination info."""
        total_items = len(lst)
        total_pages = (total_items + page_size - 1) // page_size

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        items = lst[start_idx:end_idx]

        return {
            'items': items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }


class DictUtils:
    """Utility functions for dictionary operations."""

    @staticmethod
    def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DictUtils.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def filter_none_values(data: Dict) -> Dict:
        """Remove keys with None values from dictionary."""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def flatten_dict(data: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DictUtils.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


class FileUtils:
    """Utility functions for file operations."""

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename."""
        return filename.lower().split('.')[-1] if '.' in filename else ''

    @staticmethod
    def is_allowed_file_type(filename: str, allowed_extensions: set) -> bool:
        """Check if file type is allowed."""
        extension = f".{FileUtils.get_file_extension(filename)}"
        return extension in allowed_extensions

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate unique filename while preserving extension."""
        name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, '')
        unique_id = StringUtils.generate_short_id()
        timestamp = int(datetime.utcnow().timestamp())

        if ext:
            return f"{name}_{timestamp}_{unique_id}.{ext}"
        return f"{name}_{timestamp}_{unique_id}"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)

        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1

        return f"{size:.1f}{size_names[i]}"


class BusinessUtils:
    """Business logic utility functions."""

    @staticmethod
    def calculate_route_duration(departure_time: str, arrival_time: str) -> int:
        """Calculate route duration in minutes."""
        dep_time = datetime.strptime(departure_time, "%H:%M")
        arr_time = datetime.strptime(arrival_time, "%H:%M")

        # Handle overnight trips
        if arr_time < dep_time:
            arr_time += timedelta(days=1)

        duration = arr_time - dep_time
        return int(duration.total_seconds() / 60)

    @staticmethod
    def format_duration(minutes: int) -> str:
        """Format duration in minutes to human readable format."""
        hours = minutes // 60
        mins = minutes % 60

        if hours == 0:
            return f"{mins}m"
        elif mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {mins}m"

    @staticmethod
    def calculate_seat_layout(capacity: int, seats_per_row: int = 4) -> Dict[str, Any]:
        """Calculate seat layout for a bus."""
        rows = (capacity + seats_per_row - 1) // seats_per_row

        layout = []
        seat_number = 1

        for row in range(rows):
            row_seats = []
            for seat in range(min(seats_per_row, capacity - seat_number + 1)):
                row_seats.append({
                    'number': seat_number,
                    'position': 'window' if seat in [0, seats_per_row - 1] else 'aisle'
                })
                seat_number += 1

                if seat_number > capacity:
                    break

            layout.append(row_seats)

            if seat_number > capacity:
                break

        return {
            'total_seats': capacity,
            'rows': rows,
            'seats_per_row': seats_per_row,
            'layout': layout
        }

    @staticmethod
    def generate_reservation_code() -> str:
        """Generate a unique reservation code."""
        prefix = "RES"
        timestamp = int(datetime.utcnow().timestamp())
        random_part = StringUtils.generate_short_id(4)
        return f"{prefix}{timestamp}{random_part}"

    @staticmethod
    def calculate_booking_fee(base_price: float, fee_percentage: float = 0.05) -> float:
        """Calculate booking fee based on base price."""
        return round(base_price * fee_percentage, 2)

    @staticmethod
    def calculate_total_price(base_price: float, include_fee: bool = True) -> float:
        """Calculate total price including fees."""
        total = base_price

        if include_fee:
            fee = BusinessUtils.calculate_booking_fee(base_price)
            total += fee

        return round(total, 2)