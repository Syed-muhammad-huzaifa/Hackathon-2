---
name: openai-agents-sdk
description: Build production-ready AI agents with OpenAI Agents SDK. Create agent definitions, integrate MCP servers as tools, implement stateless chat endpoints with FastAPI, manage conversation persistence, and configure runners (sync/async). This skill should be used when users ask to build AI agents, create chatbots, integrate MCP tools, implement agent-based systems, set up conversation state management, or build multi-agent workflows with handoffs.
---

# OpenAI Agents SDK

Build production-ready AI agents with MCP integration and stateless architecture.

## What This Skill Does

- Creates agent definitions with instructions and tools
- Integrates MCP servers (Hosted, Stdio, HTTP) as agent tools
- Implements stateless FastAPI chat endpoints
- Sets up conversation persistence with SQLiteSession
- Configures async/sync runners for agent execution
- Implements multi-agent handoffs and coordination
- Provides production patterns for agent deployment

## What This Skill Does NOT Do

- Deploy agents to production infrastructure
- Manage OpenAI API keys or billing
- Create MCP server implementations (use separate MCP skill)
- Handle frontend UI implementation
- Manage database migrations

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing FastAPI structure, database setup, project conventions |
| **Conversation** | User's specific requirements, agent purpose, tools needed |
| **Skill References** | Agent patterns, MCP integration, session management from `references/` |
| **User Guidelines** | Project-specific conventions, team standards, deployment targets |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

Ask about USER'S context (not domain knowledge):

1. **Agent purpose**: "What should the agent do? What domain/task?"
2. **MCP tools**: "Which MCP servers/tools will the agent use?"
3. **State management**: "How should conversation state be persisted? (SQLite, PostgreSQL, etc.)"
4. **API integration**: "Integrate with existing FastAPI app or create new?"
5. **Execution mode**: "Async or sync execution? (async recommended for FastAPI)"

---

## Implementation Workflow

### 1. Agent Definition

Create agent with instructions and configuration:

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="Task Manager",
    instructions="You help users manage tasks through natural language.",
    model="gpt-4o",
    model_settings=ModelSettings(
        temperature=0.7,
        tool_choice="auto"
    )
)
```

See `references/agent-patterns.md` for complete patterns.

### 2. MCP Tool Integration

Integrate MCP servers based on type:

| MCP Type | Use Case | Reference |
|----------|----------|-----------|
| **HostedMCPTool** | OpenAI-hosted MCP servers | `references/mcp-integration.md#hosted` |
| **MCPServerStdio** | Local stdio MCP servers | `references/mcp-integration.md#stdio` |
| **MCPServerStreamableHttp** | HTTP-based MCP servers | `references/mcp-integration.md#http` |

```python
from agents import Agent, HostedMCPTool

agent = Agent(
    name="Assistant",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "task_server",
                "server_url": "https://your-mcp-server.com",
                "require_approval": "never"
            }
        )
    ]
)
```

### 3. Session Persistence

Set up conversation state management:

```python
from agents import SQLiteSession

# In-memory session
session = SQLiteSession("user_123")

# Persistent file-based session
session = SQLiteSession("user_123", "conversations.db")
```

See `references/session-management.md` for database integration patterns.

### 4. Runner Configuration

Configure execution mode:

```python
from agents import Runner

# Async execution (recommended for FastAPI)
result = await Runner.run(agent, user_message, session=session)

# Sync execution
result = Runner.run_sync(agent, user_message, session=session)
```

See `references/runner-patterns.md` for advanced patterns.

### 5. FastAPI Integration

Create stateless chat endpoint:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner, SQLiteSession

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: str | None = None

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Load session
    session_id = request.conversation_id or f"user_{request.user_id}"
    session = SQLiteSession(session_id, "conversations.db")

    # Run agent
    result = await Runner.run(agent, request.message, session=session)

    return {
        "conversation_id": session_id,
        "response": result.final_output,
        "tool_calls": [item for item in result.new_items if item.get("type") == "tool_call"]
    }
```

See `references/fastapi-integration.md` for complete patterns.

---

## Agent Configuration Options

| Option | Purpose | Example |
|--------|---------|---------|
| `name` | Agent identifier | "Task Manager" |
| `instructions` | System prompt | "You help manage tasks..." |
| `model` | Model to use | "gpt-4o", "gpt-5-nano" |
| `tools` | Function tools | `[get_weather]` |
| `mcp_servers` | MCP server instances | `[server]` |
| `handoffs` | Other agents | `[billing_agent]` |
| `model_settings` | Model parameters | `ModelSettings(temperature=0.7)` |

---

## MCP Integration Patterns

### Pattern 1: Hosted MCP (OpenAI Infrastructure)

```python
from agents import Agent, HostedMCPTool

agent = Agent(
    name="Assistant",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "your_server",
                "server_url": "https://your-mcp-server.com",
                "require_approval": "never"
            }
        )
    ]
)
```

### Pattern 2: Local Stdio MCP

```python
from agents import Agent
from agents.mcp import MCPServerStdio

async with MCPServerStdio(
    name="Task Server",
    params={
        "command": "python",
        "args": ["mcp_server.py"]
    }
) as server:
    agent = Agent(
        name="Assistant",
        mcp_servers=[server]
    )
    result = await Runner.run(agent, "List tasks")
```

### Pattern 3: HTTP MCP with Authentication

```python
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="Task API",
    params={
        "url": "http://localhost:8000/mcp",
        "headers": {"Authorization": f"Bearer {token}"},
        "timeout": 10
    },
    cache_tools_list=True
) as server:
    agent = Agent(name="Assistant", mcp_servers=[server])
```

---

## Stateless Architecture Pattern

For scalable, stateless chat endpoints:

```python
# 1. Receive request
@app.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    # 2. Load conversation history from database
    session = SQLiteSession(request.conversation_id or f"user_{user_id}", "db.sqlite")

    # 3. Run agent (agent uses MCP tools)
    result = await Runner.run(agent, request.message, session=session)

    # 4. Return response (session auto-persists)
    return {"response": result.final_output}
```

**Benefits**:
- Any server instance can handle any request
- Server restarts don't lose state
- Horizontally scalable
- Session automatically persists to database

---

## Multi-Agent Handoffs

For triage patterns and specialized agents:

```python
from agents import Agent, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Specialized agents
task_agent = Agent(
    name="Task Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle task operations.",
    handoff_description="Manages tasks: create, list, update, delete"
)

# Triage agent
triage_agent = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route to appropriate agent.",
    handoffs=[task_agent]
)
```

See `references/handoffs.md` for advanced patterns.

---

## Output Checklist

Before delivering, verify:

### Agent Definition
- [ ] Agent has clear name and instructions
- [ ] Model specified (default: gpt-4o)
- [ ] Tools/MCP servers configured correctly

### MCP Integration
- [ ] MCP server type matches use case (Hosted/Stdio/HTTP)
- [ ] Server configuration includes all required params
- [ ] Authentication configured if needed

### Session Management
- [ ] SQLiteSession configured with appropriate storage
- [ ] Session ID strategy defined (per user/conversation)
- [ ] Database file path specified for persistence

### FastAPI Integration
- [ ] Endpoint is async (uses `await Runner.run`)
- [ ] Request/response models defined
- [ ] Session loaded from request data
- [ ] Error handling implemented

### Production Readiness
- [ ] Environment variables for sensitive data
- [ ] Logging configured
- [ ] Error handling for tool failures
- [ ] Max turns limit set if needed

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/agent-patterns.md` | Agent definition, configuration, model settings |
| `references/mcp-integration.md` | MCP server types, setup, authentication |
| `references/runner-patterns.md` | Async/sync execution, max_turns, result handling |
| `references/session-management.md` | SQLiteSession, persistence, database integration |
| `references/handoffs.md` | Multi-agent coordination, triage patterns |
| `references/fastapi-integration.md` | Stateless endpoints, request/response patterns |
| `references/production-patterns.md` | Error handling, logging, deployment |
