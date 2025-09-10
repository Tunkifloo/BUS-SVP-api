"""
Register user use case.
"""
from typing import Dict, Any, Optional
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.shared.constants import UserRole
from app.core.security import SecurityConfig
from app.core.exceptions import EntityAlreadyExistsException
from app.shared.decorators import log_execution


class RegisterUserUseCase:
    """Use case for user registration."""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    @log_execution(log_duration=True)
    async def execute(
            self,
            name: str,
            email: str,
            password: str,
            phone: Optional[str] = None,
            role: UserRole = UserRole.USER
    ) -> Dict[str, Any]:
        """
        Execute registration use case.

        Args:
            name: User full name
            email: User email
            password: User password
            phone: User phone (optional)
            role: User role (default: USER)

        Returns:
            Created user information

        Raises:
            EntityAlreadyExistsException: If email already exists
        """
        # Check if email already exists
        email_obj = Email(email)
        existing_user = await self._user_repository.find_by_email(email_obj)

        if existing_user:
            raise EntityAlreadyExistsException("User", email)

        # Hash password
        password_hash = SecurityConfig.get_password_hash(password)

        # Create user entity
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
            role=role,
            phone=phone,
            is_active=True
        )

        # Save user
        saved_user = await self._user_repository.save(user)

        return {
            "id": saved_user.id,
            "email": saved_user.email.value,
            "name": saved_user.name,
            "role": saved_user.role.value,
            "phone": saved_user.phone,
            "is_active": saved_user.is_active,
            "created_at": saved_user.created_at.isoformat()
        }