---
name: mcp-task-server
description: Build MCP servers with task management tools using Official MCP SDK. Create server implementations with 5 task tools (add, list, complete, delete, update), integrate SQLModel with Neon PostgreSQL, implement stateless tools with database persistence, and deploy as FastAPI HTTP endpoints. This skill should be used when users ask to build MCP servers, create task management tools, implement MCP tool schemas, integrate MCP with databases, or deploy MCP servers with FastAPI.
---

# MCP Task Server

Build production-ready MCP servers with task management tools and database persistence.

## What This Skill Does

- Creates MCP server implementations with Official MCP SDK
- Implements 5 task management tools (add, list, complete, delete, update)
- Integrates SQLModel with Neon PostgreSQL for persistence
- Implements stateless tools with database storage
- Defines tool schemas with proper validation
- Deploys as FastAPI HTTP MCP server
- Provides production deployment patterns

## What This Skill Does NOT Do

- Create OpenAI agents (use openai-agents-sdk skill)
- Manage database migrations
- Handle frontend UI implementation
- Deploy infrastructure
- Manage API keys or secrets

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, database setup, conventions |
| **Conversation** | User's specific requirements, database schema, deployment target |
| **Skill References** | MCP patterns, tool schemas, database integration from `references/` |
| **User Guidelines** | Project-specific conventions, team standards |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Database**: "Using Neon PostgreSQL or local PostgreSQL?"
2. **Deployment**: "Deploy as standalone server or integrate with existing FastAPI app?"
3. **Authentication**: "Need authentication for MCP tools?"
4. **Additional tools**: "Need any tools beyond the 5 basic task operations?"

---

## Implementation Workflow

### 1. Database Models

Create SQLModel models for tasks:

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

See `references/database-models.md` for complete patterns.

### 2. MCP Tool Definitions

Define the 5 task tools with schemas:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("task-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["user_id", "title"]
            }
        ),
        # ... other tools
    ]
```

See `references/tool-schemas.md` for all 5 tools.

### 3. Tool Implementation

Implement stateless tools with database operations:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add_task":
        return await add_task_handler(arguments)
    # ... other tools
```

See `references/tool-implementation.md` for complete patterns.

### 4. FastAPI Integration

Deploy MCP server as HTTP endpoint:

```python
from fastapi import FastAPI
from mcp.server.fastapi import MCPServerFastAPI

app = FastAPI()
mcp_app = MCPServerFastAPI(server)
app.mount("/mcp", mcp_app)
```

See `references/fastapi-deployment.md` for production setup.

---

## Tool Specifications

### Tool: add_task

| Aspect | Details |
|--------|---------|
| **Purpose** | Create a new task |
| **Parameters** | user_id (string, required), title (string, required), description (string, optional) |
| **Returns** | task_id, status, title |
| **Database** | INSERT into tasks table |

### Tool: list_tasks

| Aspect | Details |
|--------|---------|
| **Purpose** | Retrieve tasks from the list |
| **Parameters** | user_id (string, required), status (string, optional: "all", "pending", "completed") |
| **Returns** | Array of task objects |
| **Database** | SELECT from tasks table with filters |

### Tool: complete_task

| Aspect | Details |
|--------|---------|
| **Purpose** | Mark a task as complete |
| **Parameters** | user_id (string, required), task_id (integer, required) |
| **Returns** | task_id, status, title |
| **Database** | UPDATE tasks SET completed=true |

### Tool: delete_task

| Aspect | Details |
|--------|---------|
| **Purpose** | Remove a task from the list |
| **Parameters** | user_id (string, required), task_id (integer, required) |
| **Returns** | task_id, status, title |
| **Database** | DELETE from tasks table |

### Tool: update_task

| Aspect | Details |
|--------|---------|
| **Purpose** | Modify task title or description |
| **Parameters** | user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional) |
| **Returns** | task_id, status, title |
| **Database** | UPDATE tasks table |

---

## Quick Start

1. **Create database models:**
   ```bash
   # Use assets/models.py as template
   ```

2. **Implement MCP server:**
   ```bash
   # Use assets/mcp_server.py as template
   ```

3. **Configure database:**
   ```bash
   # Update .env with DATABASE_URL
   ```

4. **Run server:**
   ```bash
   python mcp_server.py
   ```

5. **Test tools:**
   ```bash
   python scripts/test_tools.py
   ```

---

## Output Checklist

Before delivering, verify:

### Database Models
- [ ] Task model with all required fields
- [ ] user_id indexed for performance
- [ ] Timestamps (created_at, updated_at)
- [ ] SQLModel table=True configured

### MCP Tools
- [ ] All 5 tools defined (add, list, complete, delete, update)
- [ ] Tool schemas with proper validation
- [ ] user_id parameter in all tools
- [ ] Error handling implemented

### Database Integration
- [ ] Connection string configured
- [ ] Engine and session management
- [ ] Transactions for data consistency
- [ ] Connection pooling configured

### FastAPI Deployment
- [ ] MCP server mounted at /mcp endpoint
- [ ] Health check endpoint
- [ ] CORS configured if needed
- [ ] Environment variables for config

### Production Readiness
- [ ] Error handling and logging
- [ ] Input validation
- [ ] Database connection retry logic
- [ ] Proper HTTP status codes

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/database-models.md` | SQLModel models, Neon PostgreSQL setup |
| `references/tool-schemas.md` | Complete tool schema definitions |
| `references/tool-implementation.md` | Tool handler implementations |
| `references/fastapi-deployment.md` | FastAPI integration and deployment |
| `references/production-patterns.md` | Error handling, logging, monitoring |
