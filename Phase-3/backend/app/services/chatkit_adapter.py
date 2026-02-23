"""
ChatKit adapter using the official ChatKit protocol parser/serializer.
Bridges ChatKit requests to our existing /api/{user_id}/chat endpoint.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import AsyncIterator
from uuid import UUID, uuid4

import httpx
from chatkit.server import ChatKitServer, NonStreamingResult, StreamingResult
from chatkit.store import Store
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    Attachment,
    InferenceOptions,
    Page,
    ThreadItemDoneEvent,
    ThreadItem,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    UserMessageTextContent,
)
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.core.auth import get_current_user
from app.core.database import async_session_factory

logger = logging.getLogger(__name__)

# Persistent HTTP client — reused across requests to avoid TCP setup overhead
_http_client = httpx.AsyncClient(timeout=120.0)


class InMemoryChatKitStore(Store[dict]):
    """
    In-memory + DB-backed Store implementation for ChatKit protocol operations.
    On process restart, recovers thread→conversation mapping and message history
    from the database using chatkit_thread_id.
    """

    def __init__(self) -> None:
        self._threads: dict[str, ThreadMetadata] = {}
        self._items: dict[str, list[ThreadItem]] = {}
        self._attachments: dict[str, Attachment] = {}

    def generate_thread_id(self, context: dict) -> str:
        return str(uuid4())

    def generate_item_id(self, item_type, thread: ThreadMetadata, context: dict) -> str:
        return super().generate_item_id(item_type, thread, context)

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        thread = self._threads.get(thread_id)
        if thread is not None:
            return thread

        # Thread not in memory — attempt DB recovery via chatkit_thread_id
        metadata: dict[str, str] = {"user_id": context.get("user_id", "unknown")}
        backend_conv_id = await self._find_backend_conversation_id(thread_id, context)
        if backend_conv_id:
            metadata["backend_conversation_id"] = backend_conv_id
            logger.info(
                "Recovered thread %s → backend_conversation_id=%s from DB",
                thread_id,
                backend_conv_id,
            )
        else:
            logger.warning(
                "Thread %s not in memory and not found in DB — starting fresh for user %s",
                thread_id,
                context.get("user_id", "unknown"),
            )

        thread = ThreadMetadata(
            id=thread_id,
            created_at=datetime.now(timezone.utc),
            metadata=metadata,
        )
        self._threads[thread_id] = thread
        self._items.setdefault(thread_id, [])
        return thread

    async def _find_backend_conversation_id(self, chatkit_thread_id: str, context: dict) -> str | None:
        """Query the DB for a conversation that was linked to this chatkit_thread_id."""
        user_id = context.get("user_id")
        if not user_id:
            return None
        try:
            from app.repositories.conversation_repository import ConversationRepository
            async with async_session_factory() as session:
                repo = ConversationRepository(session)
                conv = await repo.get_by_chatkit_thread_id(chatkit_thread_id)
                if conv and conv.user_id == user_id:
                    return str(conv.id)
        except Exception as e:
            logger.error("DB lookup for chatkit_thread_id=%s failed: %s", chatkit_thread_id, e)
        return None

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        if "user_id" not in thread.metadata:
            thread.metadata["user_id"] = context.get("user_id", "unknown")
        self._threads[thread.id] = thread
        self._items.setdefault(thread.id, [])

        # Ensure a DB conversation exists for this thread
        user_id = thread.metadata.get("user_id")
        if user_id:
            try:
                from app.repositories.conversation_repository import ConversationRepository
                async with async_session_factory() as session:
                    repo = ConversationRepository(session)
                    conv = await repo.get_by_chatkit_thread_id(thread.id)
                    if not conv:
                        conv = await repo.create(user_id, chatkit_thread_id=thread.id)
                    if conv and conv.user_id == user_id:
                        thread.metadata["backend_conversation_id"] = str(conv.id)
            except Exception as e:
                logger.error("Failed to persist thread %s: %s", thread.id, e)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        items = self._items.get(thread_id, [])

        # If nothing in memory, try to hydrate from DB
        if not items:
            thread = self._threads.get(thread_id)
            if thread is None:
                thread = await self.load_thread(thread_id, context)
            backend_conv_id = thread.metadata.get("backend_conversation_id") if thread else None
            if not backend_conv_id:
                backend_conv_id = await self._find_backend_conversation_id(thread_id, context)
                if backend_conv_id and thread:
                    thread.metadata["backend_conversation_id"] = backend_conv_id
            if backend_conv_id:
                loaded = await self._load_items_from_db(thread_id, backend_conv_id, context)
                if loaded:
                    self._items[thread_id] = loaded
                    items = loaded

        ordered = list(items)
        if order == "desc":
            ordered.reverse()

        start_index = 0
        if after:
            for idx, item in enumerate(ordered):
                if item.id == after:
                    start_index = idx + 1
                    break

        page_data = ordered[start_index: start_index + limit]
        has_more = start_index + limit < len(ordered)
        next_after = page_data[-1].id if has_more and page_data else None

        return Page(data=page_data, has_more=has_more, after=next_after)

    async def _load_items_from_db(
        self, thread_id: str, backend_conversation_id: str, context: dict
    ) -> list[ThreadItem]:
        """Load DB messages for a conversation and convert to ChatKit ThreadItems."""
        user_id = context.get("user_id")
        if not user_id:
            return []
        try:
            from app.repositories.message_repository import MessageRepository
            from uuid import UUID as _UUID
            async with async_session_factory() as session:
                repo = MessageRepository(session)
                messages = await repo.get_history(
                    conversation_id=_UUID(backend_conversation_id),
                    user_id=user_id,
                )

            items: list[ThreadItem] = []
            for msg in messages:
                item_id = f"msg_{msg.id}"
                ts = msg.created_at.replace(tzinfo=timezone.utc) if msg.created_at.tzinfo is None else msg.created_at
                if msg.role == "user":
                    items.append(UserMessageItem(
                        id=item_id,
                        thread_id=thread_id,
                        created_at=ts,
                        content=[UserMessageTextContent(text=msg.content)],
                        inference_options=InferenceOptions(),
                    ))
                elif msg.role == "assistant":
                    items.append(AssistantMessageItem(
                        id=item_id,
                        thread_id=thread_id,
                        created_at=ts,
                        content=[AssistantMessageContent(text=msg.content)],
                    ))

            logger.info(
                "Hydrated %d messages from DB for thread %s (conv %s)",
                len(items),
                thread_id,
                backend_conversation_id,
            )
            return items
        except Exception as e:
            logger.error("Failed to load DB messages for conv %s: %s", backend_conversation_id, e)
            return []

    async def save_attachment(self, attachment: Attachment, context: dict) -> None:
        self._attachments[attachment.id] = attachment

    async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
        attachment = self._attachments.get(attachment_id)
        if attachment is None:
            raise ValueError(f"Attachment {attachment_id} not found")
        return attachment

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        self._attachments.pop(attachment_id, None)

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict,
    ) -> Page[ThreadMetadata]:
        user_id = context.get("user_id")
        if not user_id:
            return Page(data=[], has_more=False, after=None)

        try:
            from app.repositories.conversation_repository import ConversationRepository
            async with async_session_factory() as session:
                repo = ConversationRepository(session)
                conversations, has_more = await repo.list_for_user(
                    user_id=user_id,
                    limit=limit,
                    after=after,
                    order=order,
                    chatkit_only=True,
                )

            threads: list[ThreadMetadata] = []
            for conv in conversations:
                if not conv.chatkit_thread_id:
                    continue
                meta = {
                    "user_id": conv.user_id,
                    "backend_conversation_id": str(conv.id),
                }
                thread = ThreadMetadata(
                    id=conv.chatkit_thread_id,
                    created_at=conv.created_at.replace(tzinfo=timezone.utc)
                    if conv.created_at.tzinfo is None
                    else conv.created_at,
                    metadata=meta,
                )
                self._threads[thread.id] = thread
                self._items.setdefault(thread.id, [])
                threads.append(thread)

            next_after = threads[-1].id if has_more and threads else None
            return Page(data=threads, has_more=has_more, after=next_after)
        except Exception as e:
            logger.error("Failed to load threads for user %s: %s", user_id, e)
            return Page(data=[], has_more=False, after=None)

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        self._items.setdefault(thread_id, []).append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        thread_items = self._items.setdefault(thread_id, [])
        for idx, existing in enumerate(thread_items):
            if existing.id == item.id:
                thread_items[idx] = item
                return
        thread_items.append(item)

    async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
        for item in self._items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise ValueError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        self._threads.pop(thread_id, None)
        self._items.pop(thread_id, None)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None:
        items = self._items.get(thread_id, [])
        self._items[thread_id] = [item for item in items if item.id != item_id]


class AdapterChatKitServer(ChatKitServer[dict]):
    """ChatKitServer that forwards user messages to the existing chat endpoint."""

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        user_id = context["user_id"]
        auth_header = context["authorization"]

        user_message = ""
        if input_user_message and getattr(input_user_message, "type", None) == "user_message":
            for part in input_user_message.content:
                text = getattr(part, "text", None)
                if isinstance(text, str):
                    user_message += text
        user_message = user_message.strip()

        if not user_message:
            raise HTTPException(status_code=400, detail="Empty user message")

        backend_conversation_id = thread.metadata.get("backend_conversation_id")

        chat_response = await _http_client.post(
            f"http://localhost:8001/api/{user_id}/chat",
            json={
                "message": user_message,
                "conversation_id": backend_conversation_id,
                "chatkit_thread_id": thread.id,
            },
            headers={"Authorization": auth_header},
        )

        if chat_response.status_code != 200:
            raise HTTPException(
                status_code=chat_response.status_code,
                detail=f"Chat endpoint error: {chat_response.text}",
            )

        chat_data = chat_response.json()

        backend_conversation_id = chat_data.get("conversation_id")
        if backend_conversation_id:
            thread.metadata["backend_conversation_id"] = str(backend_conversation_id)

        response_text = chat_data.get("response", "")
        tool_calls = chat_data.get("tool_calls") or []
        if tool_calls:
            tools_used = ", ".join(tc.get("tool", "unknown") for tc in tool_calls)
            response_text += f"\n\nTools used: {tools_used}"

        assistant_item = AssistantMessageItem(
            id=self.store.generate_item_id("message", thread, context),
            thread_id=thread.id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(text=response_text)],
        )

        logger.info("ChatKit adapter: user=%s, message=%s...", user_id, user_message[:50])
        yield ThreadItemDoneEvent(item=assistant_item)


store = InMemoryChatKitStore()
server = AdapterChatKitServer(store=store)


def create_chatkit_adapter() -> FastAPI:
    app = FastAPI(title="ChatKit Adapter")

    async def _handle(request: Request):
        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing authorization")

        user = await get_current_user(authorization=auth_header)

        body = await request.body()
        result = await server.process(
            body,
            {
                "user_id": user.id,
                "authorization": auth_header,
            },
        )

        if isinstance(result, StreamingResult):
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )

        if isinstance(result, NonStreamingResult):
            return Response(content=result.json, media_type="application/json")

        return result

    @app.post("")
    async def process_noslash(request: Request):
        return await _handle(request)

    @app.post("/")
    async def process_root(request: Request):
        return await _handle(request)

    @app.post("/process")
    async def process_legacy(request: Request):
        return await _handle(request)

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "chatkit-adapter"}

    return app


chatkit_adapter_app = create_chatkit_adapter()
