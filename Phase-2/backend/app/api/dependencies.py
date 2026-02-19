"""
Dependency injection functions for FastAPI routes.

Provides database sessions for dependency injection.

@spec: specs/002-todo-backend-api/spec.md (FR-001)
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session for dependency injection.

    Yields:
        AsyncSession: Async SQLAlchemy session (compatible with SQLModel)
    """
    async with async_session_maker() as session:
        yield session
