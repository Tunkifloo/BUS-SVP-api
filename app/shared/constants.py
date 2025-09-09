"""
Shared constants across the application.
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    COMPANY_ADMIN = "company_admin"
    USER = "user"


class ReservationStatus(str, Enum):
    """Reservation status values."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class BusStatus(str, Enum):
    """Bus status values."""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class RouteStatus(str, Enum):
    """Route status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ScheduleStatus(str, Enum):
    """Schedule status values."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CompanyStatus(str, Enum):
    """Company status values."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class NotificationType(str, Enum):
    """Notification types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


# Business Rules Constants
class BusinessRules:
    """Business rules and constraints."""

    # Reservation Rules
    MIN_BOOKING_HOURS_ADVANCE = 2  # Minimum hours before departure to book
    MAX_BOOKING_DAYS_ADVANCE = 90  # Maximum days in advance to book
    CANCELLATION_DEADLINE_HOURS = 4  # Hours before departure to cancel

    # Seat Rules
    MIN_SEAT_NUMBER = 1
    MAX_SEAT_NUMBER = 60
    DEFAULT_BUS_CAPACITY = 40

    # User Rules
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    PASSWORD_RESET_EXPIRY_HOURS = 24

    # Company Rules
    MIN_COMPANY_NAME_LENGTH = 3
    MAX_COMPANY_NAME_LENGTH = 100

    # Route Rules
    MIN_ROUTE_PRICE = 5.0
    MAX_ROUTE_PRICE = 500.0
    MIN_ROUTE_DURATION_MINUTES = 30
    MAX_ROUTE_DURATION_HOURS = 48

    # Schedule Rules
    MIN_SCHEDULE_INTERVAL_MINUTES = 30
    MAX_SCHEDULES_PER_DAY = 10


# API Constants
class APIConstants:
    """API-related constants."""

    # HTTP Status Messages
    SUCCESS_MESSAGE = "Operation completed successfully"
    CREATED_MESSAGE = "Resource created successfully"
    UPDATED_MESSAGE = "Resource updated successfully"
    DELETED_MESSAGE = "Resource deleted successfully"
    NOT_FOUND_MESSAGE = "Resource not found"
    UNAUTHORIZED_MESSAGE = "Unauthorized access"
    FORBIDDEN_MESSAGE = "Access forbidden"
    VALIDATION_ERROR_MESSAGE = "Validation error"

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Rate Limiting
    DEFAULT_RATE_LIMIT = 100  # requests per minute
    AUTH_RATE_LIMIT = 10  # login attempts per minute


# File Constants
class FileConstants:
    """File handling constants."""

    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE_MB = 5

    # Directories
    UPLOAD_DIR = "uploads"
    TEMP_DIR = "temp"
    BACKUP_DIR = "backups"

    # File naming
    MAX_FILENAME_LENGTH = 255


# Email Constants
class EmailConstants:
    """Email-related constants."""

    # Email types
    RESERVATION_CONFIRMATION = "reservation_confirmation"
    RESERVATION_CANCELLATION = "reservation_cancellation"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_ACTIVATION = "account_activation"

    # Email settings
    MAX_EMAIL_LENGTH = 254
    EMAIL_RETRY_ATTEMPTS = 3
    EMAIL_RETRY_DELAY_SECONDS = 30


# Database Constants
class DatabaseConstants:
    """Database-related constants."""

    # Connection settings
    CONNECTION_POOL_SIZE = 10
    MAX_OVERFLOW = 20
    POOL_TIMEOUT = 30

    # Query limits
    DEFAULT_QUERY_LIMIT = 1000
    MAX_BULK_INSERT_SIZE = 1000


# Timezone Constants
class TimezoneConstants:
    """Timezone-related constants."""

    DEFAULT_TIMEZONE = "America/Lima"  # Peru timezone
    UTC_TIMEZONE = "UTC"

    # Common Peru timezones
    PERU_TIMEZONES = [
        "America/Lima",
        "America/Iquitos"
    ]


# Cache Constants
class CacheConstants:
    """Cache-related constants."""

    # TTL in seconds
    SHORT_CACHE_TTL = 300  # 5 minutes
    MEDIUM_CACHE_TTL = 1800  # 30 minutes
    LONG_CACHE_TTL = 3600  # 1 hour

    # Cache keys
    ROUTES_CACHE_KEY = "routes:all"
    COMPANIES_CACHE_KEY = "companies:active"
    USER_PERMISSIONS_CACHE_KEY = "user:permissions:{user_id}"


# Logging Constants
class LoggingConstants:
    """Logging-related constants."""

    # Log levels
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    # Log categories
    SECURITY_LOG = "security"
    BUSINESS_LOG = "business"
    SYSTEM_LOG = "system"
    AUDIT_LOG = "audit"