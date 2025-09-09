"""
Money value object.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Union
from ..entities.base import ValueObject
from ...core.exceptions import ValidationException


class Money(ValueObject):
    """Money value object with currency support."""

    def __init__(self, amount: Union[float, int, str, Decimal], currency: str = "PEN"):
        """
        Initialize money value object.

        Args:
            amount: Monetary amount
            currency: Currency code (default: PEN for Peruvian Sol)

        Raises:
            ValidationException: If amount is invalid
        """
        try:
            self._amount = Decimal(str(amount)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
        except (ValueError, TypeError) as e:
            raise ValidationException("amount", amount, f"Invalid amount: {str(e)}")

        if self._amount < 0:
            raise ValidationException("amount", amount, "Amount cannot be negative")

        self._currency = currency.upper()

    @property
    def amount(self) -> Decimal:
        """Get amount as Decimal."""
        return self._amount

    @property
    def currency(self) -> str:
        """Get currency code."""
        return self._currency

    def to_float(self) -> float:
        """Convert amount to float."""
        return float(self._amount)

    def to_string(self, include_currency: bool = True) -> str:
        """Convert to formatted string."""
        if include_currency:
            return f"{self._currency} {self._amount:.2f}"
        return f"{self._amount:.2f}"

    def add(self, other: 'Money') -> 'Money':
        """Add two money values."""
        self._validate_same_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money values."""
        self._validate_same_currency(other)
        result_amount = self._amount - other._amount

        if result_amount < 0:
            raise ValidationException(
                "amount",
                result_amount,
                "Result cannot be negative"
            )

        return Money(result_amount, self._currency)

    def multiply(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiply money by a factor."""
        if factor < 0:
            raise ValidationException("factor", factor, "Factor cannot be negative")

        result_amount = self._amount * Decimal(str(factor))
        return Money(result_amount, self._currency)

    def divide(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Divide money by a divisor."""
        if divisor <= 0:
            raise ValidationException("divisor", divisor, "Divisor must be positive")

        result_amount = self._amount / Decimal(str(divisor))
        return Money(result_amount, self._currency)

    def percentage(self, percent: Union[int, float, Decimal]) -> 'Money':
        """Calculate percentage of money value."""
        if percent < 0:
            raise ValidationException("percent", percent, "Percentage cannot be negative")

        factor = Decimal(str(percent)) / Decimal('100')
        return self.multiply(factor)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self._amount == 0

    def is_greater_than(self, other: 'Money') -> bool:
        """Check if this money is greater than other."""
        self._validate_same_currency(other)
        return self._amount > other._amount

    def is_less_than(self, other: 'Money') -> bool:
        """Check if this money is less than other."""
        self._validate_same_currency(other)
        return self._amount < other._amount

    def is_equal_to(self, other: 'Money') -> bool:
        """Check if this money equals other."""
        return (self._currency == other._currency and
                self._amount == other._amount)

    def _validate_same_currency(self, other: 'Money') -> None:
        """Validate that both money objects have the same currency."""
        if self._currency != other._currency:
            raise ValidationException(
                "currency",
                other._currency,
                f"Currency mismatch: {self._currency} vs {other._currency}"
            )

    def __str__(self) -> str:
        """String representation."""
        return self.to_string()

    def __add__(self, other: 'Money') -> 'Money':
        """Addition operator."""
        return self.add(other)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtraction operator."""
        return self.subtract(other)

    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiplication operator."""
        return self.multiply(factor)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """Division operator."""
        return self.divide(divisor)

    def __gt__(self, other: 'Money') -> bool:
        """Greater than operator."""
        return self.is_greater_than(other)

    def __lt__(self, other: 'Money') -> bool:
        """Less than operator."""
        return self.is_less_than(other)

    def __eq__(self, other: object) -> bool:
        """Equality operator."""
        if not isinstance(other, Money):
            return False
        return self.is_equal_to(other)

    @classmethod
    def zero(cls, currency: str = "PEN") -> 'Money':
        """Create zero money value."""
        return cls(0, currency)

    @classmethod
    def from_cents(cls, cents: int, currency: str = "PEN") -> 'Money':
        """Create money from cents."""
        amount = Decimal(cents) / Decimal('100')
        return cls(amount, currency)