# Session Management

Complete patterns for conversation persistence and state management.

---

## SQLiteSession Basics

Built-in session management with SQLite.

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant", instructions="Reply concisely.")

# In-memory session (lost on restart)
session = SQLiteSession("user_123")

# Persistent file-based session
session = SQLiteSession("user_123", "conversations.db")

# Use session
result = await Runner.run(agent, "Hello", session=session)
```

**Session ID strategies**:
- Per user: `f"user_{user_id}"`
- Per conversation: `f"conv_{conversation_id}"`
- Per user + conversation: `f"user_{user_id}_conv_{conv_id}"`

---

## Multi-Turn Conversations

Sessions automatically maintain conversation history.

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant", instructions="Reply concisely.")
session = SQLiteSession("conversation_123", "db.sqlite")

# Turn 1
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# Turn 2 - agent remembers previous context
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"

# Turn 3 - continues conversation
result = await Runner.run(
    agent,
    "What's the population?",
    session=session
)
print(result.final_output)  # "Approximately 39 million"
```

**How it works**:
1. Session stores all messages
2. Each run loads full history
3. Agent sees complete context
4. New messages appended automatically

---

## Session with Database Integration

Integrate SQLiteSession with existing database.

```python
from agents import Agent, Runner, SQLiteSession
from sqlmodel import Session, select
from database import engine, Conversation

async def chat(user_id: str, message: str, conversation_id: str | None):
    # Get or create conversation in your database
    with Session(engine) as db:
        if conversation_id:
            conversation = db.get(Conversation, conversation_id)
        else:
            conversation = Conversation(user_id=user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

    # Use conversation ID for session
    session = SQLiteSession(
        f"conv_{conversation.id}",
        "agent_sessions.db"
    )

    # Run agent
    result = await Runner.run(agent, message, session=session)

    return {
        "conversation_id": conversation.id,
        "response": result.final_output
    }
```

**Benefits**:
- Separate agent state from app database
- SQLiteSession handles conversation history
- Your database tracks metadata
- Clean separation of concerns

---

## Custom Session Storage

Implement custom session storage (PostgreSQL, Redis, etc.).

```python
from agents import Session as BaseSession
from typing import List, Dict, Any
import psycopg2

class PostgresSession(BaseSession):
    """Custom session using PostgreSQL."""

    def __init__(self, session_id: str, connection_string: str):
        self.session_id = session_id
        self.conn = psycopg2.connect(connection_string)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Load messages from PostgreSQL."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at",
            (self.session_id,)
        )
        return [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]

    def add_message(self, role: str, content: str):
        """Save message to PostgreSQL."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (self.session_id, role, content)
        )
        self.conn.commit()

# Usage
session = PostgresSession("user_123", "postgresql://...")
result = await Runner.run(agent, "Hello", session=session)
```

**When to use custom storage**:
- Need PostgreSQL/MySQL
- Existing database schema
- Advanced querying requirements
- Distributed systems

---

## Stateless Architecture Pattern

Build stateless chat endpoints with session persistence.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, SQLiteSession

app = FastAPI()
agent = Agent(name="Assistant", instructions="Be helpful.")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # 1. Determine session ID
    session_id = request.conversation_id or f"user_{request.user_id}"

    # 2. Load session (loads conversation history)
    session = SQLiteSession(session_id, "conversations.db")

    # 3. Run agent (agent sees full history)
    result = await Runner.run(agent, request.message, session=session)

    # 4. Return response (session auto-persists)
    return {
        "conversation_id": session_id,
        "response": result.final_output
    }
```

**Stateless benefits**:
- Any server handles any request
- Horizontal scaling
- Server restarts don't lose state
- Load balancer friendly

---

## Session Lifecycle

Understanding session lifecycle.

```python
from agents import SQLiteSession

# 1. Create session
session = SQLiteSession("user_123", "db.sqlite")

# 2. Load existing history (automatic)
# Session loads all previous messages from database

# 3. Run agent
result = await Runner.run(agent, "New message", session=session)

# 4. Save new messages (automatic)
# Session saves user message and agent response

# 5. Session persists
# All messages stored in database for next request
```

**Lifecycle stages**:
1. **Initialization**: Create session instance
2. **Load**: Retrieve conversation history
3. **Execute**: Run agent with full context
4. **Save**: Persist new messages
5. **Cleanup**: Session ready for next request

---

## Session Management in FastAPI

Complete FastAPI integration with session management.

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from agents import Agent, Runner, SQLiteSession
from pydantic import BaseModel
import os

# Global agent
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup."""
    global agent
    agent = Agent(
        name="Task Manager",
        instructions="Help users manage tasks.",
        # MCP servers would be initialized here
    )
    yield

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: list

@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest):
    """Stateless chat endpoint with session persistence."""
    try:
        # Determine session ID
        session_id = request.conversation_id or f"user_{user_id}_{os.urandom(8).hex()}"

        # Load session
        session = SQLiteSession(session_id, "conversations.db")

        # Run agent
        result = await Runner.run(agent, request.message, session=session)

        # Extract tool calls
        tool_calls = [
            item for item in result.new_items
            if item.get("type") == "tool_call"
        ]

        return ChatResponse(
            conversation_id=session_id,
            response=result.final_output,
            tool_calls=tool_calls
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Session Cleanup

Clean up old sessions to manage storage.

```python
import sqlite3
from datetime import datetime, timedelta

def cleanup_old_sessions(db_path: str, days: int = 30):
    """Delete sessions older than specified days."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cutoff = datetime.now() - timedelta(days=days)

    cursor.execute(
        "DELETE FROM messages WHERE created_at < ?",
        (cutoff,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    return deleted

# Run cleanup periodically
deleted = cleanup_old_sessions("conversations.db", days=30)
print(f"Deleted {deleted} old messages")
```

**Cleanup strategies**:
- Periodic cleanup (daily/weekly)
- Age-based deletion
- Size-based limits
- User-triggered deletion

---

## Session Metadata

Store additional metadata with sessions.

```python
from agents import SQLiteSession
from sqlmodel import Session, select
from database import engine, Conversation

async def chat_with_metadata(user_id: str, message: str, conversation_id: str | None):
    # Track conversation in your database
    with Session(engine) as db:
        if conversation_id:
            conversation = db.get(Conversation, conversation_id)
            conversation.updated_at = datetime.now()
            conversation.message_count += 1
        else:
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                message_count=1
            )
            db.add(conversation)

        db.commit()
        db.refresh(conversation)

    # Use SQLiteSession for agent conversation
    session = SQLiteSession(f"conv_{conversation.id}", "agent_sessions.db")
    result = await Runner.run(agent, message, session=session)

    return {
        "conversation_id": conversation.id,
        "response": result.final_output,
        "message_count": conversation.message_count
    }
```

**Metadata examples**:
- Message count
- Last activity timestamp
- User preferences
- Conversation tags
- Analytics data

---

## Testing with Sessions

Test conversation flows with sessions.

```python
import pytest
from agents import Agent, Runner, SQLiteSession

@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """Test agent maintains context across turns."""
    agent = Agent(name="Test", instructions="Reply concisely.")
    session = SQLiteSession("test_session")

    # Turn 1
    result1 = await Runner.run(
        agent,
        "My name is Alice",
        session=session
    )

    # Turn 2 - agent should remember name
    result2 = await Runner.run(
        agent,
        "What's my name?",
        session=session
    )

    assert "Alice" in result2.final_output

@pytest.mark.asyncio
async def test_session_isolation():
    """Test sessions are isolated."""
    agent = Agent(name="Test", instructions="Reply concisely.")

    session1 = SQLiteSession("session_1")
    session2 = SQLiteSession("session_2")

    # Different sessions should not share context
    await Runner.run(agent, "My name is Alice", session=session1)
    result = await Runner.run(agent, "What's my name?", session=session2)

    assert "Alice" not in result.final_output
```

---

## Session Best Practices

### 1. Session ID Strategy

```python
# Good: Predictable, user-scoped
session_id = f"user_{user_id}_conv_{conversation_id}"

# Bad: Random, can't resume conversations
session_id = str(uuid.uuid4())
```

### 2. Database Location

```python
# Good: Persistent file
session = SQLiteSession("user_123", "/data/conversations.db")

# Bad: In-memory (lost on restart)
session = SQLiteSession("user_123")
```

### 3. Error Handling

```python
try:
    session = SQLiteSession(session_id, "conversations.db")
    result = await Runner.run(agent, message, session=session)
except Exception as e:
    logger.error(f"Session error: {e}")
    # Handle gracefully
```

### 4. Session Cleanup

```python
# Schedule periodic cleanup
@app.on_event("startup")
async def schedule_cleanup():
    scheduler.add_job(
        cleanup_old_sessions,
        "cron",
        hour=2,  # 2 AM daily
        args=["conversations.db", 30]
    )
```

---

## Production Checklist

Before deploying session management:

- [ ] Use persistent file-based sessions
- [ ] Implement session ID strategy
- [ ] Add error handling
- [ ] Set up session cleanup
- [ ] Test multi-turn conversations
- [ ] Test session isolation
- [ ] Monitor database size
- [ ] Backup session database
- [ ] Document session schema
- [ ] Implement session expiration
