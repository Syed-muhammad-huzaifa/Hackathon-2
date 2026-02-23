"""
Tasks REST API — GET /api/{user_id}/tasks
Direct DB query, no LLM roundtrip. Used by analytics and history pages.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_session
from app.repositories.task_repository import TaskRepository

router = APIRouter(tags=["Tasks"])


@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Return tasks for a user directly from DB (no LLM).
    Optional ?status=pending|completed|in_progress|all
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": "error", "code": "FORBIDDEN", "message": "User ID mismatch"},
        )

    filter_val = status_filter or "all"
    if filter_val not in ("all", "pending", "completed", "in_progress"):
        filter_val = "all"

    repo = TaskRepository(session)
    tasks = await repo.find_by_user_id(user_id, status_filter=filter_val)

    task_list = [
        {"id": str(t.id), "title": t.title, "status": t.status}
        for t in tasks
    ]

    return {
        "tasks": task_list,
        "total": len(task_list),
        "completed": sum(1 for t in task_list if t["status"] == "completed"),
        "pending": sum(1 for t in task_list if t["status"] == "pending"),
        "inProgress": sum(1 for t in task_list if t["status"] == "in_progress"),
    }
