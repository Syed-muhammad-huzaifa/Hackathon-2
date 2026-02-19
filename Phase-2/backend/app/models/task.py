"""
Task model and Pydantic schemas.

Defines SQLModel entity and request/response schemas for tasks.

@spec: specs/002-todo-backend-api/spec.md (FR-002, FR-003, FR-004, FR-005)
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field as SQLField, SQLModel
from pydantic import BaseModel, Field, field_validator, field_serializer


class Task(SQLModel, table=True):
    """
    Task database model.

    All queries MUST filter by user_id for multi-tenancy.

    @spec: specs/002-todo-backend-api/spec.md (FR-002, FR-010)
    """
    __tablename__ = "tasks"

    id: UUID = SQLField(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = SQLField(nullable=False, index=True, max_length=255)
    title: str = SQLField(nullable=False, max_length=500)
    description: Optional[str] = SQLField(default=None, nullable=True)
    status: str = SQLField(default="pending", nullable=False, max_length=50, index=True)
    priority: Optional[str] = SQLField(default="medium", nullable=True, max_length=50)
    created_at: datetime = SQLField(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow, nullable=False)


# ── Request / Response Pydantic Schemas ─────────────────────────────────────

class TaskCreateRequest(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=10000, description="Task description")
    priority: Optional[str] = Field("medium", description="Task priority: low | medium | high")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("low", "medium", "high"):
            raise ValueError("priority must be one of: low, medium, high")
        return v


class TaskUpdateRequest(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = Field(None, description="pending | in_progress | completed")
    priority: Optional[str] = Field(None, description="low | medium | high")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace")
            return v
        return None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("pending", "in-progress", "completed"):
            raise ValueError("status must be one of: pending, in-progress, completed")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("low", "medium", "high"):
            raise ValueError("priority must be one of: low, medium, high")
        return v


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        """Always serialize datetimes as UTC ISO strings with Z suffix.

        Pydantic v2 serializes naive datetimes without timezone info,
        which Zod's z.string().datetime() rejects. We store naive UTC
        datetimes in the DB, so we just append 'Z' to signal UTC.
        """
        if dt.tzinfo is None:
            return dt.isoformat() + "Z"
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class TaskListResponse(BaseModel):
    """Schema for task list response."""
    status: str = "success"
    data: list[TaskResponse]
    meta: dict = Field(default_factory=lambda: {"total": 0})


class TaskSingleResponse(BaseModel):
    """Schema for single task response."""
    status: str = "success"
    data: TaskResponse
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    status: str = "error"
    code: str
    message: str
    details: Optional[dict] = None
