# FastAPI Integration

Complete patterns for integrating OpenAI agents with FastAPI.

---

## Basic Chat Endpoint

Minimal stateless chat endpoint.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, SQLiteSession

app = FastAPI()

# Initialize agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Create or load session
    session_id = request.session_id or f"session_{os.urandom(8).hex()}"
    session = SQLiteSession(session_id, "conversations.db")

    # Run agent
    result = await Runner.run(agent, request.message, session=session)

    return ChatResponse(
        session_id=session_id,
        response=result.final_output
    )
```

---

## Complete Stateless Chat API

Production-ready stateless chat endpoint with MCP tools.

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp
import os
import logging

logger = logging.getLogger(__name__)

# Global state
agent = None
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global agent, mcp_server

    # Startup: Initialize MCP server and agent
    logger.info("Initializing MCP server...")
    mcp_server = await MCPServerStreamableHttp(
        name="Task Server",
        params={
            "url": os.getenv("MCP_SERVER_URL"),
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_TOKEN')}"},
            "timeout": 10
        },
        cache_tools_list=True,
        max_retry_attempts=3
    ).__aenter__()

    logger.info("Initializing agent...")
    agent = Agent(
        name="Task Manager",
        instructions="You help users manage tasks through natural language.",
        mcp_servers=[mcp_server]
    )

    yield

    # Shutdown: Cleanup
    logger.info("Shutting down MCP server...")
    await mcp_server.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)

# Request/Response models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: list[ToolCall]

@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest):
    """
    Stateless chat endpoint with conversation persistence.

    Flow:
    1. Load conversation history from database
    2. Run agent with MCP tools
    3. Return response (session auto-persists)
    """
    try:
        # Determine session ID
        session_id = request.conversation_id or f"user_{user_id}"

        # Load session (loads conversation history)
        session = SQLiteSession(session_id, "conversations.db")

        # Run agent
        logger.info(f"Processing message for user {user_id}")
        result = await Runner.run(
            agent,
            request.message,
            session=session,
            max_turns=10
        )

        # Extract tool calls
        tool_calls = [
            ToolCall(
                tool_name=item.get("name", "unknown"),
                arguments=item.get("arguments", {})
            )
            for item in result.new_items
            if item.get("type") == "tool_call"
        ]

        logger.info(f"Response generated with {len(tool_calls)} tool calls")

        return ChatResponse(
            conversation_id=session_id,
            response=result.final_output,
            tool_calls=tool_calls
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "agent": agent.name if agent else None}
```

---

## User-Scoped Endpoints

Separate endpoints per user with authentication.

```python
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Annotated
import jwt

app = FastAPI()

# Authentication
def verify_token(authorization: Annotated[str, Header()]) -> str:
    """Verify JWT token and return user_id."""
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(verify_token)
):
    """Authenticated chat endpoint."""
    # Use user_id from token
    session_id = f"user_{user_id}_conv_{request.conversation_id or 'default'}"
    session = SQLiteSession(session_id, "conversations.db")

    result = await Runner.run(agent, request.message, session=session)

    return {
        "conversation_id": session_id,
        "response": result.final_output
    }
```

---

## Database Integration

Integrate with SQLModel database.

```python
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select, create_engine
from datetime import datetime
from agents import Agent, Runner, SQLiteSession

# Database models
from sqlmodel import SQLModel, Field

class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    message_count: int = 0

class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

# Database setup
engine = create_engine(os.getenv("DATABASE_URL"))
SQLModel.metadata.create_all(engine)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with database integration."""
    with Session(engine) as db:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.get(Conversation, request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=request.user_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)

        # Run agent (uses separate SQLiteSession for agent state)
        session = SQLiteSession(f"conv_{conversation.id}", "agent_sessions.db")
        result = await Runner.run(agent, request.message, session=session)

        # Store assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result.final_output
        )
        db.add(assistant_message)

        # Update conversation metadata
        conversation.updated_at = datetime.now()
        conversation.message_count += 2
        db.commit()

        return {
            "conversation_id": conversation.id,
            "response": result.final_output
        }
```

---

## Error Handling

Comprehensive error handling.

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with error handling."""
    try:
        session = SQLiteSession(request.session_id, "conversations.db")
        result = await Runner.run(agent, request.message, session=session)
        return {"response": result.final_output}

    except TimeoutError:
        logger.error("Agent execution timeout")
        raise HTTPException(status_code=504, detail="Request timeout")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Streaming Responses

Stream agent responses for better UX.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import Agent, Runner
import json

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream agent responses."""
    async def generate():
        session = SQLiteSession(request.session_id, "conversations.db")

        async for chunk in Runner.stream(agent, request.message, session=session):
            # Send chunk as SSE
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

        # Send completion
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## Rate Limiting

Implement rate limiting per user.

```python
from fastapi import FastAPI, HTTPException, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat")
@limiter.limit("10/minute")  # 10 requests per minute
async def chat(request: ChatRequest):
    """Rate-limited chat endpoint."""
    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(agent, request.message, session=session)
    return {"response": result.final_output}
```

---

## CORS Configuration

Enable CORS for frontend access.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Environment Configuration

Use environment variables for configuration.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    mcp_server_url: str
    mcp_token: str
    database_url: str
    jwt_secret: str

    class Config:
        env_file = ".env"

settings = Settings()

# Use in app
@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_server = await MCPServerStreamableHttp(
        name="Task Server",
        params={
            "url": settings.mcp_server_url,
            "headers": {"Authorization": f"Bearer {settings.mcp_token}"},
            "timeout": 10
        }
    ).__aenter__()

    agent = Agent(name="Assistant", mcp_servers=[mcp_server])
    yield
    await mcp_server.__aexit__(None, None, None)
```

---

## Testing FastAPI Endpoints

Test chat endpoints.

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_chat_endpoint():
    """Test basic chat functionality."""
    response = client.post(
        "/api/chat",
        json={
            "user_id": "test_user",
            "message": "Hello",
            "conversation_id": None
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data

def test_chat_with_session():
    """Test conversation continuity."""
    # First message
    response1 = client.post(
        "/api/chat",
        json={"user_id": "test", "message": "My name is Alice"}
    )
    session_id = response1.json()["conversation_id"]

    # Second message - should remember context
    response2 = client.post(
        "/api/chat",
        json={
            "user_id": "test",
            "message": "What's my name?",
            "conversation_id": session_id
        }
    )

    assert "Alice" in response2.json()["response"]
```

---

## Logging and Monitoring

Add comprehensive logging.

```python
import logging
from fastapi import FastAPI, Request
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({duration:.2f}s)")

    return response

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with logging."""
    logger.info(f"Chat request from user {request.user_id}")

    try:
        session = SQLiteSession(request.session_id, "conversations.db")
        result = await Runner.run(agent, request.message, session=session)

        logger.info(f"Response generated: {len(result.final_output)} chars")
        return {"response": result.final_output}

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise
```

---

## Production Deployment

Complete production setup.

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production lifecycle management."""
    # Startup
    logger.info("Starting application...")

    # Initialize MCP server
    global mcp_server, agent
    mcp_server = await MCPServerStreamableHttp(
        name="Task Server",
        params={
            "url": os.getenv("MCP_SERVER_URL"),
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_TOKEN')}"},
            "timeout": 10
        },
        cache_tools_list=True
    ).__aenter__()

    # Initialize agent
    agent = Agent(
        name="Task Manager",
        instructions="Help users manage tasks.",
        mcp_servers=[mcp_server]
    )

    logger.info("Application started successfully")
    yield

    # Shutdown
    logger.info("Shutting down application...")
    await mcp_server.__aexit__(None, None, None)
    logger.info("Application shut down successfully")

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Add endpoints
@app.post("/api/chat")
async def chat(request: ChatRequest):
    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(agent, request.message, session=session)
    return {"response": result.final_output}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable in production
        workers=4  # Multiple workers
    )
```

---

## Production Checklist

Before deploying FastAPI integration:

- [ ] Use lifespan for MCP server management
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Configure CORS properly
- [ ] Add comprehensive error handling
- [ ] Implement logging
- [ ] Use environment variables
- [ ] Add health check endpoint
- [ ] Test with multiple concurrent requests
- [ ] Set up monitoring
- [ ] Configure proper timeouts
- [ ] Use connection pooling
- [ ] Implement graceful shutdown
- [ ] Add request validation
- [ ] Document API endpoints
