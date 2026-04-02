"""Authentication middleware."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple auth middleware placeholder.

    TODO: Implement actual authentication (API key, JWT, etc.)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Placeholder: allow all requests through
        # TODO: Add actual auth logic (API key validation, JWT check, etc.)
        response = await call_next(request)
        return response
