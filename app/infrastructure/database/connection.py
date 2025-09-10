"""
Database connection management.
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ...core.config import settings

logger = logging.getLogger(__name__)

# Global engine instance
engine: AsyncEngine = None
async_session_maker: sessionmaker = None


def get_database_engine() -> AsyncEngine:
    """Get database engine instance."""
    global engine
    if engine is None:
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )
        logger.info("Database engine created")
    return engine


def get_async_session_maker() -> sessionmaker:
    """Get async session maker."""
    global async_session_maker
    if async_session_maker is None:
        async_session_maker = sessionmaker(
            bind=get_database_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
        logger.info("Async session maker created")
    return async_session_maker


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    Yields:
        AsyncSession: Database session
    """
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database_engine():
    """Close database engine."""
    global engine
    if engine:
        await engine.dispose()
        engine = None
        logger.info("Database engine closed")