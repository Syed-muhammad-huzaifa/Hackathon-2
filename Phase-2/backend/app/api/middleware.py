"""
Request logging middleware.

Logs all incoming requests with user context and response details.

@spec: specs/002-todo-backend-api/spec.md (FR-011)
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests with timing and user context.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and log details.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler
        """
        start_time = time.time()

        # Extract user_id from path if present
        user_id = request.path_params.get("user_id", "anonymous")

        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log request details
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"user_id={user_id} - "
                f"status={response.status_code} - "
                f"duration={duration:.3f}s"
            )

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"user_id={user_id} - "
                f"error={str(e)} - "
                f"duration={duration:.3f}s",
                exc_info=True
            )
            raise
