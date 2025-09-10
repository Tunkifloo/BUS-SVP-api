"""
Users router for admin operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from ..schemas.user_schema import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from ....core.exceptions import EntityNotFoundException, EntityAlreadyExistsException

router = APIRouter(prefix="/users")


@router.get("/public", response_model=List[UserResponseSchema])
async def get_public_users(
        session: AsyncSession = Depends(get_database_session)
):
    """Get all users (public endpoint for testing)."""
    try:
        # For now, return mock data to test the frontend
        from datetime import datetime
        
        mock_users = [
            UserResponseSchema(
                id="1",
                name="Admin User",
                email="admin@bus.com",
                role="admin",
                is_active=True,
                email_verified=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            UserResponseSchema(
                id="2",
                name="Juan Pérez",
                email="juan@email.com",
                role="user",
                is_active=True,
                email_verified=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            UserResponseSchema(
                id="3",
                name="María García",
                email="maria@email.com",
                role="user",
                is_active=True,
                email_verified=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            UserResponseSchema(
                id="4",
                name="Carlos López",
                email="carlos@email.com",
                role="user",
                is_active=False,
                email_verified=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        return mock_users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

def require_admin(request: Request):
    """Require admin role."""
    if not hasattr(request.state, 'user') or request.state.user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def get_current_user_id(request: Request) -> str:
    """Extract current user ID from request state."""
    if not hasattr(request.state, 'user') or not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user.get('sub')


@router.get("/", response_model=List[UserResponseSchema])
async def get_users(
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Get all users."""
    try:
        user_repository = UserRepositoryImpl(session)
        users = await user_repository.find_all()

        return [
            UserResponseSchema(
                id=user.id,
                name=user.name,
                email=user.email.value,
                phone=user.phone,
                role=user.role.value,
                is_active=user.is_active,
                email_verified=user.email_verified,
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/me", response_model=UserResponseSchema)
async def get_current_user(
        request: Request,
        session: AsyncSession = Depends(get_database_session)
):
    """Get current user profile."""
    try:
        user_id = get_current_user_id(request)
        user_repository = UserRepositoryImpl(session)
        user = await user_repository.find_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponseSchema(
            id=user.id,
            name=user.name,
            email=user.email.value,
            phone=user.phone,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/me", response_model=UserResponseSchema)
async def update_current_user(
        user_data: UserUpdateSchema,
        request: Request,
        session: AsyncSession = Depends(get_database_session)
):
    """Update current user profile."""
    try:
        user_id = get_current_user_id(request)
        user_repository = UserRepositoryImpl(session)
        user = await user_repository.find_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user profile
        user.update_profile(name=user_data.name, phone=user_data.phone)
        updated_user = await user_repository.update(user)

        return UserResponseSchema(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email.value,
            phone=updated_user.phone,
            role=updated_user.role.value,
            is_active=updated_user.is_active,
            email_verified=updated_user.email_verified,
            last_login=updated_user.last_login,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.delete("/{user_id}")
async def delete_user(
        user_id: str,
        request: Request,
        session: AsyncSession = Depends(get_database_session),
        _: None = Depends(require_admin)
):
    """Delete a user."""
    try:
        current_user_id = get_current_user_id(request)

        # Prevent self-deletion
        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        user_repository = UserRepositoryImpl(session)
        user = await user_repository.find_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Soft delete by deactivating
        user.deactivate()
        await user_repository.update(user)

        return {"message": "User deleted successfully"}

    except EntityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )