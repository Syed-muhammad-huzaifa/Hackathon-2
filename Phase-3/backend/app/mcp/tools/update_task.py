"""
MCP tool: update_task — modify task title or description.
@spec: specs/001-chatbot-backend/contracts/mcp-tools.yaml
"""
import json
import logging
from typing import Optional
from uuid import UUID

from app.core.database import async_session_factory
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


async def update_task_impl(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Modify a task's title or description.

    Args:
        user_id: The authenticated user's ID (from JWT).
        task_id: UUID string of the task to update.
        title: New task title (optional).
        description: New task description (optional).

    Returns:
        JSON with task_id, status='updated', and title.
    """
    if title is None and description is None:
        return json.dumps({
            "error": "Must provide title or description to update",
            "code": "VALIDATION_ERROR",
        })

    try:
        tid = UUID(task_id)
    except ValueError:
        return json.dumps({"error": "Invalid task_id format", "code": "VALIDATION_ERROR"})

    updates: dict = {}
    if title is not None:
        if not title.strip():
            return json.dumps({"error": "Title cannot be empty", "code": "VALIDATION_ERROR"})
        updates["title"] = title.strip()
    if description is not None:
        updates["description"] = description

    try:
        async with async_session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.update(user_id, tid, updates)
            if not task:
                return json.dumps({"error": "Task not found", "code": "TASK_NOT_FOUND"})
            logger.info(f"[MCP:update_task] Updated task {task_id} for user {user_id}")
            return json.dumps({
                "task_id": str(task.id),
                "status": "updated",
                "title": task.title,
            })
    except Exception as e:
        logger.error(f"[MCP:update_task] Error: {e}")
        return json.dumps({"error": "Failed to update task", "code": "DATABASE_ERROR"})

