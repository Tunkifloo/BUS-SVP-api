"""
User repository implementation.
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ....domain.entities.user import User
from ....domain.repositories.user_repository import UserRepository
from ....domain.value_objects.email import Email
from ....shared.constants import UserRole
from ..models.user_model import UserModel
from .base_repository import BaseRepository
from ....shared.decorators import log_execution


class UserRepositoryImpl(BaseRepository[User, UserModel], UserRepository):
    """User repository implementation."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert model to entity."""
        return User(
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            phone=model.phone,
            is_active=model.is_active,
            user_id=model.id
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert entity to model."""
        model = UserModel(
            id=entity.id,
            email=entity.email.value,
            name=entity.name,
            password_hash=entity.password_hash,
            role=entity.role.value,
            phone=entity.phone,
            is_active=entity.is_active,
            email_verified=entity.email_verified,
            last_login=entity.last_login,
            failed_login_attempts=str(entity.failed_login_attempts)
        )
        return model

    @log_execution()
    async def save(self, user: User) -> User:
        """Save user entity."""
        model = self._entity_to_model(user)
        saved_model = await self.save_model(model)
        return self._model_to_entity(saved_model)

    @log_execution()
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID."""
        model = await self.find_by_id_model(user_id)
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    @log_execution()
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Find all users with pagination."""
        models = await self.find_all_models(limit=limit, offset=offset)
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def find_by_role(self, role: str, limit: int = 100, offset: int = 0) -> List[User]:
        """Find users by role."""
        models = await self.find_all_models(
            limit=limit,
            offset=offset,
            filters={"role": role}
        )
        return [self._model_to_entity(model) for model in models]

    @log_execution()
    async def update(self, user: User) -> User:
        """Update user entity."""
        # Find existing model
        existing_model = await self.find_by_id_model(user.id)
        if not existing_model:
            raise ValueError(f"User with id {user.id} not found")

        # Update model fields
        existing_model.email = user.email.value
        existing_model.name = user.name
        existing_model.password_hash = user.password_hash
        existing_model.role = user.role.value
        existing_model.phone = user.phone
        existing_model.is_active = user.is_active
        existing_model.email_verified = user.email_verified
        # Convert string to datetime if needed
        if user.last_login:
            from datetime import datetime
            existing_model.last_login = datetime.fromisoformat(user.last_login.replace('Z', '+00:00'))
        else:
            existing_model.last_login = None
        existing_model.failed_login_attempts = str(user.failed_login_attempts)

        updated_model = await self.update_model(existing_model)
        return self._model_to_entity(updated_model)

    @log_execution()
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID."""
        return await self.delete_model(user_id)

    @log_execution()
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email.value)
        )
        return result.scalar_one_or_none() is not None

    @log_execution()
    async def count_total(self) -> int:
        """Count total users."""
        return await self.count_models()