"""
Schedules router for admin operations.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.admin.manage_schedules import ManageSchedulesUseCase
from ....infrastructure.database.repositories.schedule_repository_impl import ScheduleRepositoryImpl
from ....infrastructure.database.repositories.route_repository_impl import RouteRepositoryImpl
from ....infrastructure.database.repositories.bus_repository_impl import BusRepositoryImpl
from ..schemas.schedule_schema import ScheduleCreateSchema, ScheduleUpdateSchema, ScheduleResponseSchema
from ....core.exceptions import EntityNotFoundException, ScheduleConflictException

router = APIRouter(prefix="/schedules")


def require_admin(request: Request):
    """Require admin role."""
    if not hasattr(request.state, 'user') or request.state.user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("/", response_model=List[ScheduleResponseSchema])
async def get_schedules(
        request: Request,
        route_id: Optional[str] = Query(None),
        bus_id: Optional[str] = Query(None),
        date: Optional[str] = Query(None),
        available_only: bool = Query(False),
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Get all schedules."""
    try:
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        bus_repository = BusRepositoryImpl(session)

        manage_use_case = ManageSchedulesUseCase(
            schedule_repository, route_repository, bus_repository
        )

        schedules = await manage_use_case.get_schedules(
            route_id=route_id,
            bus_id=bus_id,
            date=date,
            available_only=available_only
        )
        return schedules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schedules"
        )


@router.post("/", response_model=ScheduleResponseSchema)
async def create_schedule(
        schedule_data: ScheduleCreateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Create a new schedule."""
    try:
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        bus_repository = BusRepositoryImpl(session)

        manage_use_case = ManageSchedulesUseCase(
            schedule_repository, route_repository, bus_repository
        )

        result = await manage_use_case.create_schedule(
            route_id=schedule_data.route_id,
            bus_id=schedule_data.bus_id,
            departure_time=schedule_data.departure_time,
            arrival_time=schedule_data.arrival_time,
            date=schedule_data.date,
            available_seats=schedule_data.available_seats
        )

        return result

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ScheduleConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schedule creation failed"
        )


@router.put("/{schedule_id}", response_model=ScheduleResponseSchema)
async def update_schedule(
        schedule_id: str,
        schedule_data: ScheduleUpdateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Update a schedule."""
    try:
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        bus_repository = BusRepositoryImpl(session)

        manage_use_case = ManageSchedulesUseCase(
            schedule_repository, route_repository, bus_repository
        )

        result = await manage_use_case.update_schedule(
            schedule_id=schedule_id,
            departure_time=schedule_data.departure_time,
            arrival_time=schedule_data.arrival_time
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
            detail="Schedule update failed"
        )


@router.delete("/{schedule_id}")
async def delete_schedule(
        schedule_id: str,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Delete a schedule."""
    try:
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        bus_repository = BusRepositoryImpl(session)

        manage_use_case = ManageSchedulesUseCase(
            schedule_repository, route_repository, bus_repository
        )

        success = await manage_use_case.delete_schedule(schedule_id)

        if success:
            return {"message": "Schedule deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Schedule deletion failed"
        )