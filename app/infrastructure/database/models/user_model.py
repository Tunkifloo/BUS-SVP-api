"""
User SQLAlchemy model.
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base_model import BaseModel


class UserModel(BaseModel):
    """User database model."""

    __tablename__ = "users"

    email = Column(String(254), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(String(10), nullable=False, default="0")

    # Relationships
    reservations = relationship("ReservationModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
