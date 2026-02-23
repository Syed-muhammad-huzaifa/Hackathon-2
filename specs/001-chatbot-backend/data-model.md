# Data Model: AI Chatbot Backend

**Feature**: 001-chatbot-backend
**Date**: 2026-02-21
**Spec Reference**: [spec.md](./spec.md) - FR-005, FR-006, FR-009

---

## Overview

The chatbot backend introduces two new entities (Conversation, Message) while reusing the existing Task entity from Phase 2. All entities enforce multi-tenancy through user_id filtering.

---

## Entity: Conversation

**Purpose**: Represents a chat session between a user and the AI assistant. Each conversation contains multiple messages and maintains conversation context across requests.

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique conversation identifier |
| `user_id` | String | Foreign Key (users.id), NOT NULL, Indexed | Owner of the conversation |
| `created_at` | DateTime (TZ) | NOT NULL, Default: now(), Indexed | Conversation creation timestamp |
| `updated_at` | DateTime (TZ) | NOT NULL, Default: now() | Last modification timestamp |

### Relationships

- **Belongs to**: User (Better Auth) via `user_id`
- **Has many**: Messages via `conversation_id`

### Validation Rules

- `user_id` MUST exist in `users` table (enforced by foreign key)
- `created_at` defaults to current timestamp on creation
- `updated_at` automatically updated on any message addition
- Conversation CANNOT be created without valid `user_id`

### Indexes

```sql
-- Primary key index (automatic)
CREATE INDEX pk_conversations ON conversations(id);

-- Multi-tenancy + listing performance
CREATE INDEX ix_conversations_user_id_created_at
ON conversations(user_id, created_at DESC);
```

**Index Rationale**:
- `(user_id, created_at DESC)`: Enables fast retrieval of user's conversations ordered by recency
- Supports query: "Get all conversations for user X, newest first"

### State Transitions

Conversations have no explicit state field. State is implicit:
- **Active**: Has messages, user can continue conversation
- **Archived**: No explicit archive state in MVP (future enhancement)

### Multi-tenancy Enforcement

```python
# All queries MUST filter by user_id
query = select(Conversation).where(
    Conversation.user_id == authenticated_user_id
)
```

---

## Entity: Message

**Purpose**: Represents a single message in a conversation. Messages can be from the user or the AI assistant. Tool calls are stored for debugging and audit purposes.

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique message identifier |
| `conversation_id` | UUID | Foreign Key (conversations.id), NOT NULL, Indexed | Parent conversation |
| `user_id` | String | Foreign Key (users.id), NOT NULL, Indexed | Message owner (for multi-tenancy) |
| `role` | Enum | NOT NULL, Values: 'user' \| 'assistant' | Message sender |
| `content` | Text | NOT NULL, Min: 1 char | Message text content |
| `tool_calls` | JSONB | Nullable | Array of MCP tool invocations (assistant only) |
| `created_at` | DateTime (TZ) | NOT NULL, Default: now(), Indexed | Message timestamp |

### Relationships

- **Belongs to**: Conversation via `conversation_id`
- **Belongs to**: User via `user_id`

### Validation Rules

- `conversation_id` MUST exist in `conversations` table
- `user_id` MUST match `conversations.user_id` (same owner)
- `role` MUST be either 'user' or 'assistant'
- `content` CANNOT be empty string
- `tool_calls` MUST be valid JSON array if present
- `tool_calls` only valid when `role = 'assistant'`

### Tool Calls Schema

When `role = 'assistant'` and tools were invoked:

```json
{
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "user123",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": 5,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

### Indexes

```sql
-- Primary key index (automatic)
CREATE INDEX pk_messages ON messages(id);

-- Conversation history retrieval (chronological order)
CREATE INDEX ix_messages_conversation_id_created_at
ON messages(conversation_id, created_at ASC);

-- User message search (newest first)
CREATE INDEX ix_messages_user_id_created_at
ON messages(user_id, created_at DESC);
```

**Index Rationale**:
- `(conversation_id, created_at ASC)`: Enables fast retrieval of conversation messages in chronological order
- `(user_id, created_at DESC)`: Supports user-wide message search (future feature)

### Multi-tenancy Enforcement

```python
# All queries MUST filter by user_id
query = select(Message).where(
    Message.user_id == authenticated_user_id,
    Message.conversation_id == conversation_id
)

# Additional validation: conversation belongs to user
conversation = await conversation_repo.get_by_id(conversation_id, user_id)
if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")
```

---

## Entity: Task (Existing - Phase 2)

**Purpose**: Todo items managed by users. No schema changes required.

### Attributes (Reference Only)

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique task identifier |
| `user_id` | String | Foreign Key (users.id), NOT NULL, Indexed | Task owner |
| `title` | String(200) | NOT NULL | Task title |
| `description` | Text | Nullable | Task description |
| `completed` | Boolean | NOT NULL, Default: false | Completion status |
| `created_at` | DateTime (TZ) | NOT NULL, Default: now() | Creation timestamp |
| `updated_at` | DateTime (TZ) | NOT NULL, Default: now() | Last modification timestamp |

### Access Pattern

MCP tools access tasks via Phase 2 task repository:

```python
# MCP tool implementation
from phase2.repositories import TaskRepository

async def add_task(params: AddTaskParams) -> AddTaskResult:
    # Reuse Phase 2 repository (multi-tenancy enforced)
    task = await task_repository.create(
        user_id=params.user_id,
        title=params.title,
        description=params.description
    )
    return AddTaskResult(task_id=task.id, status="created", title=task.title)
```

**No Direct SQL**: MCP tools MUST NOT write raw SQL queries. They MUST use Phase 2 repository methods to ensure multi-tenancy and business logic consistency.

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     User        │ (Better Auth - existing)
│  (Phase 2)      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼─────────────────┐
    │   Conversation       │ (New - Phase 3)
    │  - id (UUID)         │
    │  - user_id (FK)      │
    │  - created_at        │
    │  - updated_at        │
    └────────┬─────────────┘
             │
             │ 1:N
             │
        ┌────▼──────────────┐
        │    Message        │ (New - Phase 3)
        │  - id (UUID)      │
        │  - conversation_id│
        │  - user_id (FK)   │
        │  - role (enum)    │
        │  - content (text) │
        │  - tool_calls     │
        │  - created_at     │
        └───────────────────┘

┌─────────────────┐
│     User        │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────▼─────────────────┐
    │      Task            │ (Existing - Phase 2)
    │  - id (int)          │
    │  - user_id (FK)      │
    │  - title             │
    │  - description       │
    │  - completed         │
    │  - created_at        │
    │  - updated_at        │
    └──────────────────────┘
```

**Note**: Tasks and Conversations are independent. MCP tools bridge them by reading/writing tasks based on conversation context.

---

## Database Schema Creation

**Method**: SQLModel with FastAPI `on_event("startup")`

**Implementation**:
```python
# app/main.py
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
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✓ Database tables created/verified")
```

**Advantages**:
- Idempotent: Safe to run multiple times (creates only if not exists)
- No migration files to maintain
- Tables created automatically on server startup
- SQLModel handles schema from Python models
- Simpler for MVP (no version tracking)

**Rollback Strategy**: Drop tables manually if needed (not automated)

**Data Migration**: None required (new tables, no existing data)

---

## SQLModel Definitions

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
```

### Message Model

```python
from sqlmodel import SQLModel, Field, Relationship, Enum
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum as PyEnum

class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole)))
    content: str = Field(min_length=1)
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

---

## Query Patterns

### Fetch Conversation History (Last 20 Messages)

```python
async def get_conversation_history(
    conversation_id: UUID,
    user_id: str,
    limit: int = 20
) -> list[Message]:
    query = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # Multi-tenancy
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.exec(query)
    messages = result.all()
    return list(reversed(messages))  # Chronological order for AI
```

### Create New Conversation

```python
async def create_conversation(user_id: str) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### Add Message to Conversation

```python
async def add_message(
    conversation_id: UUID,
    user_id: str,
    role: MessageRole,
    content: str,
    tool_calls: dict | None = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message
```

---

## Performance Considerations

### Index Coverage

All common queries are covered by indexes:
- ✅ List user's conversations: `(user_id, created_at DESC)`
- ✅ Fetch conversation messages: `(conversation_id, created_at ASC)`
- ✅ Search user's messages: `(user_id, created_at DESC)`

### Query Optimization

- **No N+1 queries**: Single query fetches all messages for conversation
- **Limit clause**: Always fetch limited messages (default 20)
- **Pagination**: Future enhancement for conversation listing

### Storage Estimates

- Average message: 200 characters = ~200 bytes
- 20 messages per conversation = 4 KB
- 100 conversations per user = 400 KB
- 1000 users = 400 MB (manageable)

---

## Security Considerations

### Multi-tenancy Enforcement

Every query MUST include `user_id` filter:
```python
# ✅ CORRECT
query = select(Conversation).where(Conversation.user_id == user_id)

# ❌ WRONG - Security vulnerability
query = select(Conversation).where(Conversation.id == conversation_id)
```

### Data Isolation

- User A cannot access User B's conversations
- User A cannot access User B's messages
- Enforced at repository layer (defense in depth)
- Validated at service layer (business logic)
- Checked at API layer (JWT verification)

### Cascade Deletes

- When user deleted → conversations deleted → messages deleted
- Prevents orphaned data
- Maintains referential integrity

---

## Future Enhancements (Out of Scope for MVP)

- Conversation titles (auto-generated from first message)
- Conversation archiving/deletion
- Message editing/deletion
- Full-text search on message content
- Conversation sharing between users
- Message reactions/feedback
- Conversation export (JSON/PDF)
