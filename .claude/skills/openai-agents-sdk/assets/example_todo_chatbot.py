"""
Complete example: Todo AI Chatbot with OpenAI Agents SDK

This example demonstrates:
- Agent with MCP tools
- Stateless FastAPI chat endpoint
- Session persistence
- Error handling
- Production patterns
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from agents import Agent, Runner, SQLiteSession
from agents.mcp import MCPServerStreamableHttp
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
agent = None
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global agent, mcp_server

    logger.info("Starting application...")

    # Initialize MCP server
    mcp_server = await MCPServerStreamableHttp(
        name="Task Server",
        params={
            "url": os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp"),
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_TOKEN')}"},
            "timeout": 10
        },
        cache_tools_list=True,
        max_retry_attempts=3
    ).__aenter__()

    # Initialize agent
    agent = Agent(
        name="Task Manager",
        instructions="""You are a task management assistant.

Your role:
- Help users create, update, and manage tasks
- Use MCP tools for all task operations
- Provide clear, concise responses
- Confirm actions before executing

When users mention adding/creating tasks, use add_task tool.
When users ask to see tasks, use list_tasks tool.
When users mark tasks complete, use complete_task tool.
When users want to delete tasks, use delete_task tool.
When users want to update tasks, use update_task tool.""",
        mcp_servers=[mcp_server]
    )

    logger.info("Application started successfully")
    yield

    # Cleanup
    logger.info("Shutting down...")
    await mcp_server.__aexit__(None, None, None)

app = FastAPI(
    title="Todo AI Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Request/Response models
class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str | None = Field(None, max_length=100)

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

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        raise HTTPException(status_code=504, detail="Request timeout")

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": agent.name if agent else None,
        "mcp_server": "connected" if mcp_server else "disconnected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
