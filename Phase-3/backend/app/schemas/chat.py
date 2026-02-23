"""
Request/response schemas for the chat API endpoint.
@spec: specs/001-chatbot-backend/contracts/chat-api.yaml
"""
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's natural language message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID. Omit to start new.")
    chatkit_thread_id: Optional[str] = Field(None, description="ChatKit thread ID for conversation recovery.")


class ToolCallRecord(BaseModel):
    tool: str
    parameters: dict[str, Any]
    result: Any


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    tool_calls: list[ToolCallRecord] = []


class ErrorResponse(BaseModel):
    status: str = "error"
    code: str
    message: str
    details: Optional[dict] = None
