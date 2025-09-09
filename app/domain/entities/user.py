"""
User domain entity.
"""
from typing import Optional
from .base import AggregateRoot, DomainEvent
from ..value_objects import Email
from ...shared.constants import UserRole
from ...shared.validators import UserValidator
from ...core.exceptions import InvalidEntityStateException, ValidationException


class User(AggregateRoot):
    """User entity representing system users."""

    def __init__(
            self,
            email: str,
            name: str,
            password_hash: str,
            role: UserRole = UserRole.USER,
            phone: Optional[str] = None,
            is_active: bool = True,
            user_id: Optional[str] = None
    ):
        """
        Initialize User entity.

        Args:
            email: User email address
            name: User full name
            password_hash: Hashed password
            role: User role (default: USER)
            phone: Phone number (optional)
            is_active: Whether user is active (default: True)
            user_id: User ID (optional, will be generated if not provided)
        """
        super().__init__(user_id)

        # Validate and set properties
        self._email = Email(email)
        self._name = UserValidator.validate_name(name)
        self._password_hash = password_hash
        self._role = role
        self._phone = UserValidator.validate_phone(phone) if phone else None
        self._is_active = is_active
        self._email_verified = False
        self._last_login = None
        self._failed_login_attempts = 0

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="User.Created",
                entity_id=self.id,
                data={
                    "email": self._email.value,
                    "name": self._name,
                    "role": self._role.value
                }
            )
        )

    @property
    def email(self) -> Email:
        """Get user email."""
        return self._email

    @property
    def name(self) -> str:
        """Get user name."""
        return self._name

    @property
    def password_hash(self) -> str:
        """Get password hash."""
        return self._password_hash

    @property
    def role(self) -> UserRole:
        """Get user role."""
        return self._role

    @property
    def phone(self) -> Optional[str]:
        """Get user phone."""
        return self._phone

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self._is_active

    @property
    def email_verified(self) -> bool:
        """Check if email is verified."""
        return self._email_verified

    @property
    def last_login(self) -> Optional[str]:
        """Get last login timestamp."""
        return self._last_login

    @property
    def failed_login_attempts(self) -> int:
        """Get failed login attempts count."""
        return self._failed_login_attempts

    def update_profile(self, name: Optional[str] = None, phone: Optional[str] = None) -> None:
        """
        Update user profile information.

        Args:
            name: New name (optional)
            phone: New phone (optional)
        """
        if not self._is_active:
            raise InvalidEntityStateException("User", "inactive", "active")

        old_name = self._name
        old_phone = self._phone

        if name is not None:
            self._name = UserValidator.validate_name(name)

        if phone is not None:
            self._phone = UserValidator.validate_phone(phone) if phone else None

        if name != old_name or phone != old_phone:
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="User.ProfileUpdated",
                    entity_id=self.id,
                    data={
                        "old_name": old_name,
                        "new_name": self._name,
                        "old_phone": old_phone,
                        "new_phone": self._phone
                    }
                )
            )

    def change_email(self, new_email: str) -> None:
        """
        Change user email address.

        Args:
            new_email: New email address
        """
        if not self._is_active:
            raise InvalidEntityStateException("User", "inactive", "active")

        old_email = self._email.value
        new_email_obj = Email(new_email)

        if self._email.value != new_email_obj.value:
            self._email = new_email_obj
            self._email_verified = False  # Reset verification when email changes
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.EmailChanged",
                    entity_id=self.id,
                    data={
                        "old_email": old_email,
                        "new_email": new_email_obj.value
                    }
                )
            )

    def change_password(self, new_password_hash: str) -> None:
        """
        Change user password.

        Args:
            new_password_hash: New password hash
        """
        if not self._is_active:
            raise InvalidEntityStateException("User", "inactive", "active")

        self._password_hash = new_password_hash
        self._failed_login_attempts = 0  # Reset failed attempts on password change
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="User.PasswordChanged",
                entity_id=self.id
            )
        )

    def activate(self) -> None:
        """Activate user account."""
        if not self._is_active:
            self._is_active = True
            self._failed_login_attempts = 0
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.Activated",
                    entity_id=self.id
                )
            )

    def deactivate(self) -> None:
        """Deactivate user account."""
        if self._is_active:
            self._is_active = False
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.Deactivated",
                    entity_id=self.id
                )
            )

    def verify_email(self) -> None:
        """Mark email as verified."""
        if not self._email_verified:
            self._email_verified = True
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.EmailVerified",
                    entity_id=self.id,
                    data={"email": self._email.value}
                )
            )

    def record_successful_login(self) -> None:
        """Record successful login."""
        from ...shared.utils import DateTimeUtils

        self._last_login = DateTimeUtils.now_utc().isoformat()
        self._failed_login_attempts = 0
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="User.LoginSuccessful",
                entity_id=self.id,
                data={"login_time": self._last_login}
            )
        )

    def record_failed_login(self) -> None:
        """Record failed login attempt."""
        from ...shared.constants import BusinessRules

        self._failed_login_attempts += 1
        self._update_timestamp()

        # Deactivate account if too many failed attempts
        if self._failed_login_attempts >= BusinessRules.MAX_LOGIN_ATTEMPTS:
            self.deactivate()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.AccountLocked",
                    entity_id=self.id,
                    data={"failed_attempts": self._failed_login_attempts}
                )
            )
        else:
            self._add_domain_event(
                DomainEvent(
                    event_type="User.LoginFailed",
                    entity_id=self.id,
                    data={"failed_attempts": self._failed_login_attempts}
                )
            )

    def change_role(self, new_role: UserRole) -> None:
        """
        Change user role.

        Args:
            new_role: New user role
        """
        if self._role != new_role:
            old_role = self._role
            self._role = new_role
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="User.RoleChanged",
                    entity_id=self.id,
                    data={
                        "old_role": old_role.value,
                        "new_role": new_role.value
                    }
                )
            )

    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self._role == UserRole.ADMIN

    def is_company_admin(self) -> bool:
        """Check if user is a company administrator."""
        return self._role == UserRole.COMPANY_ADMIN

    def can_manage_companies(self) -> bool:
        """Check if user can manage companies."""
        return self._role == UserRole.ADMIN

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self._role == UserRole.ADMIN

    def get_masked_email(self) -> str:
        """Get masked email for privacy."""
        return self._email.mask()

    def get_display_name(self) -> str:
        """Get display name for UI."""
        return self._name

    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'email': self._email.value,
            'name': self._name,
            'role': self._role.value,
            'phone': self._phone,
            'is_active': self._is_active,
            'email_verified': self._email_verified,
            'last_login': self._last_login,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }