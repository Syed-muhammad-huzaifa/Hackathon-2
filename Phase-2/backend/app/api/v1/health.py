"""
Health check endpoint.

Provides application health status and database connectivity check.

@spec: specs/002-todo-backend-api/spec.md (FR-011)
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.dependencies import get_db_session
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    health_status = {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "version": "0.1.0",
        "checks": {}
    }

    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    return health_status


@router.get("/health/ready")
async def readiness_check(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        return {"status": "ready", "message": "Service is ready to accept traffic"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "not_ready", "message": "Service is not ready"}


@router.get("/health/live")
async def liveness_check():
    return {"status": "alive", "message": "Service is running"}
