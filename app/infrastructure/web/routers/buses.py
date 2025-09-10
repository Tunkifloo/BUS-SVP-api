"""
Buses router for admin operations.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.admin.manage_buses import ManageBusesUseCase
from ....infrastructure.database.repositories.bus_repository_impl import BusRepositoryImpl
from ....infrastructure.database.repositories.company_repository_impl import CompanyRepositoryImpl
from ..schemas.bus_schema import BusCreateSchema, BusUpdateSchema, BusResponseSchema
from ....core.exceptions import EntityNotFoundException, EntityAlreadyExistsException

router = APIRouter(prefix="/buses")


@router.get("/public", response_model=List[BusResponseSchema])
async def get_public_buses(
        company_id: Optional[str] = Query(None),
        active_only: bool = True,
        session: AsyncSession = Depends(get_database_session)
):
    """Get all buses (public endpoint for testing)."""
    try:
        # Initialize repositories and use case
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        buses = await manage_use_case.get_buses(
            company_id=company_id,
            available_only=active_only
        )
        return buses

    except Exception as e:
        logger.error(f"Error in get_public_buses: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve buses: {str(e)}"
        )


@router.post("/public", response_model=BusResponseSchema)
async def create_public_bus(
        bus_data: BusCreateSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Create a new bus (public endpoint for testing)."""
    try:
        # Initialize repositories and use case
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        result = await manage_use_case.create_bus(
            company_id=bus_data.company_id,
            plate_number=bus_data.plate_number,
            capacity=bus_data.capacity,
            model=bus_data.model,
            year=bus_data.year,
            features=bus_data.features
        )
        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus creation failed"
        )


@router.put("/public/{bus_id}", response_model=BusResponseSchema)
async def update_public_bus(
        bus_id: str,
        bus_data: BusUpdateSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Update a bus (public endpoint for testing)."""
    try:
        # Initialize repositories and use case
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        result = await manage_use_case.update_bus(
            bus_id=bus_id,
            plate_number=bus_data.plate_number,
            capacity=bus_data.capacity,
            model=bus_data.model,
            year=bus_data.year,
            features=bus_data.features,
            status=bus_data.status
        )
        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus update failed"
        )


@router.delete("/public/{bus_id}")
async def delete_public_bus(
        bus_id: str,
        session: AsyncSession = Depends(get_database_session)
):
    """Delete a bus (public endpoint for testing)."""
    try:
        # Initialize repositories and use case
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        await manage_use_case.delete_bus(bus_id)
        return {"message": "Bus deleted successfully"}

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus deletion failed"
        )


def require_admin(request: Request):
    """Require admin role."""
    if not hasattr(request.state, 'user') or request.state.user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("/", response_model=List[BusResponseSchema])
async def get_buses(
        request: Request,
        company_id: Optional[str] = Query(None),
        available_only: bool = Query(False),
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Get all buses."""
    try:
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        buses = await manage_use_case.get_buses(
            company_id=company_id,
            available_only=available_only
        )
        return buses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve buses"
        )


@router.post("/", response_model=BusResponseSchema)
async def create_bus(
        bus_data: BusCreateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Create a new bus."""
    try:
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        result = await manage_use_case.create_bus(
            company_id=bus_data.company_id,
            plate_number=bus_data.plate_number,
            capacity=bus_data.capacity,
            model=bus_data.model,
            year=bus_data.year,
            features=bus_data.features
        )

        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except EntityAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus creation failed"
        )


@router.put("/{bus_id}", response_model=BusResponseSchema)
async def update_bus(
        bus_id: str,
        bus_data: BusUpdateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Update a bus."""
    try:
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        result = await manage_use_case.update_bus(
            bus_id=bus_id,
            model=bus_data.model,
            year=bus_data.year,
            features=bus_data.features
        )

        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus update failed"
        )


@router.delete("/{bus_id}")
async def delete_bus(
        bus_id: str,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Delete a bus."""
    try:
        bus_repository = BusRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)
        manage_use_case = ManageBusesUseCase(bus_repository, company_repository)

        success = await manage_use_case.delete_bus(bus_id)

        if success:
            return {"message": "Bus deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bus not found"
            )

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bus deletion failed"
        )