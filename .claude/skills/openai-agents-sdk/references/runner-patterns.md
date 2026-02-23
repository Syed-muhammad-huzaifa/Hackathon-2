# Runner Patterns

Complete patterns for executing agents with sync and async runners.

---

## Basic Async Execution

```python
import asyncio
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)

async def main():
    result = await Runner.run(agent, "What is the capital of France?")
    print(result.final_output)
    # Output: Paris is the capital of France.

asyncio.run(main())
```

**Use async when**:
- FastAPI/web applications
- Multiple concurrent operations
- I/O-bound operations
- Production applications

---

## Basic Sync Execution

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."
)

result = Runner.run_sync(agent, "What is 2 + 2?")
print(result.final_output)
# Output: 4
```

**Use sync when**:
- Scripts and CLI tools
- Jupyter notebooks
- Simple testing
- Synchronous codebases

---

## Result Object

Both runners return a result object with useful information.

```python
result = await Runner.run(agent, "Hello")

# Access response
print(result.final_output)  # Final agent response

# Access metadata
print(f"New items: {len(result.new_items)}")  # Messages, tool calls
print(f"Last response ID: {result.last_response_id}")  # Response ID
print(f"Last agent: {result.last_agent.name}")  # Which agent responded
```

**Result attributes**:
- `final_output`: Final text response from agent
- `new_items`: List of new messages/tool calls
- `last_response_id`: ID of last response
- `last_agent`: Agent that provided final response

---

## With Session (Conversation Memory)

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant", instructions="Reply concisely.")
session = SQLiteSession("conversation_123")

# First turn
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# Second turn - agent remembers context
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"
```

**Session benefits**:
- Automatic conversation history
- Context preservation
- Multi-turn conversations
- Persistent memory

See `session-management.md` for details.

---

## Max Turns Limit

Limit the number of agent turns to prevent infinite loops.

```python
# Limit to 5 turns
result = await Runner.run(
    agent,
    "Complex task that might loop",
    max_turns=5
)

# Also works with sync
result = Runner.run_sync(agent, "Task", max_turns=3)
```

**When to use**:
- Prevent infinite tool call loops
- Control execution time
- Budget API costs
- Testing and debugging

**Default**: No limit (agent runs until completion)

---

## Error Handling

Handle errors during agent execution.

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are helpful.")

async def main():
    try:
        result = await Runner.run(agent, "Hello")
        print(result.final_output)

    except TimeoutError as e:
        print(f"Agent execution timed out: {e}")

    except Exception as e:
        print(f"Agent error: {e}")
        # Log error, retry, or handle gracefully

asyncio.run(main())
```

**Common errors**:
- `TimeoutError`: Execution took too long
- `APIError`: OpenAI API error
- `ToolExecutionError`: Tool call failed
- `ValidationError`: Invalid input

---

## Streaming Responses

Stream agent responses as they're generated.

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful.")

async def stream_example():
    async for chunk in Runner.stream(agent, "Write a short story"):
        print(chunk, end="", flush=True)

asyncio.run(stream_example())
```

**Benefits**:
- Real-time feedback
- Better UX for long responses
- Lower perceived latency
- Progressive rendering

---

## Multiple Concurrent Runs

Execute multiple agent runs concurrently.

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Reply concisely.")

async def main():
    # Run multiple queries concurrently
    results = await asyncio.gather(
        Runner.run(agent, "What is 2+2?"),
        Runner.run(agent, "What is 3+3?"),
        Runner.run(agent, "What is 4+4?")
    )

    for result in results:
        print(result.final_output)

asyncio.run(main())
```

**Use cases**:
- Batch processing
- Parallel queries
- Performance optimization
- Load testing

---

## With Custom Context

Pass additional context to agent runs.

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="Use provided context to answer questions."
)

# Add context to the message
message = """Context: User is a premium subscriber.
Question: What features do I have access to?"""

result = await Runner.run(agent, message)
print(result.final_output)
```

**Context strategies**:
- Prepend to message
- Use session for persistent context
- Store in database, retrieve per request
- Include in agent instructions

---

## Jupyter Notebook Usage

Special pattern for Jupyter notebooks with existing event loop.

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful.")

# In Jupyter, use await directly (no asyncio.run)
result = await Runner.run(agent, "Hello")  # type: ignore
print(result.final_output)
```

**Why different**:
- Jupyter has running event loop
- `asyncio.run()` creates new loop (error)
- Use `await` directly in notebook cells

---

## FastAPI Integration

Recommended pattern for FastAPI endpoints.

```python
from fastapi import FastAPI
from agents import Agent, Runner, SQLiteSession

app = FastAPI()
agent = Agent(name="Assistant", instructions="Be helpful.")

@app.post("/chat")
async def chat(message: str, session_id: str):
    session = SQLiteSession(session_id)
    result = await Runner.run(agent, message, session=session)
    return {"response": result.final_output}
```

**Best practices**:
- Always use async endpoints
- Use `await Runner.run()` (not sync)
- Load session per request
- Return structured responses

See `fastapi-integration.md` for complete patterns.

---

## Testing Patterns

Test agent execution in unit tests.

```python
import pytest
from agents import Agent, Runner

@pytest.mark.asyncio
async def test_agent_response():
    agent = Agent(name="Test", instructions="Reply with 'OK'")
    result = await Runner.run(agent, "Hello")
    assert "OK" in result.final_output

def test_agent_sync():
    agent = Agent(name="Test", instructions="Reply with 'OK'")
    result = Runner.run_sync(agent, "Hello")
    assert "OK" in result.final_output
```

**Testing strategies**:
- Use `@pytest.mark.asyncio` for async tests
- Mock expensive operations
- Test error handling
- Verify tool calls
- Check response format

---

## Performance Optimization

Optimize agent execution performance.

```python
from agents import Agent, Runner, ModelSettings

# Use faster model for simple tasks
agent = Agent(
    name="Fast Assistant",
    instructions="Reply concisely.",
    model="gpt-5-nano",  # Faster, cheaper
    model_settings=ModelSettings(
        max_tokens=100,  # Limit response length
        temperature=0.3  # More deterministic
    )
)

# Limit turns to prevent long executions
result = await Runner.run(agent, "Quick question", max_turns=2)
```

**Optimization strategies**:
- Use appropriate model (nano for simple tasks)
- Limit max_tokens
- Set max_turns
- Cache sessions
- Use connection pooling

---

## Timeout Configuration

Set timeouts for agent execution.

```python
import asyncio
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="Be helpful.")

async def main():
    try:
        # Set timeout using asyncio
        result = await asyncio.wait_for(
            Runner.run(agent, "Complex task"),
            timeout=30.0  # 30 seconds
        )
        print(result.final_output)

    except asyncio.TimeoutError:
        print("Agent execution timed out after 30 seconds")

asyncio.run(main())
```

**Timeout strategies**:
- Set reasonable timeouts (30-60s)
- Handle timeout gracefully
- Log timeout events
- Retry with higher timeout if needed

---

## Logging and Monitoring

Add logging to agent execution.

```python
import logging
from agents import Agent, Runner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = Agent(name="Assistant", instructions="Be helpful.")

async def main():
    logger.info("Starting agent execution")

    result = await Runner.run(agent, "Hello")

    logger.info(f"Agent response: {result.final_output}")
    logger.info(f"New items: {len(result.new_items)}")
    logger.info(f"Response ID: {result.last_response_id}")

asyncio.run(main())
```

**What to log**:
- Execution start/end
- Input messages
- Response summaries
- Tool calls
- Errors and exceptions
- Performance metrics

---

## Production Checklist

Before deploying runner code:

- [ ] Use async execution for web apps
- [ ] Set max_turns limit
- [ ] Implement error handling
- [ ] Add timeout configuration
- [ ] Enable logging
- [ ] Use sessions for conversations
- [ ] Test error scenarios
- [ ] Monitor performance
- [ ] Handle rate limits
- [ ] Implement retry logic
