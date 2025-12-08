"""
JSON file-based storage implementation for tasks.
"""
import json
import os
from typing import Dict, List, Optional
from src.models.task import Task


class JSONStore:
    """
    JSON file-based storage that persists tasks to a JSON file.
    """
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = file_path
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
        self._load_from_file()

    def _load_from_file(self):
        """
        Load tasks from the JSON file if it exists.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    tasks_data = data.get("tasks", {})
                    next_id = data.get("next_id", 1)

                    # Convert loaded data back to Task objects
                    self._tasks = {}
                    for task_id_str, task_data in tasks_data.items():
                        task_id = int(task_id_str)
                        self._tasks[task_id] = Task.from_dict(task_data)

                    self._next_id = next_id
            except (json.JSONDecodeError, KeyError, ValueError):
                # If there's an error loading the file, start fresh
                self._tasks = {}
                self._next_id = 1
        else:
            # If file doesn't exist, start fresh
            self._tasks = {}
            self._next_id = 1

    def _save_to_file(self):
        """
        Save tasks to the JSON file.
        """
        # Convert tasks to dictionary format
        tasks_dict = {str(task_id): task.to_dict() for task_id, task in self._tasks.items()}

        data = {
            "tasks": tasks_dict,
            "next_id": self._next_id
        }

        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except IOError:
            # Handle potential file write errors gracefully
            print(f"Warning: Could not save tasks to {self.file_path}")

    def create_task(self, task_data: dict) -> int:
        """
        Add a new task to storage and persist to file.

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
        self._save_to_file()
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
        Update an existing task and persist changes to file.

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

        self._save_to_file()
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Remove a task from storage and persist changes to file.

        Args:
            task_id: ID of the task to remove

        Returns:
            True if successful, False if not found
        """
        if task_id not in self._tasks:
            return False

        del self._tasks[task_id]
        self._save_to_file()
        return True
