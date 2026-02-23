# Research Findings: AI Chatbot Backend

**Date**: 2026-02-21
**Feature**: 001-chatbot-backend
**Purpose**: Resolve technical unknowns before design phase

---

## R1: OpenAI Agents SDK Integration Pattern

**Question**: How does OpenAI Agents SDK integrate with custom MCP tools in a stateless FastAPI application?

**Decision**: Use OpenAI Agents SDK with MCP tool registration via Official MCP SDK, initializing agent per-request with conversation history as context.

**Rationale**:
- OpenAI Agents SDK supports custom tool registration through MCP protocol
- Stateless pattern: Create new agent instance per request (no shared state)
- Conversation history passed as message array to agent for context
- Agent automatically determines which tools to call based on user intent

**Implementation Pattern**:
```python
from openai import AsyncOpenAI
from mcp import MCPServer

# Initialize per-request
async def process_chat(user_message: str, history: list[dict]):
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Build message array: history + new user message
    messages = history + [{"role": "user", "content": user_message}]

    # Agent processes with MCP tools available
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=mcp_server.get_tools(),  # MCP tools registered
        tool_choice="auto"
    )

    # Handle tool calls if agent invoked any
    if response.choices[0].message.tool_calls:
        tool_results = await execute_tool_calls(response.choices[0].message.tool_calls)
        # Continue conversation with tool results
        messages.append(response.choices[0].message)
        messages.append({"role": "tool", "content": tool_results})

        # Get final response after tool execution
        final_response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return final_response.choices[0].message.content

    return response.choices[0].message.content
```

**Alternatives Considered**:
- **Persistent agent instance**: Rejected because it violates stateless architecture and prevents horizontal scaling
- **Custom intent parser**: Rejected because OpenAI Agents SDK provides superior natural language understanding

**Token Limit Management**:
- Truncate conversation history to last 20 messages before sending to agent
- Keep system message + recent messages for context
- Approximate token count: ~4 tokens per word (conservative estimate)
- Max context: ~8000 tokens for GPT-4 (leaves room for response)

**Error Handling**:
- OpenAI API timeout: Return user-friendly error, don't crash
- Rate limit (429): Return retry-after header
- Invalid API key: Fail fast on startup, not per-request

---

## R2: Official MCP SDK for Python

**Question**: What is the correct pattern for implementing MCP tools using the Official MCP SDK?

**Decision**: Use Official MCP SDK's `@mcp.tool()` decorator pattern with Pydantic schemas for type safety and automatic validation.

**Rationale**:
- Official MCP SDK provides standardized tool registration
- Pydantic integration ensures type safety and validation
- Automatic schema generation for OpenAI function calling
- Error propagation handled by SDK

**Implementation Pattern**:
```python
from mcp import MCPServer, tool
from pydantic import BaseModel, Field

# Initialize MCP server
mcp_server = MCPServer(name="task-management")

# Define tool schema
class AddTaskParams(BaseModel):
    user_id: str = Field(description="Authenticated user ID")
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional description")

class AddTaskResult(BaseModel):
    task_id: int
    status: str
    title: str

# Register tool
@mcp_server.tool()
async def add_task(params: AddTaskParams) -> AddTaskResult:
    """Create a new task for the user."""
    # Call Phase 2 task repository
    task = await task_repository.create(
        user_id=params.user_id,
        title=params.title,
        description=params.description
    )

    return AddTaskResult(
        task_id=task.id,
        status="created",
        title=task.title
    )

# Export tools for OpenAI agent
tools = mcp_server.get_tools()
```

**Alternatives Considered**:
- **Manual function calling**: Rejected because MCP SDK provides better standardization and error handling
- **LangChain tools**: Rejected because Official MCP SDK is the standard for this project

**Error Propagation**:
- Tool exceptions caught by MCP SDK
- Converted to structured error responses
- Agent receives error and can respond appropriately to user

**Async Support**:
- All MCP tools declared as `async def`
- Enables non-blocking database operations
- Compatible with FastAPI async request handlers

---

## R3: Stateless Conversation Management

**Question**: How to efficiently fetch and truncate conversation history for AI context while maintaining stateless architecture?

**Decision**: Fetch last 20 messages per conversation using database query with LIMIT, order by created_at ASC for chronological context.

**Rationale**:
- Database is single source of truth (no in-memory state)
- LIMIT 20 keeps token usage manageable (~8000 tokens max)
- Ordering ASC provides chronological context to AI
- Index on (conversation_id, created_at) ensures fast queries

**Repository Method**:
```python
async def get_conversation_history(
    self,
    conversation_id: int,
    user_id: str,
    limit: int = 20
) -> list[Message]:
    """
    Fetch recent messages for conversation context.

    Returns messages in chronological order (oldest first) for AI context.
    """
    query = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # Multi-tenancy enforcement
        )
        .order_by(Message.created_at.desc())  # Get most recent first
        .limit(limit)
    )

    result = await self.session.exec(query)
    messages = result.all()

    # Reverse to chronological order for AI
    return list(reversed(messages))
```

**Performance Optimization**:
- Composite index: `(conversation_id, created_at DESC)`
- Query time: < 10ms for 20 messages
- No N+1 queries (single query fetches all messages)

**Truncation Strategy**:
- Always keep system message (if present)
- Keep last 20 user/assistant messages
- Discard older messages (not deleted, just not sent to AI)
- User can still see full history in frontend (separate query)

**Token Counting**:
- Approximate: 4 tokens per word (conservative)
- Average message: 50 words = 200 tokens
- 20 messages = 4000 tokens (leaves 4000 for response)
- If exceeds limit: reduce to 15 messages

**Alternatives Considered**:
- **Semantic truncation**: Rejected as too complex for MVP
- **Sliding window**: Rejected because last N messages is simpler and sufficient

---

## R4: Better Auth JWT Verification (Phase 2 Pattern)

**Question**: How to reuse Phase 2's JWT verification pattern for Phase 3 backend?

**Decision**: Copy Phase 2's `app/core/auth.py` module to Phase 3 with same JWKS verification pattern.

**Rationale**:
- Phase 2 already implements correct JWT verification via JWKS
- Same Better Auth instance (same JWKS endpoint)
- Same shared secret (BETTER_AUTH_SECRET)
- Proven pattern that works in production

**Implementation** (from Phase 2):
```python
# Phase-3/backend/app/core/auth.py (copied from Phase 2)

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

security = HTTPBearer()

async def _get_jwks() -> dict:
    """Fetch JWKS from Better Auth server with caching."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BETTER_AUTH_URL.rstrip('/')}/api/auth/jwks",
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return payload.

    Raises HTTPException(401) if token is invalid.
    """
    try:
        # Fetch JWKS (cached)
        jwks = await _get_jwks()

        # Decode and verify token
        payload = jwt.decode(
            credentials.credentials,
            jwks,
            algorithms=["RS256"],
            options={"verify_signature": True, "verify_exp": True}
        )

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user_id(
    user_id: str,  # From path parameter
    token_payload: dict = Depends(verify_token)
) -> str:
    """
    Verify user_id in path matches JWT subject claim.

    Raises HTTPException(403) if mismatch.
    """
    if token_payload.get("sub") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )
    return user_id
```

**Environment Variables** (same as Phase 2):
```bash
BETTER_AUTH_URL=https://phase3-frontend.vercel.app
BETTER_AUTH_SECRET=<same-secret-as-phase-2>
```

**FastAPI Dependency Usage**:
```python
@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str = Path(...),
    request: ChatRequest = Body(...),
    authenticated_user_id: str = Depends(get_current_user_id)
):
    # authenticated_user_id is verified to match user_id
    # Proceed with chat logic
    pass
```

**Alternatives Considered**:
- **Rewrite from scratch**: Rejected because Phase 2 pattern is proven and working
- **Shared library**: Rejected as premature optimization for MVP

---

## R5: Database Schema Creation Strategy

**Question**: How to add Conversation and Message tables without breaking Phase 2 schema?

**Decision**: Use SQLModel with FastAPI `on_event("startup")` to create tables automatically on server start. No migration files needed.

**Rationale**:
- SQLModel `create_all()` creates tables if they don't exist (idempotent)
- Adding new tables is non-breaking (Phase 2 unaffected)
- Foreign keys ensure referential integrity
- Indexes defined in SQLModel are created automatically
- Simpler than Alembic for MVP (no migration version tracking needed)
- FastAPI event ensures tables exist before accepting requests

**Implementation Pattern**:
```python
# Phase-3/backend/app/main.py

from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.models.conversation import Conversation
from app.models.message import Message

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        # Create all tables defined in SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)

    print("✓ Database tables created/verified")
```

**SQLModel Definitions with Indexes**:
```python
# app/models/conversation.py
from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    __table_args__ = (
        Index('ix_conversations_user_id_created_at', 'user_id', 'created_at'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# app/models/message.py
from sqlmodel import SQLModel, Field, Column, JSON, Index
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        Index('ix_messages_conversation_id_created_at', 'conversation_id', 'created_at'),
        Index('ix_messages_user_id_created_at', 'user_id', 'created_at'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: MessageRole
    content: str
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Index Strategy**:
- `(user_id, created_at)` on conversations: Fast user conversation listing
- `(conversation_id, created_at)` on messages: Fast message history fetch
- `(user_id, created_at)` on messages: Fast user message search

**Foreign Key Constraints**:
- `conversations.user_id` → `user.id` (Better Auth table)
- `messages.conversation_id` → `conversations.id`
- `messages.user_id` → `user.id`
- CASCADE delete: Handled by database (default behavior)

**Data Types**:
- UUID for primary keys (better for distributed systems)
- JSON for tool_calls (SQLModel uses JSON column type)
- Enum for role (type safety at Python and database level)
- str for content (no length limit in PostgreSQL TEXT)

**Table Creation**:
```bash
# Tables created automatically on server startup
uv run uvicorn app.main:app --reload

# Output:
# ✓ Database tables created/verified
# INFO: Uvicorn running on http://0.0.0.0:8000
```

**Advantages over Alembic**:
- No migration files to maintain
- Idempotent (safe to run multiple times)
- Simpler for MVP (no version tracking)
- Tables created automatically on startup
- SQLModel handles schema from Python models

**Alternatives Considered**:
- **Alembic migrations**: Rejected as overkill for MVP (adds complexity)
- **Modify existing tables**: Rejected because it would break Phase 2
- **Separate database**: Rejected because shared users table is required
- **NoSQL for messages**: Rejected because PostgreSQL JSON provides sufficient flexibility

---

## Summary

All technical unknowns resolved. Key decisions:

1. **OpenAI Agents SDK**: Per-request agent initialization with conversation history as context
2. **MCP SDK**: Official SDK with `@mcp.tool()` decorator and Pydantic schemas
3. **Stateless Architecture**: Database as single source of truth, fetch last 20 messages per request
4. **JWT Verification**: Reuse Phase 2 pattern (JWKS verification)
5. **Database Migration**: Alembic migration adds new tables without breaking Phase 2

**Ready for Phase 1**: Design artifacts (data-model.md, contracts/, quickstart.md)
