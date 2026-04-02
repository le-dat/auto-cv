"""API v1 router — aggregates all route modules."""

from fastapi import APIRouter

from app.api.v1.routes import admin, health, jobs

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(jobs.router)
api_router.include_router(admin.router)
api_router.include_router(health.router)
