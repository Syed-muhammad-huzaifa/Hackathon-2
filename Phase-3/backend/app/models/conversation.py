"""
Conversation model — represents a chat session between user and AI.
@spec: specs/001-chatbot-backend/spec.md (FR-007, FR-008)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    # Stores the ChatKit frontend thread_id so we can recover state after process restart
    chatkit_thread_id: Optional[str] = Field(default=None, nullable=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
