"""
Task repository — multi-tenancy enforced on every query.
Phase 3 has its own separate database (not shared with Phase 2).
@spec: specs/001-chatbot-backend/spec.md (FR-009, FR-010)
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.models.task import Task

logger = logging.getLogger(__name__)


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_user_id(self, user_id: str, status_filter: str = "all") -> list[Task]:
        """Return tasks for user, excluding soft-deleted rows."""
        try:
            stmt = select(Task).where(
                Task.user_id == user_id,
                Task.status != "deleted",
            )
            if status_filter == "pending":
                stmt = stmt.where(Task.status == "pending")
            elif status_filter == "completed":
                stmt = stmt.where(Task.status == "completed")
            elif status_filter == "in_progress":
                stmt = stmt.where(Task.status == "in_progress")

            stmt = stmt.order_by(Task.created_at.desc())
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error listing tasks for {user_id}: {e}")
            raise

    async def find_by_id(self, user_id: str, task_id: UUID) -> Optional[Task]:
        """Find task by ID scoped to user (multi-tenancy)."""
        try:
            stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error finding task {task_id}: {e}")
            raise

    async def create(self, user_id: str, title: str, description: Optional[str] = None) -> Task:
        """Insert a new task."""
        try:
            task = Task(user_id=user_id, title=title, description=description)
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating task: {e}")
            raise

    async def update(self, user_id: str, task_id: UUID, updates: dict) -> Optional[Task]:
        """Apply field updates to an existing task."""
        try:
            task = await self.find_by_id(user_id, task_id)
            if not task:
                return None
            for key, val in updates.items():
                if hasattr(task, key):
                    setattr(task, key, val)
            task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating task {task_id}: {e}")
            raise

    async def soft_delete(self, user_id: str, task_id: UUID) -> Optional[Task]:
        """Soft-delete by setting status='deleted'."""
        try:
            task = await self.find_by_id(user_id, task_id)
            if not task:
                return None
            title = task.title
            task.status = "deleted"
            task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            self.session.add(task)
            await self.session.commit()
            return task
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting task {task_id}: {e}")
            raise
