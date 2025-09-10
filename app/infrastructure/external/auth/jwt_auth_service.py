"""
JWT authentication service implementation.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging

from ....application.interfaces.auth_service import AuthService
from ....core.config import settings
from ....core.exceptions import TokenExpiredException

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTAuthService(AuthService):
    """JWT authentication service implementation."""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    async def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create access token for user."""
        try:
            to_encode = user_data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            to_encode.update({"exp": expire})

            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )

            logger.info(f"Access token created for user {user_data.get('sub')}")
            return encoded_jwt

        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode access token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Check if token is expired
            exp = payload.get("exp")
            if exp is None:
                return None

            if datetime.utcnow() > datetime.fromtimestamp(exp):
                raise TokenExpiredException()

            return payload

        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
        except TokenExpiredException:
            logger.warning("Token has expired")
            raise

    async def create_password_reset_token(self, user_id: str) -> str:
        """Create password reset token."""
        try:
            data = {
                "sub": user_id,
                "type": "password_reset",
                "exp": datetime.utcnow() + timedelta(hours=24)  # 24 hours expiry
            }

            token = jwt.encode(data, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Password reset token created for user {user_id}")
            return token

        except Exception as e:
            logger.error(f"Failed to create password reset token: {str(e)}")
            raise

    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Check if it's a password reset token
            if payload.get("type") != "password_reset":
                return None

            # Check expiry
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None

            return payload.get("sub")

        except JWTError as e:
            logger.warning(f"Password reset token verification failed: {str(e)}")
            return None

    async def hash_password(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, hashed_password)