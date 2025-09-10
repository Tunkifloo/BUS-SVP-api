"""
Base repository implementation.
"""
from typing import TypeVar, Generic, List, Optional, Type, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from ....shared.decorators import log_execution
import logging

logger = logging.getLogger(__name__)

EntityType = TypeVar('EntityType')
ModelType = TypeVar('ModelType')


class BaseRepository(Generic[EntityType, ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self._session = session
        self._model_class = model_class

    @log_execution()
    async def save_model(self, model: ModelType) -> ModelType:
        """
        Save model to database.

        Args:
            model: Model instance to save

        Returns:
            Saved model instance
        """
        try:
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
            return model
        except SQLAlchemyError as e:
            logger.error(f"Error saving {self._model_class.__name__}: {e}")
            await self._session.rollback()
            raise

    @log_execution()
    async def update_model(self, model: ModelType) -> ModelType:
        """
        Update model in database.

        Args:
            model: Model instance to update

        Returns:
            Updated model instance
        """
        try:
            # Increment version for optimistic locking
            if hasattr(model, 'version'):
                model.version += 1

            await self._session.flush()
            await self._session.refresh(model)
            return model
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self._model_class.__name__}: {e}")
            await self._session.rollback()
            raise

    @log_execution()
    async def find_by_id_model(self, entity_id: str) -> Optional[ModelType]:
        """
        Find model by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Model instance or None
        """
        try:
            result = await self._session.execute(
                select(self._model_class).where(self._model_class.id == entity_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self._model_class.__name__} by id {entity_id}: {e}")
            raise

    @log_execution()
    async def find_all_models(
            self,
            limit: int = 100,
            offset: int = 0,
            filters: Optional[Dict[str, Any]] = None,
            order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Find all models with pagination and filters.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            filters: Filter conditions
            order_by: Order by field

        Returns:
            List of model instances
        """
        try:
            query = select(self._model_class)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self._model_class, field):
                        query = query.where(getattr(self._model_class, field) == value)

            # Apply ordering
            if order_by and hasattr(self._model_class, order_by):
                query = query.order_by(getattr(self._model_class, order_by))
            else:
                query = query.order_by(self._model_class.created_at.desc())

            # Apply pagination
            query = query.limit(limit).offset(offset)

            result = await self._session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error finding all {self._model_class.__name__}: {e}")
            raise

    @log_execution()
    async def delete_model(self, entity_id: str) -> bool:
        """
        Delete model by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if deletion was successful
        """
        try:
            result = await self._session.execute(
                delete(self._model_class).where(self._model_class.id == entity_id)
            )
            return result.rowcount > 0
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self._model_class.__name__} with id {entity_id}: {e}")
            await self._session.rollback()
            raise

    @log_execution()
    async def count_models(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count models with optional filters.

        Args:
            filters: Filter conditions

        Returns:
            Count of models
        """
        try:
            query = select(func.count(self._model_class.id))

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self._model_class, field):
                        query = query.where(getattr(self._model_class, field) == value)

            result = await self._session.execute(query)
            return result.scalar() or 0
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self._model_class.__name__}: {e}")
            raise

    @log_execution()
    async def exists_model(self, entity_id: str) -> bool:
        """
        Check if model exists by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if model exists
        """
        try:
            result = await self._session.execute(
                select(func.count(self._model_class.id)).where(self._model_class.id == entity_id)
            )
            count = result.scalar() or 0
            return count > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self._model_class.__name__} with id {entity_id}: {e}")
            raise