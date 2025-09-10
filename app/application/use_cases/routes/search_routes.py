"""
Search routes use case.
"""
from typing import List, Optional, Dict, Any
from app.domain.services.route_search_service import RouteSearchService
from app.domain.repositories.company_repository import CompanyRepository
from app.shared.decorators import log_execution, cache_result


class SearchRoutesUseCase:
    """Use case for searching available routes."""

    def __init__(
            self,
            route_search_service: RouteSearchService,
            company_repository: CompanyRepository
    ):
        self._route_search_service = route_search_service
        self._company_repository = company_repository

    @log_execution(log_duration=True)
    @cache_result(ttl=300, key_prefix="route_search")  # Cache for 5 minutes
    async def execute(
            self,
            origin: Optional[str] = None,
            destination: Optional[str] = None,
            date: Optional[str] = None,
            min_seats: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Execute route search use case.

        Args:
            origin: Origin city (optional)
            destination: Destination city (optional)
            date: Travel date (optional)
            min_seats: Minimum available seats

        Returns:
            List of available routes with schedules and company info
        """
        # Search available routes
        route_results = await self._route_search_service.search_available_routes(
            origin=origin,
            destination=destination,
            date=date,
            min_seats=min_seats
        )

        # Enrich with company information
        enriched_results = []
        for result in route_results:
            route = result['route']
            schedules = result['schedules']

            # Get company info
            company = await self._company_repository.find_by_id(route.company_id)

            enriched_result = {
                'route': {
                    'id': route.id,
                    'origin': route.origin,
                    'destination': route.destination,
                    'price': route.price.to_float(),
                    'duration': route.duration,
                    'distance_km': route.distance_km,
                    'description': route.description,
                    'total_bookings': route.total_bookings,
                    'popularity_score': route.popularity_score
                },
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'phone': company.phone,
                    'email': company.email.value,
                    'rating': company.rating
                } if company else None,
                'schedules': [
                    {
                        'id': schedule.id,
                        'departure_time': schedule.departure_time,
                        'arrival_time': schedule.arrival_time,
                        'date': schedule.date,
                        'available_seats': schedule.available_seats,
                        'total_capacity': schedule.total_capacity,
                        'bus_id': schedule.bus_id,
                        'status': schedule.status.value,
                        'can_book': schedule.can_accept_reservations()
                    }
                    for schedule in schedules
                ],
                'schedule_count': len(schedules)
            }

            enriched_results.append(enriched_result)

        return enriched_results