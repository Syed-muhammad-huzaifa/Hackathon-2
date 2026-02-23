# Production Patterns

Best practices for deploying MCP task servers in production.

---

## Error Handling

### Comprehensive Error Handling

```python
from mcp.types import TextContent
import json
import logging

logger = logging.getLogger(__name__)

async def safe_tool_handler(arguments: dict) -> list[TextContent]:
    """Tool handler with comprehensive error handling."""
    try:
        # Validate inputs
        if not arguments.get("user_id"):
            return error_response("user_id is required", "VALIDATION_ERROR")

        # Perform operation
        result = await perform_operation(arguments)

        return success_response(result)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return error_response(str(e), "VALIDATION_ERROR")

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        return error_response("Database unavailable", "CONNECTION_ERROR")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return error_response("Internal server error", "INTERNAL_ERROR")

def success_response(data: dict) -> list[TextContent]:
    """Create success response."""
    return [TextContent(type="text", text=json.dumps(data))]

def error_response(message: str, code: str) -> list[TextContent]:
    """Create error response."""
    return [TextContent(
        type="text",
        text=json.dumps({"error": message, "code": code})
    )]
```

---

## Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured JSON logger for MCP tools."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_tool_call(self, tool_name: str, user_id: str, arguments: dict):
        """Log tool call."""
        self.logger.info(json.dumps({
            "event": "tool_call",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "user_id": user_id,
            "arguments": arguments
        }))

    def log_tool_result(self, tool_name: str, user_id: str, success: bool, duration: float):
        """Log tool result."""
        self.logger.info(json.dumps({
            "event": "tool_result",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "user_id": user_id,
            "success": success,
            "duration_seconds": duration
        }))

    def log_error(self, tool_name: str, error: str, error_type: str):
        """Log error."""
        self.logger.error(json.dumps({
            "event": "tool_error",
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "error": error,
            "error_type": error_type
        }))

# Usage
logger = StructuredLogger(__name__)

async def add_task_handler(arguments: dict) -> list[TextContent]:
    start_time = time.time()
    logger.log_tool_call("add_task", arguments["user_id"], arguments)

    try:
        result = await create_task(arguments)
        duration = time.time() - start_time
        logger.log_tool_result("add_task", arguments["user_id"], True, duration)
        return success_response(result)

    except Exception as e:
        logger.log_error("add_task", str(e), type(e).__name__)
        return error_response(str(e), "ERROR")
```

---

## Database Connection Management

### Connection Pooling

```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

### Connection Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlmodel import Session

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_db_session():
    """Get database session with retry."""
    return Session(engine)
```

---

## Input Validation

### Validation Helpers

```python
def validate_user_id(user_id: str) -> bool:
    """Validate user ID format."""
    if not user_id or not isinstance(user_id, str):
        return False
    if len(user_id) > 100:
        return False
    return True

def validate_task_title(title: str) -> tuple[bool, str]:
    """Validate task title."""
    if not title or not isinstance(title, str):
        return False, "Title is required"

    title = title.strip()
    if len(title) == 0:
        return False, "Title cannot be empty"

    if len(title) > 500:
        return False, "Title too long (max 500 characters)"

    return True, ""

# Usage in handler
async def add_task_handler(arguments: dict) -> list[TextContent]:
    user_id = arguments.get("user_id")
    if not validate_user_id(user_id):
        return error_response("Invalid user_id", "VALIDATION_ERROR")

    title = arguments.get("title")
    valid, error_msg = validate_task_title(title)
    if not valid:
        return error_response(error_msg, "VALIDATION_ERROR")

    # Proceed with task creation
    # ...
```

---

## Rate Limiting

### Per-User Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(self, user_id: str) -> tuple[bool, str]:
        """Check if user is within rate limit."""
        async with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_seconds)

            # Clean old requests
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > cutoff
            ]

            # Check limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False, f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s"

            # Record request
            self.requests[user_id].append(now)
            return True, ""

# Global rate limiter
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

# Use in handlers
async def add_task_handler(arguments: dict) -> list[TextContent]:
    user_id = arguments["user_id"]

    # Check rate limit
    allowed, error_msg = await rate_limiter.check_rate_limit(user_id)
    if not allowed:
        return error_response(error_msg, "RATE_LIMIT_EXCEEDED")

    # Proceed with operation
    # ...
```

---

## Monitoring

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
tool_calls_total = Counter(
    "mcp_tool_calls_total",
    "Total number of tool calls",
    ["tool_name", "status"]
)

tool_duration_seconds = Histogram(
    "mcp_tool_duration_seconds",
    "Tool call duration in seconds",
    ["tool_name"]
)

active_connections = Gauge(
    "mcp_active_connections",
    "Number of active database connections"
)

# Use in handlers
async def add_task_handler(arguments: dict) -> list[TextContent]:
    with tool_duration_seconds.labels(tool_name="add_task").time():
        try:
            result = await create_task(arguments)
            tool_calls_total.labels(tool_name="add_task", status="success").inc()
            return success_response(result)

        except Exception as e:
            tool_calls_total.labels(tool_name="add_task", status="error").inc()
            return error_response(str(e), "ERROR")
```

---

## Security

### SQL Injection Prevention

SQLModel/SQLAlchemy automatically prevents SQL injection:

```python
# Safe - parameterized query
statement = select(Task).where(Task.user_id == user_id)

# Never do this - vulnerable to SQL injection
# statement = f"SELECT * FROM tasks WHERE user_id = '{user_id}'"
```

### Input Sanitization

```python
import html

def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    # Remove leading/trailing whitespace
    text = text.strip()

    # Escape HTML
    text = html.escape(text)

    # Limit length
    if len(text) > 10000:
        text = text[:10000]

    return text

# Use in handlers
async def add_task_handler(arguments: dict) -> list[TextContent]:
    title = sanitize_input(arguments["title"])
    description = sanitize_input(arguments.get("description", ""))

    # Proceed with task creation
    # ...
```

---

## Testing

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel

@pytest.fixture
def test_engine():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def client(test_engine):
    """Create test client."""
    return TestClient(app)

def test_add_task(client):
    """Test add_task tool."""
    response = client.post("/mcp/tools/add_task", json={
        "user_id": "test_user",
        "title": "Test task"
    })

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "created"

def test_list_tasks(client):
    """Test list_tasks tool."""
    # Create test tasks
    client.post("/mcp/tools/add_task", json={
        "user_id": "test_user",
        "title": "Task 1"
    })

    # List tasks
    response = client.post("/mcp/tools/list_tasks", json={
        "user_id": "test_user",
        "status": "all"
    })

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1
```

---

## Performance Optimization

### Database Query Optimization

```python
# Use indexes
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Index for fast lookups
    completed: bool = Field(default=False, index=True)  # Index for filtering

# Limit query results
statement = select(Task).where(Task.user_id == user_id).limit(100)

# Use pagination
def list_tasks_paginated(user_id: str, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(page_size)
    return session.exec(statement).all()
```

### Caching

```python
from functools import lru_cache
from cachetools import TTLCache
import hashlib

# Response cache
response_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes

def cache_key(user_id: str, status: str) -> str:
    """Generate cache key."""
    return hashlib.md5(f"{user_id}:{status}".encode()).hexdigest()

async def list_tasks_handler(arguments: dict) -> list[TextContent]:
    """List tasks with caching."""
    user_id = arguments["user_id"]
    status = arguments.get("status", "all")

    # Check cache
    key = cache_key(user_id, status)
    if key in response_cache:
        return response_cache[key]

    # Query database
    tasks = await get_tasks(user_id, status)
    result = success_response(tasks)

    # Cache result
    response_cache[key] = result

    return result
```

---

## Deployment Checklist

Before deploying to production:

### Infrastructure
- [ ] Database connection string configured
- [ ] Connection pooling enabled
- [ ] SSL/TLS configured for database
- [ ] Environment variables set
- [ ] Secrets management configured

### Security
- [ ] Authentication implemented
- [ ] Rate limiting enabled
- [ ] Input validation added
- [ ] SQL injection prevention verified
- [ ] CORS configured properly

### Monitoring
- [ ] Logging configured
- [ ] Metrics collection enabled
- [ ] Health check endpoint working
- [ ] Alerting configured
- [ ] Error tracking set up

### Performance
- [ ] Database indexes created
- [ ] Connection pooling configured
- [ ] Query optimization done
- [ ] Caching implemented
- [ ] Load testing completed

### Reliability
- [ ] Error handling comprehensive
- [ ] Retry logic implemented
- [ ] Graceful shutdown configured
- [ ] Backup strategy defined
- [ ] Disaster recovery plan documented
