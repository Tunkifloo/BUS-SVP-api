"""
Health check router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ....infrastructure.database.connection import get_database_session
from ....core.config import settings

router = APIRouter(prefix="/health")


@router.get("/")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@router.get("/database")
async def database_health_check(session: AsyncSession = Depends(get_database_session)):
    """Database connectivity health check."""
    try:
        # Execute a simple query
        result = await session.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


@router.get("/detailed")
async def detailed_health_check(session: AsyncSession = Depends(get_database_session)):
    """Detailed health check with system information."""
    try:
        # Check database
        await session.execute(text("SELECT 1"))
        db_status = "healthy"

    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "database": db_status,
        "environment": "development" if settings.debug else "production"
    }