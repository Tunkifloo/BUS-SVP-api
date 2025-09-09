"""
Company domain entity.
"""
from typing import Optional
from .base import AggregateRoot, DomainEvent
from ..value_objects import Email
from ...shared.constants import CompanyStatus
from ...shared.validators import CompanyValidator
from ...core.exceptions import InvalidEntityStateException


class Company(AggregateRoot):
    """Company entity representing transport companies."""

    def __init__(
            self,
            name: str,
            email: str,
            phone: str,
            status: CompanyStatus = CompanyStatus.ACTIVE,
            address: Optional[str] = None,
            description: Optional[str] = None,
            company_id: Optional[str] = None
    ):
        """
        Initialize Company entity.

        Args:
            name: Company name
            email: Company email address
            phone: Company phone number
            status: Company status (default: ACTIVE)
            address: Company address (optional)
            description: Company description (optional)
            company_id: Company ID (optional, will be generated if not provided)
        """
        super().__init__(company_id)

        # Validate and set properties
        self._name = CompanyValidator.validate_company_name(name)
        self._email = Email(email)
        self._phone = CompanyValidator.validate_company_phone(phone)
        self._status = status
        self._address = address.strip() if address else None
        self._description = description.strip() if description else None
        self._rating = 0.0
        self._total_trips = 0

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="Company.Created",
                entity_id=self.id,
                data={
                    "name": self._name,
                    "email": self._email.value,
                    "phone": self._phone
                }
            )
        )

    @property
    def name(self) -> str:
        """Get company name."""
        return self._name

    @property
    def email(self) -> Email:
        """Get company email."""
        return self._email

    @property
    def phone(self) -> str:
        """Get company phone."""
        return self._phone

    @property
    def status(self) -> CompanyStatus:
        """Get company status."""
        return self._status

    @property
    def address(self) -> Optional[str]:
        """Get company address."""
        return self._address

    @property
    def description(self) -> Optional[str]:
        """Get company description."""
        return self._description

    @property
    def rating(self) -> float:
        """Get company rating."""
        return self._rating

    @property
    def total_trips(self) -> int:
        """Get total number of trips."""
        return self._total_trips

    def update_basic_info(
            self,
            name: Optional[str] = None,
            phone: Optional[str] = None,
            address: Optional[str] = None,
            description: Optional[str] = None
    ) -> None:
        """
        Update company basic information.

        Args:
            name: New company name (optional)
            phone: New phone number (optional)
            address: New address (optional)
            description: New description (optional)
        """
        if self._status != CompanyStatus.ACTIVE:
            raise InvalidEntityStateException("Company", self._status.value, "active")

        old_data = {
            "name": self._name,
            "phone": self._phone,
            "address": self._address,
            "description": self._description
        }

        if name is not None:
            self._name = CompanyValidator.validate_company_name(name)

        if phone is not None:
            self._phone = CompanyValidator.validate_company_phone(phone)

        if address is not None:
            self._address = address.strip() if address else None

        if description is not None:
            self._description = description.strip() if description else None

        # Check if anything changed
        if (self._name != old_data["name"] or
                self._phone != old_data["phone"] or
                self._address != old_data["address"] or
                self._description != old_data["description"]):
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="Company.BasicInfoUpdated",
                    entity_id=self.id,
                    data={
                        "old_data": old_data,
                        "new_data": {
                            "name": self._name,
                            "phone": self._phone,
                            "address": self._address,
                            "description": self._description
                        }
                    }
                )
            )

    def change_email(self, new_email: str) -> None:
        """
        Change company email address.

        Args:
            new_email: New email address
        """
        if self._status != CompanyStatus.ACTIVE:
            raise InvalidEntityStateException("Company", self._status.value, "active")

        old_email = self._email.value
        new_email_obj = Email(new_email)

        if self._email.value != new_email_obj.value:
            self._email = new_email_obj
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Company.EmailChanged",
                    entity_id=self.id,
                    data={
                        "old_email": old_email,
                        "new_email": new_email_obj.value
                    }
                )
            )

    def activate(self) -> None:
        """Activate company."""
        if self._status != CompanyStatus.ACTIVE:
            old_status = self._status
            self._status = CompanyStatus.ACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Company.Activated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value
                    }
                )
            )

    def suspend(self, reason: Optional[str] = None) -> None:
        """
        Suspend company operations.

        Args:
            reason: Reason for suspension (optional)
        """
        if self._status != CompanyStatus.SUSPENDED:
            old_status = self._status
            self._status = CompanyStatus.SUSPENDED
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Company.Suspended",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value,
                        "reason": reason
                    }
                )
            )

    def deactivate(self, reason: Optional[str] = None) -> None:
        """
        Deactivate company.

        Args:
            reason: Reason for deactivation (optional)
        """
        if self._status != CompanyStatus.INACTIVE:
            old_status = self._status
            self._status = CompanyStatus.INACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Company.Deactivated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value,
                        "reason": reason
                    }
                )
            )

    def update_rating(self, new_rating: float) -> None:
        """
        Update company rating.

        Args:
            new_rating: New rating value (0.0 to 5.0)
        """
        if not 0.0 <= new_rating <= 5.0:
            from ...core.exceptions import ValidationException
            raise ValidationException("rating", new_rating, "Rating must be between 0.0 and 5.0")

        old_rating = self._rating
        self._rating = round(new_rating, 1)

        if old_rating != self._rating:
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="Company.RatingUpdated",
                    entity_id=self.id,
                    data={
                        "old_rating": old_rating,
                        "new_rating": self._rating
                    }
                )
            )

    def increment_trip_count(self) -> None:
        """Increment total trip count."""
        self._total_trips += 1
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Company.TripCompleted",
                entity_id=self.id,
                data={
                    "total_trips": self._total_trips
                }
            )
        )

    def is_active(self) -> bool:
        """Check if company is active."""
        return self._status == CompanyStatus.ACTIVE

    def is_suspended(self) -> bool:
        """Check if company is suspended."""
        return self._status == CompanyStatus.SUSPENDED

    def can_operate(self) -> bool:
        """Check if company can operate (active and not deleted)."""
        return self._status == CompanyStatus.ACTIVE and not self.is_deleted

    def get_status_display(self) -> str:
        """Get status display name."""
        status_map = {
            CompanyStatus.ACTIVE: "Activa",
            CompanyStatus.SUSPENDED: "Suspendida",
            CompanyStatus.INACTIVE: "Inactiva"
        }
        return status_map.get(self._status, self._status.value)

    def get_rating_display(self) -> str:
        """Get rating display string."""
        if self._rating == 0.0:
            return "Sin calificación"
        return f"{self._rating:.1f}/5.0"

    def get_display_summary(self) -> dict:
        """Get summary for display purposes."""
        return {
            "name": self._name,
            "rating": self.get_rating_display(),
            "total_trips": self._total_trips,
            "status": self.get_status_display(),
            "can_operate": self.can_operate()
        }

    def to_dict(self) -> dict:
        """Convert company to dictionary representation."""
        return {
            'id': self.id,
            'name': self._name,
            'email': self._email.value,
            'phone': self._phone,
            'status': self._status.value,
            'address': self._address,
            'description': self._description,
            'rating': self._rating,
            'total_trips': self._total_trips,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }