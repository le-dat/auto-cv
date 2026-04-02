"""Global exception handler middleware."""

from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import CVOptimizerError


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Catches CVOptimizerError and returns JSON error responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except CVOptimizerError as e:
            return JSONResponse(
                status_code=400,
                content={"error": e.__class__.__name__, "detail": str(e)},
            )
        except Exception:
            # Don't leak internal errors in production
            return JSONResponse(
                status_code=500,
                content={"error": "InternalServerError", "detail": "An unexpected error occurred"},
            )
