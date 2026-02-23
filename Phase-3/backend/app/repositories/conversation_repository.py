"""
Conversation repository — all DB operations for conversations.
@spec: specs/001-chatbot-backend/spec.md (FR-007, FR-008)
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, update

from app.models.conversation import Conversation

logger = logging.getLogger(__name__)


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, chatkit_thread_id: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user, optionally linking it to a ChatKit thread."""
        try:
            conv = Conversation(user_id=user_id, chatkit_thread_id=chatkit_thread_id)
            self.session.add(conv)
            await self.session.commit()
            await self.session.refresh(conv)
            logger.info(f"Created conversation {conv.id} for user {user_id} (chatkit_thread_id={chatkit_thread_id})")
            return conv
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise

    async def get_by_chatkit_thread_id(self, chatkit_thread_id: str) -> Optional[Conversation]:
        """Find a conversation by its ChatKit thread_id (used for recovery after restart)."""
        try:
            stmt = select(Conversation).where(Conversation.chatkit_thread_id == chatkit_thread_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching conversation by chatkit_thread_id {chatkit_thread_id}: {e}")
            raise

    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """Fetch conversation by ID (no user check — check in service)."""
        try:
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching conversation {conversation_id}: {e}")
            raise

    async def list_for_user(
        self,
        user_id: str,
        limit: int = 20,
        after: Optional[str] = None,
        order: str = "desc",
        chatkit_only: bool = True,
    ) -> tuple[list[Conversation], bool]:
        """
        List conversations for a user.
        Returns (conversations, has_more).
        """
        try:
            stmt = select(Conversation).where(Conversation.user_id == user_id)
            if chatkit_only:
                stmt = stmt.where(Conversation.chatkit_thread_id.is_not(None))

            # Cursor handling (use chatkit_thread_id as cursor if provided)
            if after:
                after_conv = await self.get_by_chatkit_thread_id(after)
                if after_conv:
                    if order == "desc":
                        stmt = stmt.where(Conversation.updated_at < after_conv.updated_at)
                    else:
                        stmt = stmt.where(Conversation.updated_at > after_conv.updated_at)

            order_col = Conversation.updated_at
            stmt = stmt.order_by(order_col.desc() if order == "desc" else order_col.asc())
            stmt = stmt.limit(limit + 1)

            result = await self.session.execute(stmt)
            items = result.scalars().all()
            has_more = len(items) > limit
            if has_more:
                items = items[:limit]
            return items, has_more
        except SQLAlchemyError as e:
            logger.error(f"Error listing conversations for user {user_id}: {e}")
            raise

    async def touch(self, conversation_id: UUID) -> None:
        """Update updated_at for a conversation."""
        try:
            await self.session.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(updated_at=datetime.utcnow())
            )
        except SQLAlchemyError as e:
            logger.error(f"Error updating conversation {conversation_id}: {e}")
            raise
