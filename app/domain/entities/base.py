"""
Base entity class for domain entities.
"""
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional
from ...shared.utils import StringUtils, DateTimeUtils


class DomainEvent:
    """Base class for domain events."""

    def __init__(self, event_type: str, entity_id: str, data: Optional[Dict[str, Any]] = None):
        self.event_type = event_type
        self.entity_id = entity_id
        self.data = data or {}
        self.occurred_at = DateTimeUtils.now_utc()
        self.event_id = StringUtils.generate_uuid()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'entity_id': self.entity_id,
            'data': self.data,
            'occurred_at': self.occurred_at.isoformat()
        }


class BaseEntity(ABC):
    """Base class for all domain entities."""

    def __init__(self, entity_id: Optional[str] = None):
        self._id = entity_id or StringUtils.generate_uuid()
        self._created_at = DateTimeUtils.now_utc()
        self._updated_at = DateTimeUtils.now_utc()
        self._version = 1
        self._domain_events: List[DomainEvent] = []

    @property
    def id(self) -> str:
        """Get entity ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    @property
    def version(self) -> int:
        """Get entity version for optimistic locking."""
        return self._version

    @property
    def domain_events(self) -> List[DomainEvent]:
        """Get domain events."""
        return self._domain_events.copy()

    def _update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self._updated_at = DateTimeUtils.now_utc()
        self._version += 1

    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    def __eq__(self, other) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self._id)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(id={self._id})"


class AggregateRoot(BaseEntity):
    """Base class for aggregate roots."""

    def __init__(self, entity_id: Optional[str] = None):
        super().__init__(entity_id)
        self._is_deleted = False

    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft deleted."""
        return self._is_deleted

    def mark_as_deleted(self) -> None:
        """Mark entity as soft deleted."""
        if not self._is_deleted:
            self._is_deleted = True
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type=f"{self.__class__.__name__}.Deleted",
                    entity_id=self._id
                )
            )

    def restore(self) -> None:
        """Restore soft deleted entity."""
        if self._is_deleted:
            self._is_deleted = False
            self._update_timestamp()
            self._add_domain_event(
                DomainEvent(
                    event_type=f"{self.__class__.__name__}.Restored",
                    entity_id=self._id
                )
            )


class ValueObject(ABC):
    """Base class for value objects."""

    def __eq__(self, other) -> bool:
        """Value objects are equal if all their attributes are equal."""
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash based on all attributes."""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """String representation."""
        attrs = ', '.join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"