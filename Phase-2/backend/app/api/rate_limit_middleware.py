"""
Rate limiting middleware.

Implements simple in-memory rate limiting per user.

@spec: specs/002-todo-backend-api/spec.md (FR-007)
"""
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    Tracks requests per user_id and enforces rate limits.
    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests allowed per minute per user
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

    async def dispatch(self, request: Request, call_next):
        """
        Check rate limit before processing request.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Extract user identifier (from path or use IP as fallback)
        user_id = request.path_params.get("user_id")
        if not user_id:
            user_id = request.client.host if request.client else "unknown"

        # Check rate limit
        current_time = time.time()
        count, window_start = self.request_counts[user_id]

        # Reset window if more than 60 seconds have passed
        if current_time - window_start > 60:
            count = 0
            window_start = current_time

        # Increment count
        count += 1
        self.request_counts[user_id] = (count, window_start)

        # Check if limit exceeded
        if count > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for user {user_id}: {count} requests in window")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                headers={"Retry-After": "60"}
            )

        # Clean up old entries periodically (every 1000 requests)
        if len(self.request_counts) > 1000:
            self._cleanup_old_entries(current_time)

        return await call_next(request)

    def _cleanup_old_entries(self, current_time: float):
        """
        Remove entries older than 2 minutes.

        Args:
            current_time: Current timestamp
        """
        keys_to_remove = [
            key for key, (_, window_start) in self.request_counts.items()
            if current_time - window_start > 120
        ]
        for key in keys_to_remove:
            del self.request_counts[key]

        logger.debug(f"Cleaned up {len(keys_to_remove)} old rate limit entries")
