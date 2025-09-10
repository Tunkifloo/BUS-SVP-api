"""
Reservation SQLAlchemy model.
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class ReservationModel(BaseModel):
    """Reservation database model."""

    __tablename__ = "reservations"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    schedule_id = Column(String(36), ForeignKey("schedules.id"), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="active")
    reservation_code = Column(String(50), unique=True, nullable=False, index=True)
    cancellation_reason = Column(String(500), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("UserModel", back_populates="reservations")
    schedule = relationship("ScheduleModel", back_populates="reservations")

    def __repr__(self) -> str:
        return f"<ReservationModel(id={self.id}, code={self.reservation_code}, status={self.status})>"
