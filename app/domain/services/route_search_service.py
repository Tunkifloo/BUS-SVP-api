"""
Route search domain service.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..entities.route import Route
from ..entities.schedule import Schedule
from ..repositories.route_repository import RouteRepository
from ..repositories.schedule_repository import ScheduleRepository
from ...shared.utils import DateTimeUtils


class RouteSearchService:
    """Domain service for route search operations."""

    def __init__(
        self,
        route_repository: RouteRepository,
        schedule_repository: ScheduleRepository
    ):
        self._route_repository = route_repository
        self._schedule_repository = schedule_repository

    async def search_available_routes(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        date: Optional[str] = None,
        min_seats: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Search for available routes with schedules.

        Args:
            origin: Origin city (optional)
            destination: Destination city (optional)
            date: Travel date (optional)
            min_seats: Minimum available seats required

        Returns:
            List of routes with their available schedules
        """
        # Get routes matching search criteria
        routes = await self._route_repository.search_routes(
            origin=origin,
            destination=destination
        )

        results = []
        for route in routes:
            if not route.can_accept_bookings():
                continue

            # Get schedules for this route
            schedules = await self._schedule_repository.find_available_schedules(
                route_id=route.id,
                date=date
            )

            # Filter schedules with enough seats
            available_schedules = [
                schedule for schedule in schedules
                if schedule.available_seats >= min_seats and schedule.can_accept_reservations()
            ]

            if available_schedules:
                results.append({
                    'route': route,
                    'schedules': available_schedules,
                    'schedule_count': len(available_schedules)
                })

        return results

    async def find_routes_with_schedules(
        self,
        company_id: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find routes with their schedules.

        Args:
            company_id: Filter by company (optional)
            active_only: Only return active routes

        Returns:
            List of routes with schedules
        """
        if company_id:
            routes = await self._route_repository.find_by_company(company_id)
        elif active_only:
            routes = await self._route_repository.find_active()
        else:
            routes = await self._route_repository.find_all()

        results = []
        for route in routes:
            schedules = await self._schedule_repository.find_by_route(route.id)
            results.append({
                'route': route,
                'schedules': schedules,
                'total_schedules': len(schedules),
                'active_schedules': len([s for s in schedules if s.can_accept_reservations()])
            })

        return results

    async def get_popular_destinations(
        self,
        origin: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular destinations.

        Args:
            origin: Filter by origin city (optional)
            limit: Maximum number of results

        Returns:
            List of popular destinations with booking counts
        """
        if origin:
            routes = await self._route_repository.search_routes(origin=origin)
        else:
            routes = await self._route_repository.find_popular_routes(limit=limit)

        destinations = {}
        for route in routes:
            key = route.destination
            if origin and route.origin.lower() != origin.lower():
                continue

            if key not in destinations:
                destinations[key] = {
                    'destination': key,
                    'route_count': 0,
                    'total_bookings': 0,
                    'avg_price': 0.0,
                    'companies': set()
                }

            destinations[key]['route_count'] += 1
            destinations[key]['total_bookings'] += route.total_bookings
            destinations[key]['companies'].add(route.company_id)

        # Calculate average prices and convert sets to counts
        result = []
        for dest_data in destinations.values():
            # Get routes for this destination to calculate average price
            dest_routes = [r for r in routes if r.destination == dest_data['destination']]
            if dest_routes:
                avg_price = sum(r.price.to_float() for r in dest_routes) / len(dest_routes)
                dest_data['avg_price'] = round(avg_price, 2)

            dest_data['company_count'] = len(dest_data['companies'])
            del dest_data['companies']  # Remove set object
            result.append(dest_data)

        # Sort by total bookings
        result.sort(key=lambda x: x['total_bookings'], reverse=True)
        return result[:limit]