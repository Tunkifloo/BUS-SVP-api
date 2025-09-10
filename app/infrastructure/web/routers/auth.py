"""
Authentication router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database.connection import get_database_session
from ....application.use_cases.auth.login_user import LoginUserUseCase
from ....application.use_cases.auth.register_user import RegisterUserUseCase
from ....infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from ..schemas.auth_schema import LoginSchema, RegisterSchema, TokenResponseSchema
from ..schemas.user_schema import UserResponseSchema
from ....core.exceptions import InvalidCredentialsException, EntityAlreadyExistsException

router = APIRouter(prefix="/auth")
security = HTTPBearer()


@router.post("/login", response_model=TokenResponseSchema)
async def login(
        credentials: LoginSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Authenticate user and return JWT token."""
    try:
        # Initialize use case
        user_repository = UserRepositoryImpl(session)
        login_use_case = LoginUserUseCase(user_repository)

        # Execute login
        result = await login_use_case.execute(
            email=credentials.email,
            password=credentials.password
        )

        return result

    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=TokenResponseSchema)
async def register(
        user_data: RegisterSchema,
        session: AsyncSession = Depends(get_database_session)
):
    """Register new user."""
    try:
        # Initialize use case
        user_repository = UserRepositoryImpl(session)
        register_use_case = RegisterUserUseCase(user_repository)

        # Execute registration
        user_result = await register_use_case.execute(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            phone=user_data.phone
        )

        # Login the new user
        login_use_case = LoginUserUseCase(user_repository)
        login_result = await login_use_case.execute(
            email=user_data.email,
            password=user_data.password
        )

        return login_result

    except EntityAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )