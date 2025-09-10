"""
Schedule SQLAlchemy model.
"""
from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class ScheduleModel(BaseModel):
    """Schedule database model."""

    __tablename__ = "schedules"

    route_id = Column(String(36), ForeignKey("routes.id"), nullable=False, index=True)
    bus_id = Column(String(36), ForeignKey("buses.id"), nullable=False, index=True)
    departure_time = Column(String(5), nullable=False)  # HH:MM format
    arrival_time = Column(String(5), nullable=False)  # HH:MM format
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD format
    available_seats = Column(Integer, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")
    occupied_seats = Column(JSON, nullable=True, default=list)  # List of seat numbers
    reserved_seats = Column(JSON, nullable=True, default=list)  # List of seat numbers
    actual_departure_time = Column(String(5), nullable=True)  # HH:MM format
    actual_arrival_time = Column(String(5), nullable=True)  # HH:MM format

    # Relationships
    route = relationship("RouteModel", back_populates="schedules")
    bus = relationship("BusModel", back_populates="schedules")
    reservations = relationship("ReservationModel", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ScheduleModel(id={self.id}, date={self.date}, departure={self.departure_time})>"
