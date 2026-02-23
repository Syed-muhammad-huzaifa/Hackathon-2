# MCP Integration

Complete patterns for integrating MCP servers with OpenAI agents.

---

## MCP Server Types

| Type | Use Case | Hosting | Authentication |
|------|----------|---------|----------------|
| **HostedMCPTool** | OpenAI-hosted servers | OpenAI infrastructure | Server-managed |
| **MCPServerStdio** | Local processes | Your infrastructure | Process-level |
| **MCPServerStreamableHttp** | HTTP endpoints | Your infrastructure | HTTP headers |

---

## Pattern 1: Hosted MCP (Recommended for Production)

OpenAI hosts and manages the MCP server.

```python
from agents import Agent, HostedMCPTool, Runner

agent = Agent(
    name="Assistant",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "task_server",
                "server_url": "https://your-mcp-server.com",
                "require_approval": "never"  # or "always", "if_needed"
            }
        )
    ]
)

# Use agent
result = await Runner.run(agent, "List all tasks")
```

**Configuration options**:
- `server_label`: Identifier for the MCP server
- `server_url`: URL where MCP server is hosted
- `require_approval`: Tool approval policy
  - `"never"`: Auto-approve all tool calls
  - `"always"`: Require approval for every call
  - `"if_needed"`: Approve based on tool risk

**Benefits**:
- No server management
- Automatic scaling
- Built-in monitoring
- Simplified deployment

**Use when**:
- Production deployments
- High availability required
- Don't want to manage infrastructure

---

## Pattern 2: Local Stdio MCP

Run MCP server as local subprocess.

```python
import asyncio
from pathlib import Path
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def main():
    # Context manager ensures proper cleanup
    async with MCPServerStdio(
        name="Task Server",
        params={
            "command": "python",
            "args": ["mcp_server.py"]
        }
    ) as server:
        agent = Agent(
            name="Task Manager",
            instructions="Use MCP tools to manage tasks.",
            mcp_servers=[server]
        )

        result = await Runner.run(agent, "Add task: Buy groceries")
        print(result.final_output)

asyncio.run(main())
```

**With Node.js MCP server**:
```python
async with MCPServerStdio(
    name="Filesystem Server",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(samples_dir)]
    }
) as server:
    agent = Agent(name="File Assistant", mcp_servers=[server])
```

**Benefits**:
- Full control over server
- Local development friendly
- No network latency
- Easy debugging

**Use when**:
- Development/testing
- Local-only operations
- Need full server control

---

## Pattern 3: HTTP MCP with Authentication

Connect to HTTP-based MCP server.

```python
import asyncio
import os
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

async def main():
    token = os.environ["MCP_SERVER_TOKEN"]

    async with MCPServerStreamableHttp(
        name="Task API",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": f"Bearer {token}"},
            "timeout": 10
        },
        cache_tools_list=True,
        max_retry_attempts=3
    ) as server:
        agent = Agent(
            name="Assistant",
            instructions="Use MCP tools to answer questions.",
            mcp_servers=[server]
        )

        result = await Runner.run(agent, "List pending tasks")
        print(result.final_output)

asyncio.run(main())
```

**Configuration options**:
- `url`: MCP server endpoint
- `headers`: Authentication headers
- `timeout`: Request timeout (seconds)
- `cache_tools_list`: Cache available tools (performance)
- `max_retry_attempts`: Retry failed requests

**Benefits**:
- Remote server support
- Standard HTTP authentication
- Flexible deployment
- Network-based scaling

**Use when**:
- Remote MCP servers
- Microservices architecture
- Need authentication
- Multiple agents sharing server

---

## Multiple MCP Servers

Agent can use multiple MCP servers simultaneously.

```python
async with MCPServerStdio(
    name="Task Server",
    params={"command": "python", "args": ["task_server.py"]}
) as task_server, \
MCPServerStdio(
    name="Calendar Server",
    params={"command": "python", "args": ["calendar_server.py"]}
) as calendar_server:

    agent = Agent(
        name="Personal Assistant",
        instructions="Use task and calendar tools to help users.",
        mcp_servers=[task_server, calendar_server]
    )

    result = await Runner.run(
        agent,
        "Add task 'Team meeting' and schedule it for tomorrow at 2pm"
    )
```

**Best practices**:
- Use descriptive server names
- Avoid tool name conflicts
- Document which server provides which tools
- Consider tool namespacing

---

## MCP Tool Discovery

Agent automatically discovers tools from MCP servers.

```python
# Agent discovers all tools from MCP server
async with MCPServerStdio(name="Server", params={...}) as server:
    agent = Agent(name="Assistant", mcp_servers=[server])

    # Agent can now use:
    # - add_task
    # - list_tasks
    # - complete_task
    # - delete_task
    # - update_task
    # (whatever tools the MCP server exposes)
```

**Tool naming**:
- MCP server defines tool names
- Agent sees tools as function calls
- Tool descriptions come from MCP server

---

## Error Handling

Handle MCP server connection and tool errors.

```python
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def main():
    try:
        async with MCPServerStdio(
            name="Task Server",
            params={"command": "python", "args": ["mcp_server.py"]}
        ) as server:
            agent = Agent(
                name="Assistant",
                mcp_servers=[server]
            )

            result = await Runner.run(agent, "List tasks")
            print(result.final_output)

    except ConnectionError as e:
        print(f"Failed to connect to MCP server: {e}")
    except TimeoutError as e:
        print(f"MCP server timeout: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

**Common errors**:
- `ConnectionError`: Server not reachable
- `TimeoutError`: Server response too slow
- `ToolExecutionError`: Tool call failed
- `AuthenticationError`: Invalid credentials

---

## Environment Configuration

Use environment variables for MCP configuration.

```python
import os
from agents import Agent, HostedMCPTool

# .env file:
# MCP_SERVER_URL=https://your-server.com
# MCP_SERVER_LABEL=task_server

agent = Agent(
    name="Assistant",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": os.getenv("MCP_SERVER_LABEL"),
                "server_url": os.getenv("MCP_SERVER_URL"),
                "require_approval": "never"
            }
        )
    ]
)
```

**Best practices**:
- Never hardcode credentials
- Use environment variables
- Different configs for dev/staging/prod
- Document required environment variables

---

## MCP Server Lifecycle

Proper server lifecycle management.

```python
async def create_agent_with_mcp():
    """Factory function for agent with MCP server."""
    server = await MCPServerStdio(
        name="Task Server",
        params={"command": "python", "args": ["mcp_server.py"]}
    ).__aenter__()

    agent = Agent(name="Assistant", mcp_servers=[server])
    return agent, server

async def cleanup_mcp(server):
    """Cleanup MCP server."""
    await server.__aexit__(None, None, None)

# Usage
agent, server = await create_agent_with_mcp()
try:
    result = await Runner.run(agent, "List tasks")
finally:
    await cleanup_mcp(server)
```

**Lifecycle stages**:
1. **Initialization**: Create server instance
2. **Connection**: Establish connection
3. **Tool discovery**: Load available tools
4. **Usage**: Agent calls tools
5. **Cleanup**: Close connection

---

## FastAPI Integration with MCP

Integrate MCP servers in FastAPI application.

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from agents import Agent
from agents.mcp import MCPServerStdio

# Global MCP server
mcp_server = None
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP server lifecycle."""
    global mcp_server, agent

    # Startup: Initialize MCP server
    mcp_server = await MCPServerStdio(
        name="Task Server",
        params={"command": "python", "args": ["mcp_server.py"]}
    ).__aenter__()

    agent = Agent(
        name="Task Manager",
        instructions="Use MCP tools to manage tasks.",
        mcp_servers=[mcp_server]
    )

    yield

    # Shutdown: Cleanup MCP server
    await mcp_server.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)

@app.post("/api/chat")
async def chat(message: str):
    result = await Runner.run(agent, message)
    return {"response": result.final_output}
```

**Benefits**:
- Single MCP server instance
- Shared across all requests
- Proper startup/shutdown
- Resource efficient

---

## Testing MCP Integration

Test agent with MCP tools.

```python
import pytest
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

@pytest.mark.asyncio
async def test_agent_with_mcp():
    """Test agent can use MCP tools."""
    async with MCPServerStdio(
        name="Test Server",
        params={"command": "python", "args": ["test_mcp_server.py"]}
    ) as server:
        agent = Agent(
            name="Test Agent",
            mcp_servers=[server]
        )

        result = await Runner.run(agent, "Add task: Test task")

        assert "created" in result.final_output.lower()
        assert len(result.new_items) > 0
```

**Testing strategies**:
- Use test MCP server
- Mock MCP responses
- Test error handling
- Verify tool calls
- Check agent responses

---

## Production Checklist

Before deploying MCP integration:

- [ ] Environment variables configured
- [ ] Authentication implemented
- [ ] Error handling added
- [ ] Timeouts configured
- [ ] Retry logic implemented
- [ ] Logging enabled
- [ ] Server lifecycle managed
- [ ] Connection pooling (if HTTP)
- [ ] Health checks implemented
- [ ] Monitoring configured
