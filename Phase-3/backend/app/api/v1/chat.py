"""
Chat API endpoint — POST /api/{user_id}/chat
Stateless: every request is self-contained (history from DB).
@spec: specs/001-chatbot-backend/spec.md (FR-001, FR-002, FR-017, FR-018)
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import User, get_current_user
from app.core.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Send a natural language message to the AI task manager.

    - Verifies JWT and checks user_id matches token subject (FR-002)
    - Creates or continues a conversation (FR-007)
    - Processes message with OpenAI Agent + MCP tools (FR-003, FR-004)
    - Persists messages and returns AI response (FR-005, FR-011)
    """
    # FR-002: user_id in URL must match JWT subject
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": "error", "code": "FORBIDDEN", "message": "User ID mismatch"},
        )

    try:
        service = ChatService(session)
        response = await service.process(
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            chatkit_thread_id=request.chatkit_thread_id,
        )
        return response

    except HTTPException:
        raise  # Re-raise 403 from service

    except Exception as e:
        logger.error(f"Chat endpoint error for user {user_id}: {e}")
        # FR-012 / FR-013: user-friendly error messages
        error_msg = str(e) if str(e).startswith("I'm") or "timed out" in str(e) else \
            "Unable to process request. Please try again."
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "code": "AI_SERVICE_ERROR", "message": error_msg},
        )
