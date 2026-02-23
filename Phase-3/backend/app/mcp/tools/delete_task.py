"""
MCP tool: delete_task — soft-delete a task (status='deleted').
@spec: specs/001-chatbot-backend/contracts/mcp-tools.yaml
"""
import json
import logging
from uuid import UUID

from app.core.database import async_session_factory
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


async def delete_task_impl(user_id: str, task_id: str) -> str:
    """
    Delete a task from the list (soft delete).

    Args:
        user_id: The authenticated user's ID (from JWT).
        task_id: UUID string of the task to delete.

    Returns:
        JSON with task_id, status='deleted', and title.
    """
    try:
        tid = UUID(task_id)
    except ValueError:
        return json.dumps({"error": "Invalid task_id format", "code": "VALIDATION_ERROR"})

    try:
        async with async_session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.soft_delete(user_id, tid)
            if not task:
                return json.dumps({"error": "Task not found", "code": "TASK_NOT_FOUND"})
            logger.info(f"[MCP:delete_task] Deleted task {task_id} for user {user_id}")
            return json.dumps({
                "task_id": str(task.id),
                "status": "deleted",
                "title": task.title,
            })
    except Exception as e:
        logger.error(f"[MCP:delete_task] Error: {e}")
        return json.dumps({"error": "Failed to delete task", "code": "DATABASE_ERROR"})

