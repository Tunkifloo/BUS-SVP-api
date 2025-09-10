"""
Bus SQLAlchemy model.
"""
from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class BusModel(BaseModel):
    """Bus database model."""

    __tablename__ = "buses"

    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False, index=True)
    plate_number = Column(String(20), unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    model = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    features = Column(JSON, nullable=True)
    year = Column(Integer, nullable=True)
    mileage = Column(Integer, nullable=False, default=0)
    last_maintenance_date = Column(String(10), nullable=True)  # YYYY-MM-DD format
    next_maintenance_due = Column(String(10), nullable=True)  # YYYY-MM-DD format

    # Relationships
    company = relationship("CompanyModel", back_populates="buses")
    schedules = relationship("ScheduleModel", back_populates="bus", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BusModel(id={self.id}, plate_number={self.plate_number}, capacity={self.capacity})>"
