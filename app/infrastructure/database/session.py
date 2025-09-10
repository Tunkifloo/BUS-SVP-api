"""
Database session management.
"""
from typing import Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from ...shared.decorators import log_execution
import logging

logger = logging.getLogger(__name__)


class DatabaseSession:
    """Database session manager with transaction support."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._transaction = None

    @property
    def session(self) -> AsyncSession:
        """Get the underlying session."""
        return self._session

    @log_execution()
    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        if self._transaction is None:
            self._transaction = await self._session.begin()
            logger.debug("Transaction started")

    @log_execution()
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        if self._transaction:
            await self._transaction.commit()
            self._transaction = None
            logger.debug("Transaction committed")

    @log_execution()
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if self._transaction:
            await self._transaction.rollback()
            self._transaction = None
            logger.debug("Transaction rolled back")

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Execute a raw SQL query.

        Args:
            query: SQL query string
            parameters: Query parameters

        Returns:
            Query result
        """
        try:
            result = await self._session.execute(query, parameters or {})
            return result
        except SQLAlchemyError as e:
            logger.error(f"Query execution error: {e}")
            raise

    async def flush(self) -> None:
        """Flush pending changes to database."""
        try:
            await self._session.flush()
        except SQLAlchemyError as e:
            logger.error(f"Session flush error: {e}")
            raise

    async def refresh(self, instance: Any) -> None:
        """Refresh an instance from database."""
        try:
            await self._session.refresh(instance)
        except SQLAlchemyError as e:
            logger.error(f"Instance refresh error: {e}")
            raise