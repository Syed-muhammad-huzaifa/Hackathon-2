# Production Patterns

Best practices for deploying OpenAI agents in production.

---

## Error Handling

### Comprehensive Error Handling

```python
from agents import Agent, Runner, SQLiteSession
from fastapi import FastAPI, HTTPException
import logging

logger = logging.getLogger(__name__)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with comprehensive error handling."""
    try:
        session = SQLiteSession(request.session_id, "conversations.db")
        result = await Runner.run(
            agent,
            request.message,
            session=session,
            max_turns=10
        )
        return {"response": result.final_output}

    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        raise HTTPException(status_code=504, detail="Request timeout")

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except ConnectionError as e:
        logger.error(f"MCP connection error: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Retry Logic

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def run_agent_with_retry(agent, message, session):
    """Run agent with automatic retry on failure."""
    return await Runner.run(agent, message, session=session)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with retry logic."""
    try:
        session = SQLiteSession(request.session_id, "conversations.db")
        result = await run_agent_with_retry(agent, request.message, session)
        return {"response": result.final_output}
    except Exception as e:
        logger.error(f"Failed after retries: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable")
```

---

## Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured JSON logger."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, user_id: str, message: str, session_id: str):
        """Log incoming request."""
        self.logger.info(json.dumps({
            "event": "chat_request",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "message_length": len(message)
        }))

    def log_response(self, user_id: str, response: str, duration: float, tool_calls: int):
        """Log agent response."""
        self.logger.info(json.dumps({
            "event": "chat_response",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "response_length": len(response),
            "duration_seconds": duration,
            "tool_calls": tool_calls
        }))

    def log_error(self, user_id: str, error: str, error_type: str):
        """Log error."""
        self.logger.error(json.dumps({
            "event": "chat_error",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "error": error,
            "error_type": error_type
        }))

# Usage
logger = StructuredLogger(__name__)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    logger.log_request(request.user_id, request.message, request.session_id)

    try:
        session = SQLiteSession(request.session_id, "conversations.db")
        result = await Runner.run(agent, request.message, session=session)

        duration = time.time() - start_time
        tool_calls = len([i for i in result.new_items if i.get("type") == "tool_call"])
        logger.log_response(request.user_id, result.final_output, duration, tool_calls)

        return {"response": result.final_output}

    except Exception as e:
        logger.log_error(request.user_id, str(e), type(e).__name__)
        raise
```

---

## Monitoring

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
chat_requests = Counter("chat_requests_total", "Total chat requests", ["user_id"])
chat_duration = Histogram("chat_duration_seconds", "Chat request duration")
chat_errors = Counter("chat_errors_total", "Total chat errors", ["error_type"])
tool_calls = Counter("tool_calls_total", "Total tool calls", ["tool_name"])

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with metrics."""
    chat_requests.labels(user_id=request.user_id).inc()

    with chat_duration.time():
        try:
            session = SQLiteSession(request.session_id, "conversations.db")
            result = await Runner.run(agent, request.message, session=session)

            # Track tool calls
            for item in result.new_items:
                if item.get("type") == "tool_call":
                    tool_calls.labels(tool_name=item.get("name", "unknown")).inc()

            return {"response": result.final_output}

        except Exception as e:
            chat_errors.labels(error_type=type(e).__name__).inc()
            raise
```

---

## Security

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str | None = Field(None, max_length=100)

    @validator("message")
    def validate_message(cls, v):
        """Validate message content."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

    @validator("user_id")
    def validate_user_id(cls, v):
        """Validate user ID format."""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Invalid user ID format")
        return v
```

### Rate Limiting

```python
from fastapi import FastAPI, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    async def check_rate_limit(self, user_id: str):
        """Check if user is within rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff
        ]

        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s"
            )

        # Record request
        self.requests[user_id].append(now)

rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with rate limiting."""
    await rate_limiter.check_rate_limit(request.user_id)

    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(agent, request.message, session=session)
    return {"response": result.final_output}
```

### Environment Variables

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # MCP Server
    mcp_server_url: str
    mcp_token: str

    # Database
    database_url: str
    agent_sessions_db: str = "agent_sessions.db"

    # Security
    jwt_secret: str
    allowed_origins: list[str] = ["http://localhost:3000"]

    # Performance
    max_turns: int = 10
    request_timeout: int = 30

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()

# Usage
settings = get_settings()
```

---

## Performance Optimization

### Connection Pooling

```python
from contextlib import asynccontextmanager
from agents.mcp import MCPServerStreamableHttp

# Global connection pool
mcp_server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize connection pool."""
    global mcp_server

    # Create single MCP server instance
    mcp_server = await MCPServerStreamableHttp(
        name="Task Server",
        params={
            "url": settings.mcp_server_url,
            "headers": {"Authorization": f"Bearer {settings.mcp_token}"},
            "timeout": 10
        },
        cache_tools_list=True,  # Cache tool list
        max_retry_attempts=3
    ).__aenter__()

    yield

    await mcp_server.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)
```

### Caching

```python
from functools import lru_cache
from cachetools import TTLCache
import hashlib

# Response cache
response_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes

def cache_key(user_id: str, message: str) -> str:
    """Generate cache key."""
    return hashlib.md5(f"{user_id}:{message}".encode()).hexdigest()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with caching."""
    # Check cache
    key = cache_key(request.user_id, request.message)
    if key in response_cache:
        logger.info("Cache hit")
        return response_cache[key]

    # Run agent
    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(agent, request.message, session=session)

    response = {"response": result.final_output}

    # Cache response
    response_cache[key] = response

    return response
```

---

## Health Checks

### Comprehensive Health Check

```python
from fastapi import FastAPI
from datetime import datetime

@app.get("/health")
async def health():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Check agent
    try:
        if agent:
            health_status["checks"]["agent"] = "healthy"
        else:
            health_status["checks"]["agent"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["agent"] = f"error: {e}"
        health_status["status"] = "unhealthy"

    # Check MCP server
    try:
        if mcp_server:
            health_status["checks"]["mcp_server"] = "healthy"
        else:
            health_status["checks"]["mcp_server"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["mcp_server"] = f"error: {e}"
        health_status["status"] = "unhealthy"

    # Check database
    try:
        session = SQLiteSession("health_check", "conversations.db")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {e}"
        health_status["status"] = "unhealthy"

    return health_status

@app.get("/health/ready")
async def readiness():
    """Readiness check for Kubernetes."""
    if agent and mcp_server:
        return {"status": "ready"}
    return {"status": "not ready"}, 503

@app.get("/health/live")
async def liveness():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}
```

---

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MCP_SERVER_URL=${MCP_SERVER_URL}
      - MCP_TOKEN=${MCP_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./conversations.db:/app/conversations.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-api
  template:
    metadata:
      labels:
        app: agent-api
    spec:
      containers:
      - name: api
        image: agent-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        - name: MCP_SERVER_URL
          valueFrom:
            configMapKeyRef:
              name: agent-config
              key: mcp-server-url
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## Testing

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.integration
def test_chat_flow():
    """Test complete chat flow."""
    # First message
    response1 = client.post(
        "/api/chat",
        json={
            "user_id": "test_user",
            "message": "Add task: Buy groceries"
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert "conversation_id" in data1
    assert "response" in data1

    # Second message with same session
    response2 = client.post(
        "/api/chat",
        json={
            "user_id": "test_user",
            "message": "List my tasks",
            "conversation_id": data1["conversation_id"]
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert "groceries" in data2["response"].lower()

@pytest.mark.integration
def test_error_handling():
    """Test error handling."""
    # Invalid request
    response = client.post(
        "/api/chat",
        json={"user_id": "", "message": ""}
    )
    assert response.status_code == 422  # Validation error
```

---

## Production Checklist

Before deploying to production:

### Infrastructure
- [ ] Environment variables configured
- [ ] Secrets management set up
- [ ] Database backups configured
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Health checks implemented

### Security
- [ ] Authentication implemented
- [ ] Rate limiting enabled
- [ ] Input validation added
- [ ] CORS configured properly
- [ ] HTTPS enabled
- [ ] API keys secured

### Performance
- [ ] Connection pooling configured
- [ ] Caching implemented
- [ ] Timeouts set appropriately
- [ ] Max turns limited
- [ ] Resource limits configured

### Reliability
- [ ] Error handling comprehensive
- [ ] Retry logic implemented
- [ ] Graceful shutdown configured
- [ ] Circuit breakers added
- [ ] Fallback strategies defined

### Observability
- [ ] Structured logging enabled
- [ ] Metrics collection configured
- [ ] Distributed tracing set up
- [ ] Alerting configured
- [ ] Dashboards created

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Load tests completed
- [ ] Error scenarios tested
- [ ] Rollback plan documented
