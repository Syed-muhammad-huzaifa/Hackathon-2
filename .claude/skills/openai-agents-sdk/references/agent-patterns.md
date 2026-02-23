# Agent Patterns

Complete patterns for defining and configuring OpenAI agents.

---

## Basic Agent Definition

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)
```

**Required fields**:
- `name`: Agent identifier (used in logs, handoffs)
- `instructions`: System prompt defining agent behavior

---

## Agent with Model Configuration

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="Task Manager",
    instructions="You help users manage tasks through natural language.",
    model="gpt-4o",  # or "gpt-5-nano", "gpt-4o-mini"
    model_settings=ModelSettings(
        temperature=0.7,
        tool_choice="auto"  # "auto", "required", "none"
    )
)
```

**Model options**:
- `gpt-4o`: Default, balanced performance
- `gpt-5-nano`: Fast, lightweight
- `gpt-4o-mini`: Cost-effective

**ModelSettings options**:
- `temperature`: 0.0-2.0 (default: 1.0)
- `tool_choice`: "auto" | "required" | "none"
- `max_tokens`: Maximum response length
- `top_p`: Nucleus sampling parameter

---

## Agent with Function Tools

```python
from agents import Agent, function_tool

@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

@function_tool
def calculate(expression: str) -> float:
    """Evaluates a mathematical expression."""
    return eval(expression)

agent = Agent(
    name="Assistant",
    instructions="Use tools to answer questions accurately.",
    tools=[get_weather, calculate]
)
```

**Function tool requirements**:
- Use `@function_tool` decorator
- Include docstring (becomes tool description)
- Type hints required for parameters
- Return type hint recommended

---

## Agent with Built-in Tools

```python
from agents import Agent, FileSearchTool, WebSearchTool

agent = Agent(
    name="Research Assistant",
    instructions="Help users research topics using web and file search.",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"]
        )
    ]
)
```

**Built-in tools**:
- `WebSearchTool()`: Web search capability
- `FileSearchTool()`: Search uploaded files/vector stores
- `CodeInterpreterTool()`: Execute Python code

---

## Agent with MCP Servers

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
        name="Task Manager",
        instructions="Use MCP tools to manage tasks.",
        mcp_servers=[server]
    )
```

See `mcp-integration.md` for complete MCP patterns.

---

## Agent with Handoffs

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Specialized agent
billing_agent = Agent(
    name="Billing Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle billing questions.",
    handoff_description="Manages billing inquiries and payment issues"
)

# Triage agent
triage_agent = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route to appropriate agent.",
    handoffs=[billing_agent]
)
```

**Handoff best practices**:
- Use `RECOMMENDED_PROMPT_PREFIX` in instructions
- Provide clear `handoff_description` for specialized agents
- Triage agent should have routing logic in instructions

See `handoffs.md` for advanced patterns.

---

## Agent Configuration Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent identifier |
| `instructions` | str | Required | System prompt |
| `model` | str | "gpt-4o" | Model to use |
| `model_settings` | ModelSettings | None | Model parameters |
| `tools` | list | [] | Function tools |
| `mcp_servers` | list | [] | MCP server instances |
| `handoffs` | list | [] | Other agents for delegation |
| `handoff_description` | str | None | Description for handoff tool |

---

## Instructions Best Practices

### Good Instructions

```python
instructions = """You are a task management assistant.

Your role:
- Help users create, update, and manage tasks
- Use natural language to understand task operations
- Confirm actions before executing
- Provide clear, concise responses

When users mention adding/creating tasks, use add_task tool.
When users ask to see tasks, use list_tasks tool.
When users mark tasks complete, use complete_task tool."""
```

**Why it works**:
- Clear role definition
- Specific behaviors listed
- Tool usage guidance
- Concise and actionable

### Bad Instructions

```python
instructions = "You help with tasks."
```

**Why it fails**:
- Too vague
- No tool guidance
- No behavior specification

---

## Model Selection Guide

| Use Case | Recommended Model | Reasoning |
|----------|-------------------|-----------|
| Production chatbot | gpt-4o | Balanced performance/cost |
| High-volume simple tasks | gpt-5-nano | Fast, cost-effective |
| Complex reasoning | gpt-4o | Better reasoning capability |
| Budget-conscious | gpt-4o-mini | Lower cost |

---

## Temperature Guidelines

| Temperature | Use Case | Example |
|-------------|----------|---------|
| 0.0-0.3 | Deterministic, factual | Data extraction, classification |
| 0.4-0.7 | Balanced | General chatbot, task management |
| 0.8-1.2 | Creative | Content generation, brainstorming |
| 1.3-2.0 | Very creative | Experimental, artistic |

---

## Tool Choice Strategies

| Setting | Behavior | Use Case |
|---------|----------|----------|
| `"auto"` | Model decides | General purpose (default) |
| `"required"` | Must use tool | Force tool usage |
| `"none"` | No tools | Pure conversation |

```python
# Force tool usage
agent = Agent(
    name="Calculator",
    instructions="Always use the calculate tool.",
    tools=[calculate],
    model_settings=ModelSettings(tool_choice="required")
)
```

---

## Complete Example: Production Agent

```python
from agents import Agent, ModelSettings, function_tool
from agents.mcp import MCPServerStreamableHttp
import os

# Define custom tools
@function_tool
def validate_input(text: str) -> dict:
    """Validates user input for safety."""
    return {"valid": len(text) < 1000, "reason": "Length check"}

# MCP server setup
async def create_agent():
    async with MCPServerStreamableHttp(
        name="Task API",
        params={
            "url": os.getenv("MCP_SERVER_URL"),
            "headers": {"Authorization": f"Bearer {os.getenv('MCP_TOKEN')}"},
            "timeout": 10
        },
        cache_tools_list=True
    ) as server:
        agent = Agent(
            name="Production Task Manager",
            instructions="""You are a professional task management assistant.

            Your responsibilities:
            - Help users manage their tasks efficiently
            - Use MCP tools for all task operations
            - Validate inputs before processing
            - Provide clear confirmations
            - Handle errors gracefully

            Always confirm task operations with the user.""",
            model="gpt-4o",
            model_settings=ModelSettings(
                temperature=0.7,
                tool_choice="auto",
                max_tokens=500
            ),
            tools=[validate_input],
            mcp_servers=[server]
        )
        return agent
```
