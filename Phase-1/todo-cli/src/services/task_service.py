"""
Task service layer handling business logic for task operations.
"""
from typing import List, Optional
from src.models.task import Task
from src.storage.json_store import JSONStore


class TaskService:
    """
    Service layer for task operations.
    """
    def __init__(self, store: JSONStore):
        self.store = store

    def add_task(self, title: str, description: str = "") -> int:
        """
        Create a new task with the given title and optional description.

        Args:
            title: Required task title
            description: Optional task description

        Returns:
            Task ID of the created task

        Raises:
            ValueError: If title is empty
        """
        if not title or not title.strip():
            raise ValueError("Title must not be empty or contain only whitespace")

        task_data = {
            "title": title,
            "description": description,
            "status": "pending"
        }

        task_id = self.store.create_task(task_data)
        return task_id

    def view_tasks(self) -> List[Task]:
        """
        Retrieve all tasks in the system.

        Returns:
            List of task objects
        """
        return self.store.get_all_tasks()

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update title and/or description of an existing task.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            True if successful, False if task not found
        """
        # Get the current task to preserve fields not being updated
        current_task = self.store.get_task(task_id)
        if not current_task:
            return False

        # Prepare update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description

        return self.store.update_task(task_id, update_data)

    def delete_task(self, task_id: int) -> bool:
        """
        Remove a task from the system.

        Args:
            task_id: ID of the task to remove

        Returns:
            True if successful, False if task not found
        """
        return self.store.delete_task(task_id)

    def toggle_task_status(self, task_id: int) -> bool:
        """
        Toggle a task's status between pending and completed.

        Args:
            task_id: ID of the task to toggle

        Returns:
            True if successful, False if task not found
        """
        current_task = self.store.get_task(task_id)
        if not current_task:
            return False

        # Determine the new status
        new_status = "completed" if current_task.status == "pending" else "pending"

        # Update the task with the new status
        return self.store.update_task(task_id, {"status": new_status})
