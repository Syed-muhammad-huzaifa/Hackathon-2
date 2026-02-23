"""
Complete MCP Task Server Implementation

This is a production-ready MCP server with 5 task management tools:
- add_task: Create new tasks
- list_tasks: List tasks with filtering
- complete_task: Mark tasks as complete
- delete_task: Remove tasks
- update_task: Update task details
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.server.fastapi import MCPServerFastAPI
from mcp.types import Tool, TextContent
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime
from typing import Optional
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Database model
class Task(SQLModel, table=True):
    """Task model."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# MCP Server
server = Server("task-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "title": {"type": "string", "description": "Task title", "maxLength": 500},
                    "description": {"type": "string", "description": "Optional task description"}
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks for a user with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["all", "pending", "completed"],
                        "default": "all"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to complete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task from the user's list",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to delete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's title or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New task title", "maxLength": 500},
                    "description": {"type": "string", "description": "New task description"}
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]

# Tool handlers
async def add_task_handler(arguments: dict) -> list[TextContent]:
    """Create a new task."""
    try:
        user_id = arguments["user_id"]
        title = arguments["title"].strip()
        description = arguments.get("description")

        if not title:
            return [TextContent(type="text", text=json.dumps({
                "error": "Title cannot be empty",
                "code": "VALIDATION_ERROR"
            }))]

        with Session(engine) as session:
            task = Task(user_id=user_id, title=title, description=description)
            session.add(task)
            session.commit()
            session.refresh(task)

            return [TextContent(type="text", text=json.dumps({
                "task_id": task.id,
                "status": "created",
                "title": task.title
            }))]

    except Exception as e:
        logger.error(f"Error in add_task: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "code": "DATABASE_ERROR"
        }))]

async def list_tasks_handler(arguments: dict) -> list[TextContent]:
    """List tasks for a user."""
    try:
        user_id = arguments["user_id"]
        status = arguments.get("status", "all")

        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            statement = statement.order_by(Task.created_at.desc())
            tasks = session.exec(statement).all()

            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]

            return [TextContent(type="text", text=json.dumps(task_list))]

    except Exception as e:
        logger.error(f"Error in list_tasks: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "code": "DATABASE_ERROR"
        }))]

async def complete_task_handler(arguments: dict) -> list[TextContent]:
    """Mark a task as completed."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]

        with Session(engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found",
                    "code": "TASK_NOT_FOUND"
                }))]

            task.completed = True
            task.updated_at = datetime.now()
            session.add(task)
            session.commit()

            return [TextContent(type="text", text=json.dumps({
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            }))]

    except Exception as e:
        logger.error(f"Error in complete_task: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "code": "DATABASE_ERROR"
        }))]

async def delete_task_handler(arguments: dict) -> list[TextContent]:
    """Delete a task."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]

        with Session(engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found",
                    "code": "TASK_NOT_FOUND"
                }))]

            task_info = {"task_id": task.id, "status": "deleted", "title": task.title}
            session.delete(task)
            session.commit()

            return [TextContent(type="text", text=json.dumps(task_info))]

    except Exception as e:
        logger.error(f"Error in delete_task: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "code": "DATABASE_ERROR"
        }))]

async def update_task_handler(arguments: dict) -> list[TextContent]:
    """Update a task."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]
        new_title = arguments.get("title")
        new_description = arguments.get("description")

        if new_title is None and new_description is None:
            return [TextContent(type="text", text=json.dumps({
                "error": "Must provide title or description to update",
                "code": "VALIDATION_ERROR"
            }))]

        with Session(engine) as session:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Task not found",
                    "code": "TASK_NOT_FOUND"
                }))]

            if new_title is not None:
                task.title = new_title.strip()
            if new_description is not None:
                task.description = new_description

            task.updated_at = datetime.now()
            session.add(task)
            session.commit()

            return [TextContent(type="text", text=json.dumps({
                "task_id": task.id,
                "status": "updated",
                "title": task.title
            }))]

    except Exception as e:
        logger.error(f"Error in update_task: {e}")
        return [TextContent(type="text", text=json.dumps({
            "error": str(e),
            "code": "DATABASE_ERROR"
        }))]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to handlers."""
    handlers = {
        "add_task": add_task_handler,
        "list_tasks": list_tasks_handler,
        "complete_task": complete_task_handler,
        "delete_task": delete_task_handler,
        "update_task": update_task_handler
    }

    handler = handlers.get(name)
    if not handler:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Unknown tool: {name}",
            "code": "UNKNOWN_TOOL"
        }))]

    return await handler(arguments)

# FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting MCP Task Server...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")
    yield
    logger.info("Shutting down MCP Task Server...")

app = FastAPI(title="Task MCP Server", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server
mcp_app = MCPServerFastAPI(server)
app.mount("/mcp", mcp_app)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Task MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "server": "task-mcp-server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
