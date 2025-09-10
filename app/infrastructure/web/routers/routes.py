"""
Routes router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.routes.search_routes import SearchRoutesUseCase
from ....application.use_cases.routes.create_route import CreateRouteUseCase
from ....application.use_cases.routes.update_route import UpdateRouteUseCase
from ....infrastructure.database.repositories.route_repository_impl import RouteRepositoryImpl
from ....infrastructure.database.repositories.company_repository_impl import CompanyRepositoryImpl
from ....infrastructure.database.repositories.schedule_repository_impl import ScheduleRepositoryImpl
from ....domain.services.route_search_service import RouteSearchService
from ..schemas.route_schema import (
    RouteCreateSchema, RouteUpdateSchema, RouteResponseSchema,
    RouteSearchSchema, RouteWithSchedulesSchema
)
from ....core.exceptions import EntityNotFoundException, ValidationException

router = APIRouter(prefix="/routes")


@router.get("/search", response_model=List[RouteWithSchedulesSchema])
async def search_routes(
        origin: Optional[str] = Query(None, description="Origin city"),
        destination: Optional[str] = Query(None, description="Destination city"),
        date: Optional[str] = Query(None, description="Travel date (YYYY-MM-DD)"),
        min_seats: int = Query(1, ge=1, description="Minimum available seats"),
        session: AsyncSession = Depends(get_database_session)
):
    """Search available routes with schedules."""
    try:
        # Initialize repositories and services
        route_repository = RouteRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)

        route_search_service = RouteSearchService(route_repository, schedule_repository)
        search_use_case = SearchRoutesUseCase(route_search_service, company_repository)

        # Execute search
        results = await search_use_case.execute(
            origin=origin,
            destination=destination,
            date=date,
            min_seats=min_seats
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.post("/", response_model=RouteResponseSchema)
async def create_route(
        route_data: RouteCreateSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Create a new route."""
    try:
        # Initialize repositories and use case
        route_repository = RouteRepositoryImpl(session)
        company_repository = CompanyRepositoryImpl(session)

        create_use_case = CreateRouteUseCase(route_repository, company_repository)

        # Execute creation
        result = await create_use_case.execute(
            company_id=route_data.company_id,
            origin=route_data.origin,
            destination=route_data.destination,
            price=route_data.price,
            duration=route_data.duration,
            distance_km=route_data.distance_km,
            description=route_data.description
        )

        return result

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Route creation failed"
        )


@router.put("/{route_id}", response_model=RouteResponseSchema)
async def update_route(
        route_id: str,
        route_data: RouteUpdateSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Update a route."""
    try:
        # Initialize repository and use case
        route_repository = RouteRepositoryImpl(session)
        update_use_case = UpdateRouteUseCase(route_repository)

        # Execute update
        result = await update_use_case.execute(
            route_id=route_id,
            price=route_data.price,
            duration=route_data.duration,
            distance_km=route_data.distance_km,
            description=route_data.description
        )

        return result

    except EntityNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Route update failed"
        )
