"""
FastAPI application initialization.

Main application entry point with lifespan management and middleware.

@spec: specs/002-todo-backend-api/spec.md (FR-001, FR-010, FR-011)
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine
from app.models.task import Task  # Import to register with metadata
from app.api.middleware import RequestLoggingMiddleware
from app.api.security_middleware import SecurityHeadersMiddleware, RequestIDMiddleware
from app.api.exception_handlers import (
    validation_exception_handler,
    database_exception_handler,
    generic_exception_handler
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    Creates database tables on startup.

    @spec: specs/002-todo-backend-api/spec.md (FR-010)
    """
    logger.info("Starting application...")

    # Startup: Create all tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

    yield

    # Shutdown: Dispose engine
    logger.info("Shutting down application...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="A secure, multi-tenant API for task management",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware (order matters - first added is outermost)
if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(RequestIDMiddleware)

# Configure CORS middleware
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    from app.api.rate_limit_middleware import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "TaskFlow Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if not settings.is_production else "disabled",
        "health": "/health/live"
    }

# Include routers

from app.api.v1 import tasks, health, auth
app.include_router(auth.router)
app.include_router(tasks.router, tags=["tasks"])
app.include_router(health.router, tags=["health"])

logger.info(f"Application started in {settings.APP_ENV} mode")
