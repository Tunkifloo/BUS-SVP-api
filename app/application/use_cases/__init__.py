"""
Application use cases.
"""
# Import all use cases to make them available
from .auth.login_user import LoginUserUseCase
from .auth.register_user import RegisterUserUseCase
from .routes.search_routes import SearchRoutesUseCase
from .routes.create_route import CreateRouteUseCase
from .routes.update_route import UpdateRouteUseCase
from .reservations.create_reservation import CreateReservationUseCase
from .reservations.cancel_reservation import CancelReservationUseCase
from .reservations.get_user_reservations import GetUserReservationsUseCase
from .admin.manage_companies import ManageCompaniesUseCase
from .admin.manage_buses import ManageBusesUseCase
from .admin.manage_schedules import ManageSchedulesUseCase

__all__ = [
    # Auth use cases
    'LoginUserUseCase',
    'RegisterUserUseCase',

    # Route use cases
    'SearchRoutesUseCase',
    'CreateRouteUseCase',
    'UpdateRouteUseCase',

    # Reservation use cases
    'CreateReservationUseCase',
    'CancelReservationUseCase',
    'GetUserReservationsUseCase',

    # Admin use cases
    'ManageCompaniesUseCase',
    'ManageBusesUseCase',
    'ManageSchedulesUseCase'
]