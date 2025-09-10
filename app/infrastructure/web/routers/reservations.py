"""
Reservations router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.reservations.create_reservation import CreateReservationUseCase
from ....application.use_cases.reservations.cancel_reservation import CancelReservationUseCase
from ....application.use_cases.reservations.get_user_reservations import GetUserReservationsUseCase
from ....infrastructure.database.repositories.reservation_repository_impl import ReservationRepositoryImpl
from ....infrastructure.database.repositories.schedule_repository_impl import ScheduleRepositoryImpl
from ....infrastructure.database.repositories.route_repository_impl import RouteRepositoryImpl
from ....infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from ....domain.services.reservation_service import ReservationService
from ....domain.services.seat_allocation_service import SeatAllocationService
from ..schemas.reservation_schema import (
    ReservationCreateSchema, ReservationResponseSchema, ReservationCancelSchema,
    ReservationWithDetailsSchema
)
from ....core.exceptions import EntityNotFoundException, SeatNotAvailableException

router = APIRouter(prefix="/reservations")


@router.post("/public", response_model=ReservationResponseSchema)
async def create_public_reservation(
        reservation_data: ReservationCreateSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Create a reservation (public endpoint for testing)."""
    try:
        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        user_repository = UserRepositoryImpl(session)
        
        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, 
            schedule_repository, 
            route_repository, 
            seat_allocation_service
        )
        
        create_use_case = CreateReservationUseCase(reservation_service, user_repository)
        
        # Execute creation
        result = await create_use_case.execute(
            user_id=reservation_data.user_id,
            schedule_id=reservation_data.schedule_id,
            seat_number=reservation_data.seat_number
        )
        
        return result
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except SeatNotAvailableException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Seat {e.seat_number} is not available"
        )
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reservation creation failed"
        )


@router.get("/public/user/{user_id}", response_model=List[ReservationWithDetailsSchema])
async def get_public_user_reservations(
        user_id: str,
        session: AsyncSession = Depends(get_database_session)
):
    """Get user reservations (public endpoint for testing)."""
    try:
        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        
        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, 
            schedule_repository, 
            route_repository, 
            seat_allocation_service
        )
        
        # Get user reservations with details
        reservations = await reservation_service.get_user_reservations_with_details(user_id)
        
        return reservations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user reservations"
        )


@router.delete("/public/{reservation_id}", response_model=ReservationResponseSchema)
async def cancel_public_reservation(
        reservation_id: str,
        session: AsyncSession = Depends(get_database_session)
):
    """Cancel a reservation (public endpoint for testing)."""
    try:
        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        
        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, 
            schedule_repository, 
            route_repository, 
            seat_allocation_service
        )
        
        # Cancel reservation
        result = await reservation_service.cancel_reservation(reservation_id)
        
        return {
            "id": result.id,
            "user_id": result.user_id,
            "schedule_id": result.schedule_id,
            "seat_number": result.seat_number.number,
            "price": result.price.to_float(),
            "status": result.status.value,
            "reservation_code": result.reservation_code,
            "cancelled_at": result.cancelled_at.isoformat() if result.cancelled_at else None,
            "cancellation_reason": result.cancellation_reason,
            "created_at": result.created_at.isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reservation cancellation failed"
        )


def get_current_user_id(request: Request) -> str:
    """Extract current user ID from request state."""
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user.get('sub')


@router.post("/", response_model=ReservationResponseSchema)
async def create_reservation(
        reservation_data: ReservationCreateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session)
):
    """Create a new reservation."""
    try:
        user_id = get_current_user_id(request)

        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        user_repository = UserRepositoryImpl(session)

        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, schedule_repository, route_repository, seat_allocation_service
        )

        create_use_case = CreateReservationUseCase(reservation_service, user_repository)

        # Execute creation
        result = await create_use_case.execute(
            user_id=user_id,
            schedule_id=reservation_data.schedule_id,
            seat_number=reservation_data.seat_number
        )

        return result

    except SeatNotAvailableException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Seat {e.details.get('seat_number')} is not available"
        )
    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reservation creation failed"
        )


@router.get("/my", response_model=List[ReservationWithDetailsSchema])
async def get_my_reservations(
        request: Request,
        session: AsyncSession = Depends(get_database_session)
):
    """Get current user's reservations."""
    try:
        user_id = get_current_user_id(request)

        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)
        user_repository = UserRepositoryImpl(session)

        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, schedule_repository, route_repository, seat_allocation_service
        )

        get_reservations_use_case = GetUserReservationsUseCase(reservation_service, user_repository)

        # Execute query
        results = await get_reservations_use_case.execute(user_id=user_id)

        return results

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reservations"
        )


@router.delete("/{reservation_id}", response_model=ReservationResponseSchema)
async def cancel_reservation(
        reservation_id: str,
        cancel_data: ReservationCancelSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session)
):
    """Cancel a reservation."""
    try:
        user_id = get_current_user_id(request)

        # Initialize repositories and services
        reservation_repository = ReservationRepositoryImpl(session)
        schedule_repository = ScheduleRepositoryImpl(session)
        route_repository = RouteRepositoryImpl(session)

        seat_allocation_service = SeatAllocationService(schedule_repository, reservation_repository)
        reservation_service = ReservationService(
            reservation_repository, schedule_repository, route_repository, seat_allocation_service
        )

        cancel_use_case = CancelReservationUseCase(reservation_service)

        # Verify reservation belongs to user (additional security check)
        reservation = await reservation_repository.find_by_id(reservation_id)
        if not reservation or reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )

        # Execute cancellation
        result = await cancel_use_case.execute(
            reservation_id=reservation_id,
            reason=cancel_data.reason
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
            detail="Reservation cancellation failed"
        )