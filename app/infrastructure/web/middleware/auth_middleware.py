"""
Authentication middleware for FastAPI.
"""
from typing import Optional, List
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from ....core.security import SecurityConfig
from ....core.exceptions import TokenExpiredException, InsufficientPermissionsException

logger = logging.getLogger(__name__)

# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/routes/search",  # Allow public route search
}

# Endpoints that require authentication but no specific permissions
AUTHENTICATED_ENDPOINTS = {
    "/api/v1/auth/profile",
    "/api/v1/routes",
    "/api/v1/schedules",
    "/api/v1/reservations",
}

# Admin-only endpoints
ADMIN_ENDPOINTS = {
    "/api/v1/users",
    "/api/v1/companies",
    "/api/v1/buses",
    "/api/v1/admin",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication and authorization middleware."""

    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware."""

        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Extract and validate token
        token = self._extract_token(request)
        if not token:
            return self._unauthorized_response()

        try:
            # Verify token and get user data
            user_data = SecurityConfig.verify_token(token)

            # Add user data to request state
            request.state.user = user_data

            # Check permissions for protected endpoints
            if not self._check_permissions(request.url.path, user_data.get("role")):
                return self._forbidden_response()

            response = await call_next(request)
            return response

        except TokenExpiredException:
            return self._unauthorized_response("Token expired")
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            return self._unauthorized_response("Invalid token")

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public."""
        # Exact match
        if path in PUBLIC_ENDPOINTS:
            return True

        # Pattern matching for dynamic routes
        for public_path in PUBLIC_ENDPOINTS:
            if path.startswith(public_path.rstrip("*")):
                return True

        return False

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        if not auth_header.startswith("Bearer "):
            return None

        return auth_header.split(" ")[1]

    def _check_permissions(self, path: str, user_role: Optional[str]) -> bool:
        """Check if user has permission to access endpoint."""
        if not user_role:
            return False

        # Admin can access everything
        if user_role == "admin":
            return True

        # Check admin-only endpoints
        for admin_path in ADMIN_ENDPOINTS:
            if path.startswith(admin_path):
                return False

        # Regular users can access authenticated endpoints
        return True

    def _unauthorized_response(self, detail: str = "Authentication required") -> Response:
        """Return 401 Unauthorized response."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "message": detail,
                    "error_code": "UNAUTHORIZED"
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    def _forbidden_response(self) -> Response:
        """Return 403 Forbidden response."""
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "message": "Insufficient permissions",
                    "error_code": "FORBIDDEN"
                }
            }
        )