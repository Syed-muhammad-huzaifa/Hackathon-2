# Handoffs

Multi-agent coordination and delegation patterns.

---

## What Are Handoffs?

Handoffs allow agents to delegate tasks to specialized agents. The agent sees handoffs as tool calls (e.g., `transfer_to_billing_agent`).

**Use cases**:
- Triage systems (route to specialists)
- Domain-specific expertise
- Workflow orchestration
- Escalation patterns

---

## Basic Handoff

Simple agent-to-agent delegation.

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

# Usage
result = await Runner.run(triage_agent, "I have a billing question")
print(f"Final agent: {result.last_agent.name}")  # "Billing Agent"
```

**How it works**:
1. Triage agent receives message
2. Recognizes billing question
3. Calls `transfer_to_billing_agent` tool
4. Billing agent takes over
5. Billing agent responds

---

## RECOMMENDED_PROMPT_PREFIX

Always use this prefix in agent instructions for handoffs.

```python
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

agent = Agent(
    name="Specialist",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a specialist in X. Handle Y tasks."""
)
```

**Why required**:
- Teaches agent handoff protocol
- Ensures proper delegation
- Improves handoff reliability

---

## Multiple Handoffs

Triage agent with multiple specialists.

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Specialized agents
billing_agent = Agent(
    name="Billing Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle billing.",
    handoff_description="Billing inquiries, payments, invoices"
)

technical_agent = Agent(
    name="Technical Support",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Provide technical support.",
    handoff_description="Software issues, bugs, technical problems"
)

account_agent = Agent(
    name="Account Manager",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Manage accounts.",
    handoff_description="Account settings, profile, preferences"
)

# Triage agent
triage_agent = Agent(
    name="Triage",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are the first point of contact. Analyze the request and transfer to:
    - Billing Agent: for payment, invoice, billing questions
    - Technical Support: for software, bugs, technical issues
    - Account Manager: for account settings, profile changes""",
    handoffs=[billing_agent, technical_agent, account_agent]
)
```

---

## Custom Handoff Configuration

Customize handoff tool name and description.

```python
from agents import Agent, handoff

technical_agent = Agent(
    name="Technical Support",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Provide tech support."
)

triage_agent = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route requests.",
    handoffs=[
        handoff(
            agent=technical_agent,
            tool_name_override="escalate_to_tech_support",
            tool_description_override="Escalate technical issues to expert support team"
        )
    ]
)
```

**Customization options**:
- `tool_name_override`: Custom tool name
- `tool_description_override`: Custom tool description
- Helps guide agent decision-making

---

## Handoff with Input Data

Pass structured data during handoff.

```python
from pydantic import BaseModel
from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str
    priority: str
    customer_tier: str

async def on_escalation(ctx: RunContextWrapper, data: EscalationData):
    """Called when escalation happens."""
    print(f"Escalating: {data.reason}")
    print(f"Priority: {data.priority}")
    print(f"Customer tier: {data.customer_tier}")
    # Log to monitoring system, send alerts, etc.

escalation_agent = Agent(
    name="Escalation Handler",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle escalated issues."
)

triage_agent = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route or escalate.",
    handoffs=[
        handoff(
            agent=escalation_agent,
            on_handoff=on_escalation,
            input_type=EscalationData
        )
    ]
)
```

**Use cases**:
- Logging and monitoring
- Analytics tracking
- Alert triggering
- Context passing

---

## Handoff Callbacks

Execute code when handoff occurs.

```python
from agents import Agent, handoff, RunContextWrapper

async def log_handoff(ctx: RunContextWrapper, data: dict):
    """Log handoff event."""
    print(f"Handoff to {ctx.agent.name}")
    print(f"Reason: {data.get('reason', 'N/A')}")
    # Log to database, analytics, etc.

specialist_agent = Agent(
    name="Specialist",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle specialized tasks."
)

triage_agent = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route requests.",
    handoffs=[
        handoff(
            agent=specialist_agent,
            on_handoff=log_handoff
        )
    ]
)
```

**Callback uses**:
- Logging
- Metrics collection
- Notifications
- State updates

---

## Handoff Description Best Practices

Clear descriptions help triage agent make correct decisions.

```python
# Good: Specific, actionable
billing_agent = Agent(
    name="Billing Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle billing.",
    handoff_description="Handles billing inquiries, payment issues, invoice questions, refund requests, and subscription changes"
)

# Bad: Vague
billing_agent = Agent(
    name="Billing Agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle billing.",
    handoff_description="Billing stuff"
)
```

**Good descriptions**:
- List specific capabilities
- Use clear language
- Include examples
- Be comprehensive

---

## Triage Instructions Pattern

Effective triage agent instructions.

```python
triage_agent = Agent(
    name="Customer Support Triage",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

You are the first point of contact for customer support.

Your role:
1. Understand the customer's request
2. Determine which specialist can best help
3. Transfer to the appropriate agent

Transfer guidelines:
- Billing Agent: payments, invoices, refunds, subscriptions
- Technical Support: bugs, errors, software issues, troubleshooting
- Account Manager: profile, settings, preferences, account changes
- Escalation: urgent issues, VIP customers, complex problems

Always be polite and explain the transfer to the customer.""",
    handoffs=[billing_agent, technical_agent, account_agent, escalation_agent]
)
```

**Key elements**:
- Clear role definition
- Transfer guidelines
- Specific routing rules
- Customer communication guidance

---

## Specialist Agent Pattern

Effective specialist agent configuration.

```python
billing_agent = Agent(
    name="Billing Specialist",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

You are a billing specialist with expertise in:
- Payment processing
- Invoice management
- Refund policies
- Subscription changes

Guidelines:
- Be precise about amounts and dates
- Verify customer identity before discussing billing
- Explain charges clearly
- Offer solutions proactively

If you cannot resolve the issue, explain why and suggest next steps.""",
    handoff_description="Handles all billing-related inquiries including payments, invoices, refunds, and subscription management",
    tools=[check_invoice, process_refund, update_subscription]  # Billing-specific tools
)
```

**Specialist best practices**:
- Domain expertise in instructions
- Specific tools for domain
- Clear handoff description
- Escalation guidance

---

## Multi-Level Handoffs

Specialists can handoff to other specialists.

```python
# Level 1: General support
general_support = Agent(
    name="General Support",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Provide general support.",
    handoff_description="General customer support"
)

# Level 2: Specialized support
technical_specialist = Agent(
    name="Technical Specialist",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle technical issues.",
    handoff_description="Advanced technical support",
    handoffs=[general_support]  # Can handoff back if needed
)

# Level 3: Expert support
technical_expert = Agent(
    name="Technical Expert",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Resolve complex technical issues.",
    handoff_description="Expert-level technical support",
    handoffs=[technical_specialist]  # Can handoff back
)

# Triage
triage = Agent(
    name="Triage",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route to appropriate level.",
    handoffs=[general_support, technical_specialist, technical_expert]
)
```

**Use cases**:
- Escalation hierarchies
- Skill-based routing
- Complexity-based delegation

---

## Handoff with MCP Tools

Combine handoffs with MCP tools.

```python
from agents import Agent, HostedMCPTool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# Task specialist with MCP tools
task_agent = Agent(
    name="Task Manager",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Manage tasks using MCP tools.",
    handoff_description="Manages tasks: create, list, update, delete",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "task_server",
                "server_url": "https://task-server.com",
                "require_approval": "never"
            }
        )
    ]
)

# Calendar specialist with MCP tools
calendar_agent = Agent(
    name="Calendar Manager",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Manage calendar using MCP tools.",
    handoff_description="Manages calendar: schedule, view, update events",
    tools=[
        HostedMCPTool(
            tool_config={
                "type": "mcp",
                "server_label": "calendar_server",
                "server_url": "https://calendar-server.com",
                "require_approval": "never"
            }
        )
    ]
)

# Triage
triage = Agent(
    name="Personal Assistant",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Route task requests to Task Manager.
    Route calendar requests to Calendar Manager.""",
    handoffs=[task_agent, calendar_agent]
)
```

**Benefits**:
- Specialized tools per agent
- Clear separation of concerns
- Domain-specific expertise

---

## Testing Handoffs

Test handoff behavior.

```python
import pytest
from agents import Agent, Runner
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

@pytest.mark.asyncio
async def test_handoff_to_specialist():
    """Test triage agent hands off to specialist."""
    specialist = Agent(
        name="Specialist",
        instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle specialized tasks.",
        handoff_description="Specialized task handler"
    )

    triage = Agent(
        name="Triage",
        instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route to specialist.",
        handoffs=[specialist]
    )

    result = await Runner.run(triage, "I need specialized help")

    # Verify handoff occurred
    assert result.last_agent.name == "Specialist"

@pytest.mark.asyncio
async def test_handoff_callback():
    """Test handoff callback is called."""
    callback_called = False

    async def on_handoff(ctx, data):
        nonlocal callback_called
        callback_called = True

    specialist = Agent(name="Specialist", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Help.")

    triage = Agent(
        name="Triage",
        instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route.",
        handoffs=[handoff(agent=specialist, on_handoff=on_handoff)]
    )

    await Runner.run(triage, "Need help")
    assert callback_called
```

---

## Production Patterns

### Pattern 1: Customer Support Triage

```python
# Specialists
billing = Agent(name="Billing", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Handle billing.", handoff_description="Billing and payments")
technical = Agent(name="Technical", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Technical support.", handoff_description="Technical issues")
account = Agent(name="Account", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Account management.", handoff_description="Account settings")

# Triage
support = Agent(
    name="Support",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route customer requests.",
    handoffs=[billing, technical, account]
)
```

### Pattern 2: Task-Based Routing

```python
# Task specialists
task_creator = Agent(name="Task Creator", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Create tasks.", handoff_description="Create new tasks")
task_manager = Agent(name="Task Manager", instructions=f"{RECOMMENDED_PROMPT_PREFIX} Manage tasks.", handoff_description="Update, delete tasks")
task_viewer = Agent(name="Task Viewer", instructions=f"{RECOMMENDED_PROMPT_PREFIX} View tasks.", handoff_description="List, search tasks")

# Router
assistant = Agent(
    name="Assistant",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Route task operations.",
    handoffs=[task_creator, task_manager, task_viewer]
)
```

---

## Production Checklist

Before deploying handoffs:

- [ ] Use RECOMMENDED_PROMPT_PREFIX in all agents
- [ ] Clear handoff descriptions
- [ ] Specific triage instructions
- [ ] Test handoff routing
- [ ] Implement handoff logging
- [ ] Monitor handoff patterns
- [ ] Document agent hierarchy
- [ ] Test edge cases
- [ ] Handle handoff failures
- [ ] Measure handoff accuracy
