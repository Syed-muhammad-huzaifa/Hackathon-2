
"""
MCP tool: list_tasks — retrieve tasks for the authenticated user.
@spec: specs/001-chatbot-backend/contracts/mcp-tools.yaml
"""
import json
import logging

from app.core.database import async_session_factory
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


async def list_tasks_impl(user_id: str, status: str = "all") -> str:
    """
    Retrieve tasks for the user with optional status filter.

    Args:
        user_id: The authenticated user's ID (from JWT).
        status: Filter — 'all', 'pending', or 'completed'. Default: 'all'.

    Returns:
        JSON array of task objects.
    """
    if status not in ("all", "pending", "completed"):
        status = "all"

    try:
        async with async_session_factory() as session:
            repo = TaskRepository(session)
            tasks = await repo.find_by_user_id(user_id, status_filter=status)
            tasks = tasks[:5]  # cap at 5 — keep payload small for LLM token limits
            logger.info(f"[MCP:list_tasks] Found {len(tasks)} tasks for user {user_id}")
            return json.dumps([
                {"id": str(t.id), "title": t.title, "status": t.status}
                for t in tasks
            ])
    except Exception as e:
        logger.error(f"[MCP:list_tasks] Error: {e}")
        return json.dumps({"error": "Failed to retrieve tasks", "code": "DATABASE_ERROR"})
