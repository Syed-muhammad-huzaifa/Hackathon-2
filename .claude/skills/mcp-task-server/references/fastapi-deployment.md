# FastAPI Deployment

Deploy MCP server as FastAPI HTTP endpoint.

---

## Basic FastAPI Integration

Mount MCP server at `/mcp` endpoint:

```python
from fastapi import FastAPI
from mcp.server import Server
from mcp.server.fastapi import MCPServerFastAPI

# Create MCP server
server = Server("task-server")

# Create FastAPI app
app = FastAPI(title="Task MCP Server")

# Mount MCP server
mcp_app = MCPServerFastAPI(server)
app.mount("/mcp", mcp_app)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "server": "task-mcp-server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Complete FastAPI Application

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.server.fastapi import MCPServerFastAPI
from sqlmodel import SQLModel, create_engine
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# MCP server
server = Server("task-server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting MCP server...")

    # Initialize database
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")

    yield

    logger.info("Shutting down MCP server...")

# Create FastAPI app
app = FastAPI(
    title="Task MCP Server",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP server
mcp_app = MCPServerFastAPI(server)
app.mount("/mcp", mcp_app)

# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "task-mcp-server",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Task MCP Server",
        "version": "1.0.0",
        "mcp_endpoint": "/mcp",
        "health_endpoint": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
```

---

## Environment Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    allowed_origins: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Authentication

### Bearer Token Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify bearer token."""
    token = credentials.credentials

    # Verify token (implement your logic)
    if token != os.getenv("MCP_TOKEN"):
        raise HTTPException(status_code=401, detail="Invalid token")

    return token

# Protect MCP endpoint
@app.middleware("http")
async def auth_middleware(request, call_next):
    """Authentication middleware."""
    if request.url.path.startswith("/mcp"):
        # Check authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized"}
            )

    return await call_next(request)
```

---

## Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

---

## Logging

```python
import logging
from fastapi import Request
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({duration:.2f}s)")

    return response
```

---

## Testing

### Test MCP Endpoint

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_mcp_endpoint():
    """Test MCP endpoint is accessible."""
    response = client.get("/mcp")
    assert response.status_code in [200, 405]  # GET may not be allowed

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "mcp_endpoint" in response.json()
```

---

## Docker Deployment

### Dockerfile

```dockerfile
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
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - MCP_TOKEN=${MCP_TOKEN}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Production Deployment

### Gunicorn with Uvicorn Workers

```python
# gunicorn.conf.py
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
```

Run with:
```bash
gunicorn main:app -c gunicorn.conf.py
```

### Systemd Service

```ini
# /etc/systemd/system/mcp-server.service
[Unit]
Description=Task MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mcp-server
Environment="DATABASE_URL=postgresql://..."
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
tool_calls = Counter("mcp_tool_calls_total", "Total tool calls", ["tool_name"])
tool_duration = Histogram("mcp_tool_duration_seconds", "Tool call duration")
tool_errors = Counter("mcp_tool_errors_total", "Total tool errors", ["tool_name"])

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")

# Track metrics in tool handlers
@tool_duration.time()
async def add_task_handler(arguments: dict):
    tool_calls.labels(tool_name="add_task").inc()
    try:
        # Tool logic
        pass
    except Exception as e:
        tool_errors.labels(tool_name="add_task").inc()
        raise
```

---

## Load Balancing

### Nginx Configuration

```nginx
upstream mcp_servers {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Production Checklist

Before deploying:

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] Authentication implemented
- [ ] CORS configured properly
- [ ] Error handling added
- [ ] Logging configured
- [ ] Health check endpoint working
- [ ] Metrics collection enabled
- [ ] Docker image built and tested
- [ ] Load balancing configured
- [ ] SSL/TLS certificates installed
- [ ] Monitoring and alerting set up
