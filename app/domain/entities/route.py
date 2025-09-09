"""
Route domain entity.
"""
from typing import Optional, Dict, Any
from .base import AggregateRoot, DomainEvent
from ..value_objects import Money
from ...shared.constants import RouteStatus
from ...shared.validators import RouteValidator
from ...shared.utils import BusinessUtils
from ...core.exceptions import InvalidEntityStateException, ValidationException


class Route(AggregateRoot):
    """Route entity representing travel routes between cities."""

    def __init__(
            self,
            company_id: str,
            origin: str,
            destination: str,
            price: float,
            duration: str,
            status: RouteStatus = RouteStatus.ACTIVE,
            distance_km: Optional[int] = None,
            description: Optional[str] = None,
            route_id: Optional[str] = None
    ):
        """
        Initialize Route entity.

        Args:
            company_id: ID of the company that operates the route
            origin: Origin city
            destination: Destination city
            price: Route price
            duration: Duration of the trip (e.g., "2h 30m")
            status: Route status (default: ACTIVE)
            distance_km: Distance in kilometers (optional)
            description: Route description (optional)
            route_id: Route ID (optional, will be generated if not provided)
        """
        super().__init__(route_id)

        # Validate and set properties
        self._company_id = company_id
        self._origin = RouteValidator.validate_origin(origin)
        self._destination = RouteValidator.validate_destination(destination)

        # Validate that origin and destination are different
        RouteValidator.validate_different_cities(self._origin, self._destination)

        self._price = Money(RouteValidator.validate_price(price))
        self._duration = RouteValidator.validate_duration(duration)
        self._status = status
        self._distance_km = distance_km
        self._description = description.strip() if description else None
        self._total_bookings = 0
        self._popularity_score = 0.0

        # Add domain event
        self._add_domain_event(
            DomainEvent(
                event_type="Route.Created",
                entity_id=self.id,
                data={
                    "company_id": self._company_id,
                    "origin": self._origin,
                    "destination": self._destination,
                    "price": self._price.to_float(),
                    "duration": self._duration
                }
            )
        )

    @property
    def company_id(self) -> str:
        """Get company ID."""
        return self._company_id

    @property
    def origin(self) -> str:
        """Get origin city."""
        return self._origin

    @property
    def destination(self) -> str:
        """Get destination city."""
        return self._destination

    @property
    def price(self) -> Money:
        """Get route price."""
        return self._price

    @property
    def duration(self) -> str:
        """Get trip duration."""
        return self._duration

    @property
    def status(self) -> RouteStatus:
        """Get route status."""
        return self._status

    @property
    def distance_km(self) -> Optional[int]:
        """Get distance in kilometers."""
        return self._distance_km

    @property
    def description(self) -> Optional[str]:
        """Get route description."""
        return self._description

    @property
    def total_bookings(self) -> int:
        """Get total number of bookings."""
        return self._total_bookings

    @property
    def popularity_score(self) -> float:
        """Get popularity score."""
        return self._popularity_score

    def update_basic_info(
            self,
            duration: Optional[str] = None,
            distance_km: Optional[int] = None,
            description: Optional[str] = None
    ) -> None:
        """
        Update route basic information.

        Args:
            duration: New duration (optional)
            distance_km: New distance (optional)
            description: New description (optional)
        """
        if self._status != RouteStatus.ACTIVE:
            raise InvalidEntityStateException("Route", self._status.value, "active")

        old_data = {
            "duration": self._duration,
            "distance_km": self._distance_km,
            "description": self._description
        }

        if duration is not None:
            self._duration = RouteValidator.validate_duration(duration)

        if distance_km is not None:
            if distance_km < 0:
                raise ValidationException("distance_km", distance_km, "Distance cannot be negative")
            self._distance_km = distance_km

        if description is not None:
            self._description = description.strip() if description else None

        # Check if anything changed
        if (self._duration != old_data["duration"] or
                self._distance_km != old_data["distance_km"] or
                self._description != old_data["description"]):
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type="Route.BasicInfoUpdated",
                    entity_id=self.id,
                    data={
                        "old_data": old_data,
                        "new_data": {
                            "duration": self._duration,
                            "distance_km": self._distance_km,
                            "description": self._description
                        }
                    }
                )
            )

    def update_price(self, new_price: float) -> None:
        """
        Update route price.

        Args:
            new_price: New price
        """
        if self._status != RouteStatus.ACTIVE:
            raise InvalidEntityStateException("Route", self._status.value, "active")

        old_price = self._price.to_float()
        validated_price = RouteValidator.validate_price(new_price)
        new_price_obj = Money(validated_price)

        if not self._price.is_equal_to(new_price_obj):
            self._price = new_price_obj
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Route.PriceUpdated",
                    entity_id=self.id,
                    data={
                        "old_price": old_price,
                        "new_price": validated_price,
                        "price_change_percent": ((validated_price - old_price) / old_price) * 100
                    }
                )
            )

    def activate(self) -> None:
        """Activate route."""
        if self._status != RouteStatus.ACTIVE:
            old_status = self._status
            self._status = RouteStatus.ACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Route.Activated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value
                    }
                )
            )

    def suspend(self, reason: Optional[str] = None) -> None:
        """
        Suspend route operations.

        Args:
            reason: Reason for suspension (optional)
        """
        if self._status != RouteStatus.SUSPENDED:
            old_status = self._status
            self._status = RouteStatus.SUSPENDED
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Route.Suspended",
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
        Deactivate route.

        Args:
            reason: Reason for deactivation (optional)
        """
        if self._status != RouteStatus.INACTIVE:
            old_status = self._status
            self._status = RouteStatus.INACTIVE
            self._update_timestamp()

            self._add_domain_event(
                DomainEvent(
                    event_type="Route.Deactivated",
                    entity_id=self.id,
                    data={
                        "old_status": old_status.value,
                        "new_status": self._status.value,
                        "reason": reason
                    }
                )
            )

    def record_booking(self) -> None:
        """Record a new booking for this route."""
        self._total_bookings += 1
        self._calculate_popularity_score()
        self._update_timestamp()

        self._add_domain_event(
            DomainEvent(
                event_type="Route.BookingRecorded",
                entity_id=self.id,
                data={
                    "total_bookings": self._total_bookings,
                    "popularity_score": self._popularity_score
                }
            )
        )

    def _calculate_popularity_score(self) -> None:
        """Calculate popularity score based on bookings and other factors."""
        # Simple popularity calculation - can be enhanced with more factors
        base_score = min(self._total_bookings / 100.0, 5.0)  # Max 5.0 based on bookings

        # Additional factors can be added here (reviews, frequency, etc.)
        self._popularity_score = round(base_score, 2)

    def get_duration_minutes(self) -> int:
        """
        Get duration in minutes.

        Returns:
            Duration in minutes
        """
        return BusinessUtils.calculate_route_duration("00:00", self._duration) if ":" in self._duration else 0

    def get_formatted_duration(self) -> str:
        """Get formatted duration for display."""
        return BusinessUtils.format_duration(self.get_duration_minutes())

    def calculate_total_price(self, include_fees: bool = True) -> Money:
        """
        Calculate total price including fees.

        Args:
            include_fees: Whether to include booking fees

        Returns:
            Total price as Money object
        """
        total = BusinessUtils.calculate_total_price(self._price.to_float(), include_fees)
        return Money(total)

    def get_route_display_name(self) -> str:
        """Get route display name."""
        return f"{self._origin} → {self._destination}"

    def get_reverse_route_name(self) -> str:
        """Get reverse route display name."""
        return f"{self._destination} → {self._origin}"

    def is_active(self) -> bool:
        """Check if route is active."""
        return self._status == RouteStatus.ACTIVE

    def is_suspended(self) -> bool:
        """Check if route is suspended."""
        return self._status == RouteStatus.SUSPENDED

    def can_accept_bookings(self) -> bool:
        """Check if route can accept bookings."""
        return self._status == RouteStatus.ACTIVE and not self.is_deleted

    def get_status_display(self) -> str:
        """Get status display name."""
        status_map = {
            RouteStatus.ACTIVE: "Activa",
            RouteStatus.SUSPENDED: "Suspendida",
            RouteStatus.INACTIVE: "Inactiva"
        }
        return status_map.get(self._status, self._status.value)

    def get_popularity_display(self) -> str:
        """Get popularity display string."""
        if self._popularity_score == 0.0:
            return "Nueva ruta"
        elif self._popularity_score < 2.0:
            return "Baja demanda"
        elif self._popularity_score < 4.0:
            return "Demanda moderada"
        else:
            return "Alta demanda"

    def matches_search(self, origin: Optional[str] = None, destination: Optional[str] = None) -> bool:
        """
        Check if route matches search criteria.

        Args:
            origin: Origin city to match (optional)
            destination: Destination city to match (optional)

        Returns:
            True if route matches search criteria
        """
        if origin and not self._origin.lower().startswith(origin.lower()):
            return False

        if destination and not self._destination.lower().startswith(destination.lower()):
            return False

        return True

    def get_display_summary(self) -> Dict[str, Any]:
        """Get summary for display purposes."""
        return {
            "route_name": self.get_route_display_name(),
            "price": self._price.to_string(),
            "duration": self._duration,
            "status": self.get_status_display(),
            "popularity": self.get_popularity_display(),
            "total_bookings": self._total_bookings,
            "can_book": self.can_accept_bookings(),
            "distance": f"{self._distance_km} km" if self._distance_km else "No especificado"
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert route to dictionary representation."""
        return {
            'id': self.id,
            'company_id': self._company_id,
            'origin': self._origin,
            'destination': self._destination,
            'price': self._price.to_float(),
            'duration': self._duration,
            'status': self._status.value,
            'distance_km': self._distance_km,
            'description': self._description,
            'total_bookings': self._total_bookings,
            'popularity_score': self._popularity_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }