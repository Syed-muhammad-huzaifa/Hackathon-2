"""
Task API routes.

Handles HTTP requests for task CRUD operations.

@spec: specs/002-todo-backend-api/spec.md (FR-003, FR-004, FR-005, FR-006)
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, User
from app.models.task import (
    TaskListResponse,
    TaskResponse,
    TaskSingleResponse,
    TaskCreateRequest,
    TaskUpdateRequest,
)
from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository
from app.api.dependencies import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()


def get_task_repository(session: AsyncSession = Depends(get_db_session)) -> TaskRepository:
    return TaskRepository(session)


def get_task_service(repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repository)


@router.get("/api/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    tasks = await service.list_tasks(user_id)

    return TaskListResponse(
        status="success",
        data=[TaskResponse.model_validate(task) for task in tasks],
        meta={"total": len(tasks)},
    )


@router.get("/api/{user_id}/tasks/{task_id}", response_model=TaskSingleResponse)
async def get_task(
    user_id: str,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks",
        )

    task = await service.get_task(user_id, task_id)

    return TaskSingleResponse(
        status="success",
        data=TaskResponse.model_validate(task),
    )


@router.post("/api/{user_id}/tasks", response_model=TaskSingleResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself",
        )

    task = await service.create_task(user_id, task_request)

    return TaskSingleResponse(
        status="success",
        data=TaskResponse.model_validate(task),
        message="Task created successfully",
    )


@router.patch("/api/{user_id}/tasks/{task_id}", response_model=TaskSingleResponse)
async def update_task(
    user_id: str,
    task_id: UUID,
    task_request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks",
        )

    task = await service.update_task(user_id, task_id, task_request)

    return TaskSingleResponse(
        status="success",
        data=TaskResponse.model_validate(task),
        message="Task updated successfully",
    )


@router.delete("/api/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    user_id: str,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks",
        )

    await service.delete_task(user_id, task_id)

    return {"status": "success", "message": "Task deleted successfully"}
