"""
Route SQLAlchemy model.
"""
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class RouteModel(BaseModel):
    """Route database model."""

    __tablename__ = "routes"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    origin = Column(String(50), nullable=False, index=True)
    destination = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    duration = Column(String(20), nullable=False)  # e.g., "2h 30m"
    status = Column(String(20), nullable=False, default="active")
    distance_km = Column(Integer, nullable=True)
    description = Column(String(1000), nullable=True)
    total_bookings = Column(Integer, nullable=False, default=0)
    popularity_score = Column(Float, nullable=False, default=0.0)

    # Relationships
    company = relationship("CompanyModel", back_populates="routes")
    schedules = relationship("ScheduleModel", back_populates="route", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<RouteModel(id={self.id}, origin={self.origin}, destination={self.destination})>"
