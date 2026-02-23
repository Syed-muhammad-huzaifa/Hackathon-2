"""
ChatService — orchestrates the OpenAI Agent with FastMCP server and conversation persistence.
Stateless: fetches history from DB each request, persists results back.
@spec: specs/001-chatbot-backend/spec.md (FR-003 to FR-015)
"""
import asyncio
import json
import logging
from typing import Optional
from uuid import UUID

from openai import AsyncOpenAI
from agents import Agent, Runner, ModelSettings
from agents.mcp import MCPServerStdio
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from agents.exceptions import InputGuardrailTripwireTriggered
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat import ChatResponse, ToolCallRecord
from app.services.guardrail import todo_only_guardrail, REFUSAL_MESSAGE

logger = logging.getLogger(__name__)

# ── Grok/Groq client via Chat Completions API ─────────────────
# Uses /v1/chat/completions (not /v1/responses) — required for Groq
# because Groq's responses API doesn't support MCP tool output format.
_grok_client = AsyncOpenAI(
    base_url=settings.GROK_BASE_URL,
    api_key=settings.GROK_API_KEY,
)

# ── MCP server subprocess (set by lifespan in main.py) ─────────
_mcp_server: Optional[MCPServerStdio] = None


def set_mcp_server(server: MCPServerStdio) -> None:
    """Called from app lifespan after MCPServerStdio is started."""
    global _mcp_server
    _mcp_server = server


# ── Agent system prompt ────────────────────────────────────────
AGENT_INSTRUCTIONS = """You are a task management assistant. Help users manage their tasks through natural language.

Your responsibilities:
- Create tasks when users mention adding, creating, or remembering something
- List tasks when users ask to see, show, or list tasks
- Complete tasks when users say done, finished, or mark as complete
- Delete tasks when users say delete, remove, or cancel
- Update tasks when users say change, rename, or update

IMPORTANT: You always have a user_id provided in context. Use it for ALL tool calls.
Always respond in a friendly, concise manner. Confirm actions clearly.
Never claim a task was created/updated/completed/deleted unless the corresponding tool output confirms success.
If a tool returns an error, timeout, or missing status, tell the user the action may have failed and ask them to retry.

Examples:
- "Add task to buy groceries" → call add_task → respond "✓ Task added: Buy groceries"
- "Show my tasks" → call list_tasks → respond with formatted list
- "Mark task <id> as done" → call complete_task → respond "✓ Task completed: <title>"
- "Delete task <id>" → call delete_task → respond "✓ Task deleted: <title>"
- "Change task <id> to 'New title'" → call update_task → respond "✓ Task updated: New title"

If user doesn't specify which task for delete/complete/update, first call list_tasks then ask to specify.
"""


def _build_agent(user_id: str) -> Agent:
    """Create a fresh agent instance with user_id injected into instructions."""
    if _mcp_server is None:
        raise RuntimeError("MCP server not initialised — lifespan did not run")
    instructions = (
        f"{AGENT_INSTRUCTIONS}\n\n"
        f"Current authenticated user_id: {user_id}\n"
        f"ALWAYS pass user_id='{user_id}' to every tool call."
    )
    # OpenAIChatCompletionsModel forces /v1/chat/completions — required for Groq
    # (Groq's /v1/responses endpoint doesn't support MCP tool output format)
    chat_model = OpenAIChatCompletionsModel(
        model=settings.GROK_MODEL,
        openai_client=_grok_client,
    )
    return Agent(
        name="Task Manager",
        instructions=instructions,
        model=chat_model,
        model_settings=ModelSettings(temperature=0.4, tool_choice="auto"),
        mcp_servers=[_mcp_server],
        input_guardrails=[todo_only_guardrail],
    )


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)

    async def process(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[UUID],
        chatkit_thread_id: Optional[str] = None,
    ) -> ChatResponse:
        """
        Stateless chat flow:
        1. Get or create conversation
        2. Fetch history from DB
        3. Run agent (uses FastMCP tools via stdio subprocess)
        4. Persist messages
        5. Return response
        """
        # Step 1: Get or create conversation
        if conversation_id:
            conv = await self.conv_repo.get_by_id(conversation_id)
            if not conv:
                logger.warning(f"Conversation {conversation_id} not found, creating new")
                conv = await self.conv_repo.create(user_id, chatkit_thread_id=chatkit_thread_id)
            elif conv.user_id != user_id:
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Conversation not found")
        elif chatkit_thread_id:
            # Try to recover the existing conversation via ChatKit thread_id (survives process restart)
            conv = await self.conv_repo.get_by_chatkit_thread_id(chatkit_thread_id)
            if not conv or conv.user_id != user_id:
                conv = await self.conv_repo.create(user_id, chatkit_thread_id=chatkit_thread_id)
                logger.info(f"Created new conversation {conv.id} for chatkit_thread_id={chatkit_thread_id}")
        else:
            conv = await self.conv_repo.create(user_id)

        # Step 2: Fetch conversation history (last 20 messages)
        history = await self.msg_repo.get_history(conv.id, user_id)

        # Step 3: Build agent input (plain dicts for Chat Completions API)
        if not history:
            agent_input = message
        else:
            input_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in history
            ]
            input_messages.append({"role": "user", "content": message})
            agent_input = input_messages  # type: ignore[assignment]

        # Step 4: Run agent via FastMCP server tools
        agent = _build_agent(user_id)
        try:
            result = await asyncio.wait_for(
                Runner.run(agent, agent_input, max_turns=10),
                timeout=60.0,
            )
        except InputGuardrailTripwireTriggered:
            logger.info(f"Guardrail tripped for user {user_id}: off-topic message")
            await self.msg_repo.create(conv.id, user_id, "user", message)
            await self.msg_repo.create(conv.id, user_id, "assistant", REFUSAL_MESSAGE)
            return ChatResponse(
                conversation_id=conv.id,
                response=REFUSAL_MESSAGE,
                tool_calls=[],
            )
        except asyncio.TimeoutError:
            logger.error(f"Agent timeout for user {user_id}")
            raise Exception("Agent execution timed out. Please try again.")
        except Exception as e:
            logger.error(f"Agent error for user {user_id}: {e}")
            raise Exception("I'm having trouble connecting right now. Please try again.")

        # Step 5: Extract tool calls and their outputs
        tool_calls_records: list[ToolCallRecord] = []
        tool_calls_json: Optional[str] = None

        # Build a map from call_id → output for matching results to calls
        output_by_call_id: dict[str, dict] = {}
        for item in result.new_items:
            item_type = getattr(item, "type", None)
            if item_type == "tool_call_output_item":
                try:
                    raw = getattr(item, "raw_item", None)
                    call_id = None
                    output_str = ""
                    if isinstance(raw, dict):
                        call_id = raw.get("call_id") or raw.get("tool_call_id")
                        output_str = raw.get("output", "")
                    else:
                        call_id = getattr(raw, "call_id", None) or getattr(raw, "tool_call_id", None)
                        output_str = getattr(raw, "output", "")
                    if call_id:
                        try:
                            output_by_call_id[call_id] = json.loads(output_str) if output_str else {}
                        except (json.JSONDecodeError, TypeError):
                            output_by_call_id[call_id] = {"raw": output_str}
                except Exception:
                    pass

        for item in result.new_items:
            item_type = getattr(item, "type", None)
            if item_type == "tool_call_item":
                try:
                    raw = getattr(item, "raw_item", None)
                    tool_name = "unknown"
                    args_str = "{}"
                    call_id = None

                    if isinstance(raw, dict):
                        func = raw.get("function", {})
                        tool_name = func.get("name", "unknown")
                        args_str = func.get("arguments", "{}")
                        call_id = raw.get("id")
                    else:
                        func = getattr(raw, "function", None)
                        if func:
                            tool_name = getattr(func, "name", "unknown")
                            args_str = getattr(func, "arguments", "{}")
                        else:
                            tool_name = getattr(raw, "name", "unknown")
                            args_str = getattr(raw, "arguments", "{}")
                        call_id = getattr(raw, "id", None) or getattr(raw, "call_id", None)

                    params = json.loads(args_str or "{}")
                    tool_result = output_by_call_id.get(call_id, {}) if call_id else {}
                    tool_calls_records.append(
                        ToolCallRecord(tool=tool_name, parameters=params, result=tool_result)
                    )
                except Exception:
                    pass

        if tool_calls_records:
            tool_calls_json = json.dumps([tc.model_dump() for tc in tool_calls_records])

        assistant_response = result.final_output or "I'm not sure how to help with that."

        # Step 6: Persist messages
        await self.msg_repo.create(conv.id, user_id, "user", message)
        await self.msg_repo.create(
            conv.id, user_id, "assistant", assistant_response, tool_calls_json
        )

        logger.info(f"Chat processed for user {user_id}, conv {conv.id}, tools={len(tool_calls_records)}")

        return ChatResponse(
            conversation_id=conv.id,
            response=assistant_response,
            tool_calls=tool_calls_records,
        )
