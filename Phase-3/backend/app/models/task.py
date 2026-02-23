"""
Task model — Phase 3 separate database (not shared with Phase 2).
@spec: specs/001-chatbot-backend/spec.md (FR-009)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task table for Phase 3. Separate from Phase 2.
    status: 'pending' | 'in_progress' | 'completed' | 'deleted'
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    title: str = Field(nullable=False, max_length=500)
    description: Optional[str] = Field(default=None, nullable=True)
    status: str = Field(default="pending", nullable=False, max_length=50, index=True)
    priority: Optional[str] = Field(default="medium", nullable=True, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
