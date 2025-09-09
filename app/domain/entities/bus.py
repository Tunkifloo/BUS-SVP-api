"""
Bus domain entity.
"""
from typing import Optional, List, Dict, Any
from .base import AggregateRoot, DomainEvent
from ..value_objects import SeatNumber
from ...shared.constants import BusStatus
from ...shared.validators import BusValidator
from ...core.exceptions import InvalidEntityStateException, ValidationException


class Bus(AggregateRoot):
    """Bus entity representing transport vehicles."""

    def __init__(
            self,
            company_id: str,
            plate_number: str,
            capacity: int,
            model: str,
            status: BusStatus = BusStatus.ACTIVE,
            features: Optional[List[str]] = None,
            year: Optional[int] = None,
            bus_id: Optional[str] = None
    ):
        """
        Initialize Bus entity.

        Args:
            company_id: ID of the company that owns the bus
            plate_number: Vehicle plate number
            capacity: Seating capacity
            model: Bus model/brand
            status: Bus status (default: ACTIVE)
            features: List of bus features (optional)
            year: Manufacturing year (optional)
            bus_id: Bus ID (optional, will be generated if not provided)
        """
        super().__init__(bus_id)

        # Validate and set properties
        self._company_id = company_id
        self._plate_number = BusValidator.validate_plate_number(plate_number)
        self._capacity = BusValidator.validate_capacity(capacity)
        self._model = BusValidator.validate_model(model)
        self._status = status
        self._features = features or []
        self._year = year
        self._mileage = 0
        self._last_maintenance_date = None
        self._next_maintenance_due = None

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="Bus.Created",
                entity_id=self.id,
                data={
                    "company_id": self._company_id,
                    "plate_number": self._plate_number,
                    "capacity": self._capacity,
                    "model": self._model
                }
            )
        )

    @property
    def company_id(self) -> str:
        """Get company ID."""
        return self._company_id

    @property
    def plate_number(self) -> str:
        """Get plate number."""
        return self._plate_number

    @property
    def capacity(self) -> int:
        """Get seating capacity."""
        return self._capacity

    @property
    def model(self) -> str:
        """Get bus model."""
        return self._model

    @property
    def status(self) -> BusStatus:
        """Get bus status."""
        return self._status

    @property
    def features(self) -> List[str]:
        """Get bus features."""
        return self._features.copy()

    @property
    def year(self) -> Optional[int]:
        """Get manufacturing year."""
        return self._year

    @property
    def mileage(self) -> int:
        """Get current mileage."""
        return self._mileage

    @property
    def last_maintenance_date(self) -> Optional[str]:
        """Get last maintenance date."""
        return self._last_maintenance_date

    @property
    def next_maintenance_due(self) -> Optional[str]:
        """Get next maintenance due date."""
        return self._next_maintenance_due

    def update_basic_info(
            self,
            model: Optional[str] = None,
            year: Optional[int] = None,
            features: Optional[List[str]] = None
    ) -> None:
        """
        Update bus basic information.

        Args:
            model: New model (optional)
            year: New year (optional)
            features: New features list (optional)
        """
        if self._status == BusStatus.INACTIVE:
            raise InvalidEntityStateException("Bus", "inactive", "active")

        old_data = {
            "model": self._model,
            "year": self._year,
            "features": self._features.copy()
        }

        if model is not None:
            self._model = BusValidator.validate_model(model)

        if year is not None:
            from datetime import datetime
            current_year = datetime.now().year
            if year < 1980 or year > current_year + 1:
                raise ValidationException("year", year, f"Year must be between 1980 and {current_year + 1}")
            self._year = year

        if features is not None:
            self._features = [feature.strip() for feature in features if feature.strip()]

        # Check if anything changed
        if (self._model != old_data["model"] or
                self._year != old_data["year"] or
                self._features != old_data["features"]):
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.BasicInfoUpdated",
                    entity_id=self.id,
                    data={
                        "old_data": old_data,
                        "new_data": {
                            "model": self._model,
                            "year": self._year,
                            "features": self._features
                        }
                    }
                )
            )

    def change_plate_number(self, new_plate_number: str) -> None:
        """
        Change bus plate number.

        Args:
            new_plate_number: New plate number
        """
        if self._status == BusStatus.INACTIVE:
            raise InvalidEntityStateException("Bus", "inactive", "active")

        old_plate = self._plate_number
        new_plate = BusValidator.validate_plate_number(new_plate_number)

        if old_plate != new_plate:
            self._plate_number = new_plate
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.PlateNumberChanged",
                    entity_id=self.id,
                    data={
                        "old_plate": old_plate,
                        "new_plate": new_plate
                    }
                )
            )

    def activate(self) -> None:
        """Activate bus for service."""
        if self._status != BusStatus.ACTIVE:
            old_status = self._status
            self._status = BusStatus.ACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.Activated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value
                    }
                )
            )

    def send_to_maintenance(self, reason: Optional[str] = None) -> None:
        """
        Send bus to maintenance.

        Args:
            reason: Reason for maintenance (optional)
        """
        if self._status != BusStatus.MAINTENANCE:
            old_status = self._status
            self._status = BusStatus.MAINTENANCE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.SentToMaintenance",
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
        Deactivate bus.

        Args:
            reason: Reason for deactivation (optional)
        """
        if self._status != BusStatus.INACTIVE:
            old_status = self._status
            self._status = BusStatus.INACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.Deactivated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value,
                        "reason": reason
                    }
                )
            )

    def record_maintenance(self, maintenance_date: str, next_due_date: Optional[str] = None) -> None:
        """
        Record maintenance completion.

        Args:
            maintenance_date: Date when maintenance was completed
            next_due_date: Next maintenance due date (optional)
        """
        from datetime import datetime

        # Validate date format
        try:
            datetime.strptime(maintenance_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationException("maintenance_date", maintenance_date, "Invalid date format. Use YYYY-MM-DD")

        if next_due_date:
            try:
                datetime.strptime(next_due_date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException("next_due_date", next_due_date, "Invalid date format. Use YYYY-MM-DD")

        self._last_maintenance_date = maintenance_date
        self._next_maintenance_due = next_due_date

        # If bus was in maintenance, activate it
        if self._status == BusStatus.MAINTENANCE:
            self._status = BusStatus.ACTIVE

        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Bus.MaintenanceCompleted",
                entity_id=self.id,
                data={
                    "maintenance_date": maintenance_date,
                    "next_due_date": next_due_date,
                    "status": self._status.value
                }
            )
        )

    def update_mileage(self, new_mileage: int) -> None:
        """
        Update bus mileage.

        Args:
            new_mileage: New mileage reading
        """
        if new_mileage < 0:
            raise ValidationException("mileage", new_mileage, "Mileage cannot be negative")

        if new_mileage < self._mileage:
            raise ValidationException("mileage", new_mileage, "New mileage cannot be less than current mileage")

        old_mileage = self._mileage
        self._mileage = new_mileage
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Bus.MileageUpdated",
                entity_id=self.id,
                data={
                    "old_mileage": old_mileage,
                    "new_mileage": new_mileage
                }
            )
        )

    def add_feature(self, feature: str) -> None:
        """
        Add a feature to the bus.

        Args:
            feature: Feature to add
        """
        feature = feature.strip()
        if feature and feature not in self._features:
            self._features.append(feature)
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.FeatureAdded",
                    entity_id=self.id,
                    data={"feature": feature}
                )
            )

    def remove_feature(self, feature: str) -> None:
        """
        Remove a feature from the bus.

        Args:
            feature: Feature to remove
        """
        if feature in self._features:
            self._features.remove(feature)
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Bus.FeatureRemoved",
                    entity_id=self.id,
                    data={"feature": feature}
                )
            )

    def get_seat_map(self, seats_per_row: int = 4) -> Dict[str, Any]:
        """
        Get seat map for this bus.

        Args:
            seats_per_row: Number of seats per row (default: 4)

        Returns:
            Dictionary with seat layout information
        """
        return SeatNumber.generate_seat_map(self._capacity, seats_per_row)

    def validate_seat_number(self, seat_number: int) -> SeatNumber:
        """
        Validate and create SeatNumber for this bus.

        Args:
            seat_number: Seat number to validate

        Returns:
            SeatNumber object
        """
        return SeatNumber(seat_number, self._capacity)

    def is_available_for_service(self) -> bool:
        """Check if bus is available for service."""
        return self._status == BusStatus.ACTIVE and not self.is_deleted

    def is_in_maintenance(self) -> bool:
        """Check if bus is in maintenance."""
        return self._status == BusStatus.MAINTENANCE

    def needs_maintenance(self) -> bool:
        """Check if bus needs maintenance."""
        if not self._next_maintenance_due:
            return False

        from datetime import datetime
        try:
            due_date = datetime.strptime(self._next_maintenance_due, "%Y-%m-%d").date()
            today = datetime.now().date()
            return today >= due_date
        except ValueError:
            return False

    def get_status_display(self) -> str:
        """Get status display name."""
        status_map = {
            BusStatus.ACTIVE: "Activo",
            BusStatus.MAINTENANCE: "En Mantenimiento",
            BusStatus.INACTIVE: "Inactivo"
        }
        return status_map.get(self._status, self._status.value)

    def get_age(self) -> Optional[int]:
        """Get bus age in years."""
        if not self._year:
            return None

        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self._year

    def get_display_summary(self) -> Dict[str, Any]:
        """Get summary for display purposes."""
        return {
            "plate_number": self._plate_number,
            "model": self._model,
            "capacity": self._capacity,
            "status": self.get_status_display(),
            "available": self.is_available_for_service(),
            "needs_maintenance": self.needs_maintenance(),
            "features": self._features,
            "age": self.get_age()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert bus to dictionary representation."""
        return {
            'id': self.id,
            'company_id': self._company_id,
            'plate_number': self._plate_number,
            'capacity': self._capacity,
            'model': self._model,
            'status': self._status.value,
            'features': self._features,
            'year': self._year,
            'mileage': self._mileage,
            'last_maintenance_date': self._last_maintenance_date,
            'next_maintenance_due': self._next_maintenance_due,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }