"""
Company SQLAlchemy model.
"""
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class CompanyModel(BaseModel):
    """Company database model."""

    __tablename__ = "companies"

    name = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    address = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    rating = Column(Float, nullable=False, default=0.0)
    total_trips = Column(Integer, nullable=False, default=0)

    # Relationships
    buses = relationship("BusModel", back_populates="company", cascade="all, delete-orphan")
    routes = relationship("RouteModel", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CompanyModel(id={self.id}, name={self.name}, status={self.status})>"
