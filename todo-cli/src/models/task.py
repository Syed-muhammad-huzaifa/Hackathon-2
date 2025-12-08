"""
Task model representing a single todo item.
"""
from dataclasses import dataclass
from typing import Optional


class Task:
    """
    Represents a single todo item with an ID, title, description, and status.
    """
    def __init__(self, id: int, title: str, description: Optional[str] = "", status: str = "pending"):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.validate()

    def validate(self):
        """
        Validate the task after initialization.
        """
        if not self.title or not self.title.strip():
            raise ValueError("Title must not be empty or contain only whitespace")

        if self.status not in ["pending", "completed"]:
            raise ValueError("Status must be either 'pending' or 'completed'")

    def to_dict(self) -> dict:
        """
        Convert the task to a dictionary representation.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Task instance from a dictionary.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "pending")
        )
