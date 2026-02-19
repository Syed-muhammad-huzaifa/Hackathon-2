"""
Task repository for data access operations.

Handles all database queries for tasks with multi-tenancy enforcement.

@spec: specs/002-todo-backend-api/spec.md (FR-002, FR-003, FR-004, FR-005)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

from app.models.task import Task

logger = logging.getLogger(__name__)


class TaskRepository:
    """
    Repository for Task entity data access.

    All methods enforce multi-tenancy by filtering on user_id.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_user_id(self, user_id: str) -> list[Task]:
        """Find all non-deleted tasks for a user, newest first."""
        try:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.status != "deleted"
            ).order_by(Task.created_at.desc())

            result = await self.session.execute(statement)
            tasks = result.scalars().all()
            logger.debug(f"Found {len(tasks)} tasks for user {user_id}")
            return tasks
        except SQLAlchemyError as e:
            logger.error(f"Database error finding tasks for user {user_id}: {str(e)}")
            raise

    async def find_by_id(self, user_id: str, task_id: UUID) -> Optional[Task]:
        """Find a specific task by ID scoped to a user."""
        try:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await self.session.execute(statement)
            task = result.scalars().first()
            if task:
                logger.debug(f"Found task {task_id} for user {user_id}")
            else:
                logger.debug(f"Task {task_id} not found for user {user_id}")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Database error finding task {task_id} for user {user_id}: {str(e)}")
            raise

    async def create(self, user_id: str, task_data: dict) -> Task:
        """Insert a new task for a user."""
        try:
            task = Task(
                user_id=user_id,
                title=task_data["title"],
                description=task_data.get("description"),
                priority=task_data.get("priority", "medium"),
                status="pending",
            )
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            logger.debug(f"Created task {task.id} for user {user_id}")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Database error creating task for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def update(self, user_id: str, task_id: UUID, updates: dict) -> Optional[Task]:
        """Apply updates dict to an existing task."""
        try:
            task = await self.find_by_id(user_id, task_id)
            if not task:
                return None

            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            logger.debug(f"Updated task {task_id} for user {user_id}")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Database error updating task {task_id} for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise

    async def soft_delete(self, user_id: str, task_id: UUID) -> bool:
        """Set task status to 'deleted' (soft delete)."""
        try:
            task = await self.find_by_id(user_id, task_id)
            if not task:
                return False

            task.status = "deleted"
            task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

            self.session.add(task)
            await self.session.commit()
            logger.debug(f"Soft deleted task {task_id} for user {user_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting task {task_id} for user {user_id}: {str(e)}")
            await self.session.rollback()
            raise
