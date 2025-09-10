"""
Web schemas for FastAPI.
"""
from .base_schema import BaseSchema, BaseResponseSchema, PaginatedResponseSchema
from .user_schema import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from .auth_schema import LoginSchema, RegisterSchema, TokenResponseSchema
from .company_schema import CompanyCreateSchema, CompanyUpdateSchema, CompanyResponseSchema
from .bus_schema import BusCreateSchema, BusUpdateSchema, BusResponseSchema
from .route_schema import RouteCreateSchema, RouteUpdateSchema, RouteResponseSchema, RouteSearchSchema
from .schedule_schema import ScheduleCreateSchema, ScheduleUpdateSchema, ScheduleResponseSchema
from .reservation_schema import ReservationCreateSchema, ReservationResponseSchema, ReservationCancelSchema
from .response_schema import ApiResponseSchema, HealthResponseSchema

__all__ = [
    'BaseSchema', 'BaseResponseSchema', 'PaginatedResponseSchema',
    'UserCreateSchema', 'UserUpdateSchema', 'UserResponseSchema',
    'LoginSchema', 'RegisterSchema', 'TokenResponseSchema',
    'CompanyCreateSchema', 'CompanyUpdateSchema', 'CompanyResponseSchema',
    'BusCreateSchema', 'BusUpdateSchema', 'BusResponseSchema',
    'RouteCreateSchema', 'RouteUpdateSchema', 'RouteResponseSchema', 'RouteSearchSchema',
    'ScheduleCreateSchema', 'ScheduleUpdateSchema', 'ScheduleResponseSchema',
    'ReservationCreateSchema', 'ReservationResponseSchema', 'ReservationCancelSchema',
    'ApiResponseSchema', 'HealthResponseSchema'
]