"""Rate limiting middleware."""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware placeholder.

    TODO: Implement actual rate limiting using Redis.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Placeholder: allow all requests through
        # TODO: Implement rate limiting using Redis
        # - Track requests per client IP/API key
        # - Return 429 if limit exceeded
        response = await call_next(request)
        return response
