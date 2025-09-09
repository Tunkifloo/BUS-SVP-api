"""
Value objects for the domain layer.
"""
from .email import Email
from .money import Money
from .seat_number import SeatNumber

__all__ = ['Email', 'Money', 'SeatNumber']