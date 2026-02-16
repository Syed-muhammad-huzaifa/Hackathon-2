"""
In-memory storage implementation for tasks.
"""
from typing import Dict, List, Optional
from src.models.task import Task


class InMemoryStore:
    """
    In-memory storage using dictionary structure to store tasks.
    """
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, task_data: dict) -> int:
        """
        Add a new task to storage.

        Args:
            task_data: Dictionary containing task information

        Returns:
            ID of created task
        """
        task_id = self._next_id
        self._next_id += 1

        # Create task with the generated ID
        task = Task(
            id=task_id,
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=task_data.get("status", "pending")
        )

        self._tasks[task_id] = task
        return task_id

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks from storage.

        Returns:
            List of all task objects
        """
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object or None if not found
        """
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, task_data: dict) -> bool:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            task_data: Updated task data

        Returns:
            True if successful, False if not found
        """
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]

        # Update fields if provided in task_data
        if "title" in task_data:
            task.title = task_data["title"]
        if "description" in task_data:
            task.description = task_data["description"]
        if "status" in task_data:
            task.status = task_data["status"]

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Remove a task from storage.

        Args:
            task_id: ID of the task to remove

        Returns:
            True if successful, False if not found
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        return True
