"""
Create admin user script.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.infrastructure.database.connection import get_async_session_maker
from app.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from app.domain.entities.user import User
from app.shared.constants import UserRole
from app.core.security import SecurityConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create admin user."""
    try:
        session_maker = get_async_session_maker()

        async with session_maker() as session:
            user_repository = UserRepositoryImpl(session)

            # Check if admin already exists
            from app.domain.value_objects.email import Email
            admin_email = Email("admin@bus.com")
            existing_admin = await user_repository.find_by_email(admin_email)

            if existing_admin:
                logger.info("Admin user already exists!")
                return

            # Create admin user
            password_hash = SecurityConfig.get_password_hash("admin123")

            admin_user = User(
                email="admin@bus.com",
                name="Administrador del Sistema",
                password_hash=password_hash,
                role=UserRole.ADMIN,
                phone="+51999888777",
                is_active=True
            )

            # Verify email (admin doesn't need verification)
            admin_user.verify_email()

            # Save admin user
            await user_repository.save(admin_user)
            await session.commit()

            logger.info("Admin user created successfully!")
            logger.info("Email: admin@bus.com")
            logger.info("Password: admin123")

    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(create_admin_user())