"""
Message model — a single message in a conversation (user or assistant).
@spec: specs/001-chatbot-backend/spec.md (FR-005, FR-015)
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    conversation_id: UUID = Field(nullable=False, foreign_key="conversations.id", index=True)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    role: str = Field(nullable=False, max_length=20)  # 'user' | 'assistant'
    content: str = Field(nullable=False)
    tool_calls: Optional[str] = Field(default=None, nullable=True)  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
