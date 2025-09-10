"""
Login user use case.
"""
from typing import Optional, Dict, Any
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.core.security import SecurityConfig
from app.core.exceptions import InvalidCredentialsException
from app.shared.decorators import log_execution


class LoginUserUseCase:
    """Use case for user authentication."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    @log_execution(log_duration=True)
    async def execute(self, email: str, password: str) -> Dict[str, Any]:
        """
        Execute login use case.

        Args:
            email: User email
            password: User password

        Returns:
            Authentication result with token and user info

        Raises:
            InvalidCredentialsException: If credentials are invalid
        """
        # Find user by email
        email_obj = Email(email)
        user = await self._user_repository.find_by_email(email_obj)

        if not user:
            raise InvalidCredentialsException()

        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsException()

        # Verify password
        if not SecurityConfig.verify_password(password, user.password_hash):
            # Record failed login attempt
            user.record_failed_login()
            await self._user_repository.update(user)
            raise InvalidCredentialsException()

        # Record successful login
        user.record_successful_login()
        await self._user_repository.update(user)

        # Generate access token
        token_data = {
            "sub": user.id,
            "email": user.email.value,
            "role": user.role.value,
            "name": user.name
        }
        access_token = SecurityConfig.create_access_token(token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email.value,
                "name": user.name,
                "role": user.role.value,
                "is_active": user.is_active,
                "email_verified": user.email_verified,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }