"""
Pricing domain service.
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from ..entities.route import Route
from ..value_objects.money import Money
from ...shared.utils import BusinessUtils


class PricingService:
    """Domain service for pricing calculations."""

    def calculate_total_price(
            self,
            base_price: Money,
            include_booking_fee: bool = True,
            discount_percentage: float = 0.0,
            additional_fees: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate total price with all fees and discounts.

        Args:
            base_price: Base route price
            include_booking_fee: Whether to include booking fee
            discount_percentage: Discount percentage (0-100)
            additional_fees: Additional fees dictionary

        Returns:
            Price breakdown dictionary
        """
        breakdown = {
            'base_price': base_price.to_float(),
            'booking_fee': 0.0,
            'additional_fees': {},
            'discount_amount': 0.0,
            'total_before_discount': 0.0,
            'total_price': 0.0
        }

        total = base_price

        # Add booking fee
        if include_booking_fee:
            booking_fee = BusinessUtils.calculate_booking_fee(base_price.to_float())
            breakdown['booking_fee'] = booking_fee
            total = total.add(Money(booking_fee))

        # Add additional fees
        if additional_fees:
            for fee_name, fee_amount in additional_fees.items():
                breakdown['additional_fees'][fee_name] = fee_amount
                total = total.add(Money(fee_amount))

        breakdown['total_before_discount'] = total.to_float()

        # Apply discount
        if discount_percentage > 0:
            discount_amount = total.percentage(discount_percentage)
            breakdown['discount_amount'] = discount_amount.to_float()
            total = total.subtract(discount_amount)

        breakdown['total_price'] = total.to_float()

        return breakdown

    def calculate_refund_amount(
            self,
            original_price: Money,
            cancellation_fee_percentage: float = 10.0,
            processing_fee: float = 5.0
    ) -> Dict[str, Any]:
        """
        Calculate refund amount for cancellation.

        Args:
            original_price: Original reservation price
            cancellation_fee_percentage: Cancellation fee percentage
            processing_fee: Fixed processing fee

        Returns:
            Refund breakdown dictionary
        """
        breakdown = {
            'original_price': original_price.to_float(),
            'cancellation_fee': 0.0,
            'processing_fee': processing_fee,
            'refund_amount': 0.0
        }

        # Calculate cancellation fee
        cancellation_fee = original_price.percentage(cancellation_fee_percentage)
        breakdown['cancellation_fee'] = cancellation_fee.to_float()

        # Calculate refund
        total_deductions = cancellation_fee.add(Money(processing_fee))

        if original_price.is_greater_than(total_deductions):
            refund = original_price.subtract(total_deductions)
            breakdown['refund_amount'] = refund.to_float()
        else:
            breakdown['refund_amount'] = 0.0

        return breakdown

    def calculate_dynamic_pricing(
            self,
            base_price: Money,
            occupancy_rate: float,
            days_until_departure: int,
            is_peak_time: bool = False,
            route_popularity: float = 0.0
    ) -> Money:
        """
        Calculate dynamic pricing based on demand factors.

        Args:
            base_price: Base route price
            occupancy_rate: Current occupancy rate (0-1)
            days_until_departure: Days until departure
            is_peak_time: Whether it's peak travel time
            route_popularity: Route popularity score (0-5)

        Returns:
            Adjusted price
        """
        multiplier = Decimal('1.0')

        # Occupancy-based pricing
        if occupancy_rate > 0.8:
            multiplier += Decimal('0.2')  # 20% increase for high occupancy
        elif occupancy_rate > 0.6:
            multiplier += Decimal('0.1')  # 10% increase for medium occupancy

        # Time-based pricing
        if days_until_departure <= 3:
            multiplier += Decimal('0.15')  # 15% increase for last-minute bookings
        elif days_until_departure <= 7:
            multiplier += Decimal('0.05')  # 5% increase for short notice

        # Peak time pricing
        if is_peak_time:
            multiplier += Decimal('0.25')  # 25% increase for peak times

        # Popularity-based pricing
        if route_popularity > 4.0:
            multiplier += Decimal('0.1')  # 10% increase for very popular routes
        elif route_popularity > 3.0:
            multiplier += Decimal('0.05')  # 5% increase for popular routes

        # Apply multiplier with reasonable bounds
        multiplier = max(Decimal('0.8'), min(multiplier, Decimal('2.0')))

        return base_price.multiply(float(multiplier))

    def calculate_group_discount(
            self,
            base_price: Money,
            passenger_count: int
    ) -> Dict[str, Any]:
        """
        Calculate group discount for multiple passengers.

        Args:
            base_price: Base price per passenger
            passenger_count: Number of passengers

        Returns:
            Group pricing breakdown
        """
        breakdown = {
            'passenger_count': passenger_count,
            'base_price_per_passenger': base_price.to_float(),
            'total_base_price': base_price.multiply(passenger_count).to_float(),
            'discount_percentage': 0.0,
            'discount_amount': 0.0,
            'final_total': 0.0
        }

        # Group discount tiers
        discount_percentage = 0.0
        if passenger_count >= 10:
            discount_percentage = 15.0  # 15% for 10+ passengers
        elif passenger_count >= 5:
            discount_percentage = 10.0  # 10% for 5+ passengers
        elif passenger_count >= 3:
            discount_percentage = 5.0  # 5% for 3+ passengers

        total_price = base_price.multiply(passenger_count)

        if discount_percentage > 0:
            discount_amount = total_price.percentage(discount_percentage)
            final_total = total_price.subtract(discount_amount)

            breakdown['discount_percentage'] = discount_percentage
            breakdown['discount_amount'] = discount_amount.to_float()
            breakdown['final_total'] = final_total.to_float()
        else:
            breakdown['final_total'] = total_price.to_float()

        return breakdown