#!/usr/bin/env python3
"""
Script to create test data for the bus system.
"""
import asyncio
import sys
import os
from datetime import datetime, date, time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.infrastructure.database.connection import get_database_engine, get_async_session_maker
from app.infrastructure.database.models.company_model import CompanyModel
from app.infrastructure.database.models.bus_model import BusModel
from app.infrastructure.database.models.route_model import RouteModel
from app.infrastructure.database.models.schedule_model import ScheduleModel


async def create_test_data():
    """Create test data for the system."""
    engine = get_database_engine()
    session_maker = get_async_session_maker()
    
    async with session_maker() as session:
        try:
            # Create test companies
            companies = [
                CompanyModel(
                    id="company-1",
                    name="TransAndina",
                    email="info@transandina.com",
                    phone="+51 999 888 777",
                    address="Av. Javier Prado 123, Lima",
                    description="Empresa líder en transporte interprovincial",
                    status="active",
                    rating=4.5,
                    total_trips=500
                ),
                CompanyModel(
                    id="company-2",
                    name="Cruz del Sur",
                    email="info@cruzdelsur.com",
                    phone="+51 999 777 666",
                    address="Av. Grau 456, Lima",
                    description="Transporte de lujo y confort",
                    status="active",
                    rating=4.8,
                    total_trips=750
                )
            ]
            
            for company in companies:
                session.add(company)
            
            # Create test buses
            buses = [
                BusModel(
                    id="bus-1",
                    company_id="company-1",
                    plate_number="ABC-123",
                    capacity=40,
                    model="Mercedes Benz",
                    year=2020,
                    status="active",
                    features=["Aire acondicionado", "WiFi", "Asientos reclinables"],
                    mileage=50000,
                    last_maintenance_date="2024-01-15",
                    next_maintenance_due="2024-07-15"
                ),
                BusModel(
                    id="bus-2",
                    company_id="company-1",
                    plate_number="DEF-456",
                    capacity=35,
                    model="Volvo",
                    year=2021,
                    status="active",
                    features=["Aire acondicionado", "WiFi"],
                    mileage=30000,
                    last_maintenance_date="2024-02-10",
                    next_maintenance_due="2024-08-10"
                ),
                BusModel(
                    id="bus-3",
                    company_id="company-2",
                    plate_number="GHI-789",
                    capacity=45,
                    model="Scania",
                    year=2022,
                    status="active",
                    features=["Aire acondicionado", "WiFi", "Asientos reclinables", "TV"],
                    mileage=20000,
                    last_maintenance_date="2024-03-05",
                    next_maintenance_due="2024-09-05"
                )
            ]
            
            for bus in buses:
                session.add(bus)
            
            # Create test routes
            routes = [
                RouteModel(
                    id="route-1",
                    company_id="company-1",
                    origin="Lima",
                    destination="Cusco",
                    price=80.0,
                    duration="22h",
                    status="active",
                    distance_km=1100,
                    description="Viaje directo Lima - Cusco",
                    total_bookings=150,
                    popularity_score=4.5
                ),
                RouteModel(
                    id="route-2",
                    company_id="company-1",
                    origin="Lima",
                    destination="Arequipa",
                    price=60.0,
                    duration="16h",
                    status="active",
                    distance_km=1000,
                    description="Viaje directo Lima - Arequipa",
                    total_bookings=200,
                    popularity_score=4.3
                ),
                RouteModel(
                    id="route-3",
                    company_id="company-2",
                    origin="Lima",
                    destination="Trujillo",
                    price=45.0,
                    duration="8h",
                    status="active",
                    distance_km=560,
                    description="Viaje directo Lima - Trujillo",
                    total_bookings=300,
                    popularity_score=4.1
                )
            ]
            
            for route in routes:
                session.add(route)
            
            # Create test schedules
            schedules = [
                ScheduleModel(
                    id="schedule-1",
                    route_id="route-1",
                    bus_id="bus-1",
                    departure_time="20:00",
                    arrival_time="18:00",
                    date="2024-12-15",
                    available_seats=40,
                    total_capacity=40,
                    status="active",
                    occupied_seats=0,
                    reserved_seats=0
                ),
                ScheduleModel(
                    id="schedule-2",
                    route_id="route-2",
                    bus_id="bus-2",
                    departure_time="22:00",
                    arrival_time="14:00",
                    date="2024-12-16",
                    available_seats=35,
                    total_capacity=35,
                    status="active",
                    occupied_seats=0,
                    reserved_seats=0
                ),
                ScheduleModel(
                    id="schedule-3",
                    route_id="route-3",
                    bus_id="bus-3",
                    departure_time="08:00",
                    arrival_time="16:00",
                    date="2024-12-17",
                    available_seats=45,
                    total_capacity=45,
                    status="active",
                    occupied_seats=0,
                    reserved_seats=0
                )
            ]
            
            for schedule in schedules:
                session.add(schedule)
            
            await session.commit()
            print("✅ Test data created successfully!")
            print("📊 Created:")
            print("   - 2 companies")
            print("   - 3 buses")
            print("   - 3 routes")
            print("   - 3 schedules")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating test data: {e}")
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(create_test_data())
