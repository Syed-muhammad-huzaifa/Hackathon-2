"""
FastMCP task management server.
- Runs as stdio subprocess (agent connects via MCPServerStdio)
- Mounted at /mcp in FastAPI for external MCP clients
Tools: add_task, list_tasks, complete_task, delete_task, update_task
"""
from typing import Optional

from fastmcp import FastMCP

from app.mcp.tools.add_task import add_task_impl
from app.mcp.tools.list_tasks import list_tasks_impl
from app.mcp.tools.complete_task import complete_task_impl
from app.mcp.tools.delete_task import delete_task_impl
from app.mcp.tools.update_task import update_task_impl

mcp = FastMCP("Task Server")


@mcp.tool
async def add_task(user_id: str, title: str, description: Optional[str] = None) -> str:
    """Create a new task for the user."""
    return await add_task_impl(user_id=user_id, title=title, description=description)


@mcp.tool
async def list_tasks(user_id: str, status: str = "all") -> str:
    """List tasks for a user. status: all | pending | completed"""
    return await list_tasks_impl(user_id=user_id, status=status)


@mcp.tool
async def complete_task(user_id: str, task_id: str) -> str:
    """Mark a task as completed."""
    return await complete_task_impl(user_id=user_id, task_id=task_id)


@mcp.tool
async def delete_task(user_id: str, task_id: str) -> str:
    """Delete (soft-delete) a task."""
    return await delete_task_impl(user_id=user_id, task_id=task_id)


@mcp.tool
async def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Update a task's title or description. At least one of title/description required."""
    return await update_task_impl(
        user_id=user_id,
        task_id=task_id,
        title=title,
        description=description,
    )


if __name__ == "__main__":
    mcp.run()  # stdio transport — used when spawned as subprocess by agent
