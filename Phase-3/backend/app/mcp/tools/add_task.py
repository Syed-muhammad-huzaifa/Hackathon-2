"""
MCP tool: add_task — create a new task for the authenticated user.
@spec: specs/001-chatbot-backend/contracts/mcp-tools.yaml
"""
import json
import logging
from typing import Optional

from app.core.database import async_session_factory
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


async def add_task_impl(user_id: str, title: str, description: Optional[str] = None) -> str:
    """
    Create a new task for the user.

    Args:
        user_id: The authenticated user's ID (from JWT).
        title: Task title (required, 1-200 chars).
        description: Optional task description.

    Returns:
        JSON with task_id, status, and title.
    """
    if not title or not title.strip():
        return json.dumps({"error": "Title cannot be empty", "code": "VALIDATION_ERROR"})

    try:
        async with async_session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.create(user_id, title.strip(), description)
            logger.info(f"[MCP:add_task] Created task {task.id} for user {user_id}")
            return json.dumps({
                "task_id": str(task.id),
                "status": "created",
                "title": task.title,
            })
    except Exception as e:
        logger.error(f"[MCP:add_task] Error: {e}")
        return json.dumps({"error": "Failed to create task", "code": "DATABASE_ERROR"})


