"""
Message repository — persist and retrieve chat messages.
@spec: specs/001-chatbot-backend/spec.md (FR-005, FR-006, FR-014)
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, update

from app.models.conversation import Conversation
from app.models.message import Message

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 20  # FR-014: truncate to last 20 messages


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: UUID,
        user_id: str,
        role: str,
        content: str,
        tool_calls: Optional[str] = None,
    ) -> Message:
        """Persist a single message."""
        try:
            msg = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
            )
            self.session.add(msg)
            # Update conversation "last active" timestamp
            await self.session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )
            await self.session.commit()
            await self.session.refresh(msg)
            logger.info(
                "Saved message %s role=%s conv=%s user=%s",
                msg.id,
                msg.role,
                msg.conversation_id,
                msg.user_id,
            )
            return msg
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error saving message: {e}")
            raise

    async def get_history(
        self, conversation_id: UUID, user_id: str, limit: Optional[int] = None
    ) -> list[Message]:
        """Fetch last N messages for a conversation (oldest first)."""
        try:
            effective_limit = limit or HISTORY_LIMIT
            # Get last 20 ordered by created_at ascending (oldest → newest)
            stmt = (
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.user_id == user_id,
                )
                .order_by(Message.created_at.desc())
                .limit(effective_limit)
            )
            result = await self.session.execute(stmt)
            messages = result.scalars().all()
            # Reverse so oldest is first (chronological order for agent)
            return list(reversed(messages))
        except SQLAlchemyError as e:
            logger.error(f"Error fetching history: {e}")
            raise
