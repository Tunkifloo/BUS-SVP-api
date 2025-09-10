"""
Web middleware components.
"""

from .middleware.auth_middleware import AuthMiddleware
from .middleware.cors_middleware import setup_cors

__all__ = ["AuthMiddleware", "setup_cors"]