"""Health check endpoint."""

from fastapi import APIRouter
from services.cache import cache

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check():
    """Health check with system status."""
    return {
        "status": "healthy",
        "cache_size": cache.size,
        "version": "1.0.0"
    }
