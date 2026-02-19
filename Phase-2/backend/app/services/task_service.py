"""
Task service for business logic.

Handles task operations with ownership validation and business rules.

@spec: specs/002-todo-backend-api/spec.md (FR-002, FR-003, FR-004, FR-005)
"""
from uuid import UUID
from fastapi import HTTPException, status
import logging

from app.models.task import Task, TaskCreateRequest, TaskUpdateRequest
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)


class TaskService:
    """Service layer for task business logic."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def list_tasks(self, user_id: str) -> list[Task]:
        try:
            tasks = await self.repository.find_by_user_id(user_id)
            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
            return tasks
        except Exception as e:
            logger.error(f"Error listing tasks for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks"
            )

    async def create_task(self, user_id: str, task_request: TaskCreateRequest) -> Task:
        if not task_request.title or len(task_request.title.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot be empty"
            )

        if task_request.description and len(task_request.description) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task description cannot exceed 10,000 characters"
            )

        try:
            task_data = {
                "title": task_request.title.strip(),
                "description": task_request.description.strip() if task_request.description else None,
                "priority": task_request.priority or "medium"
            }
            task = await self.repository.create(user_id, task_data)
            logger.info(f"Created task {task.id} for user {user_id}")
            return task
        except Exception as e:
            logger.error(f"Error creating task for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

    async def get_task(self, user_id: str, task_id: UUID) -> Task:
        try:
            task = await self.repository.find_by_id(user_id, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            return task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve task"
            )

    async def update_task(self, user_id: str, task_id: UUID, updates: TaskUpdateRequest) -> Task:
        try:
            task = await self.repository.find_by_id(user_id, task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            if task.status == "deleted":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update deleted task"
                )

            if updates.title is not None and len(updates.title.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task title cannot be empty"
                )

            if updates.description is not None and len(updates.description) > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Task description cannot exceed 10,000 characters"
                )

            update_data = {}
            if updates.title is not None:
                update_data["title"] = updates.title.strip()
            if updates.description is not None:
                update_data["description"] = updates.description.strip() if updates.description else None
            if updates.status is not None:
                update_data["status"] = updates.status
            if updates.priority is not None:
                update_data["priority"] = updates.priority

            updated_task = await self.repository.update(user_id, task_id, update_data)
            logger.info(f"Updated task {task_id} for user {user_id}")
            return updated_task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )

    async def delete_task(self, user_id: str, task_id: UUID) -> bool:
        try:
            task = await self.repository.find_by_id(user_id, task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )

            if task.status == "deleted":
                logger.info(f"Task {task_id} already deleted for user {user_id}")
                return True

            success = await self.repository.soft_delete(user_id, task_id)
            logger.info(f"Deleted task {task_id} for user {user_id}")
            return success
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
