"""
Core security configuration and utilities.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import settings
from .exceptions import TokenExpiredException, InvalidCredentialsException

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityConfig:
    """Security configuration and utilities."""

    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
            data: dict,
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            SecurityConfig.SECRET_KEY,
            algorithm=SecurityConfig.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                SecurityConfig.SECRET_KEY,
                algorithms=[SecurityConfig.ALGORITHM]
            )
            return payload
        except JWTError:
            raise TokenExpiredException()


class PermissionChecker:
    """Permission checking utilities."""

    ADMIN_PERMISSIONS = [
        "manage_users",
        "manage_companies",
        "manage_buses",
        "manage_routes",
        "manage_schedules",
        "view_all_reservations",
        "system_administration"
    ]

    USER_PERMISSIONS = [
        "search_routes",
        "create_reservation",
        "view_own_reservations",
        "cancel_own_reservation"
    ]

    COMPANY_ADMIN_PERMISSIONS = [
        "manage_own_buses",
        "manage_own_routes",
        "manage_own_schedules",
        "view_own_reservations"
    ]

    @classmethod
    def get_user_permissions(cls, user_role: str) -> List[str]:
        """Get permissions for a user role."""
        if user_role == "admin":
            return cls.ADMIN_PERMISSIONS + cls.USER_PERMISSIONS + cls.COMPANY_ADMIN_PERMISSIONS
        elif user_role == "company_admin":
            return cls.COMPANY_ADMIN_PERMISSIONS + cls.USER_PERMISSIONS
        elif user_role == "user":
            return cls.USER_PERMISSIONS
        else:
            return []

    @classmethod
    def has_permission(cls, user_role: str, required_permission: str) -> bool:
        """Check if a user role has a specific permission."""
        user_permissions = cls.get_user_permissions(user_role)
        return required_permission in user_permissions


def get_current_user_permissions(user_role: str) -> List[str]:
    """Get current user permissions based on role."""
    return PermissionChecker.get_user_permissions(user_role)


def require_permission(required_permission: str):
    """Decorator to require specific permission."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This will be implemented in the web layer with dependency injection
            return await func(*args, **kwargs)

        return wrapper

    return decorator