"""
Global exception handlers for the application.

Provides consistent error responses and logging for all exceptions.

@spec: specs/002-todo-backend-api/spec.md (FR-009)
"""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error messages.

    Returns 400 Bad Request with field-level error details.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors}
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors with appropriate status codes.

    Returns 500 Internal Server Error for database issues.
    """
    logger.error(f"Database error on {request.url.path}: {str(exc)}", exc_info=True)

    # Check for specific database errors
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "status": "error",
                "code": "INTEGRITY_ERROR",
                "message": "Database constraint violation",
                "details": None
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "DATABASE_ERROR",
            "message": "An error occurred while processing your request",
            "details": None
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Returns 500 Internal Server Error with minimal details for security.
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": None
        }
    )
