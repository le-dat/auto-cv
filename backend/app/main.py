"""FastAPI application entry point with lifespan management."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.middleware.auth import AuthMiddleware
from app.api.v1.middleware.exception_handler import ExceptionHandlerMiddleware
from app.api.v1.middleware.rate_limit import RateLimitMiddleware
from app.api.v1.router import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global Redis pool reference
redis_pool: redis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — setup on startup, cleanup on shutdown."""
    global redis_pool

    logger.info("Starting CV Optimizer API...")

    # Create Redis connection pool
    try:
        redis_pool = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await redis_pool.ping()
        logger.info(f"Connected to Redis at {settings.redis_url}")
        app.state.redis = redis_pool
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without Redis.")
        redis_pool = None

    yield

    # Cleanup
    if redis_pool:
        await redis_pool.close()
        logger.info("Redis connection closed.")


def create_app() -> FastAPI:
    """Application factory for creating the FastAPI app."""
    app = FastAPI(
        title="CV Optimizer",
        description="AI-powered CV rewriting service that optimizes resumes for job descriptions",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware (order matters — last added = first executed)
    app.add_middleware(ExceptionHandlerMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)

    # Include API routes
    app.include_router(api_router)

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
