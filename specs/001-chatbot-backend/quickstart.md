# Quickstart Guide: AI Chatbot Backend

**Feature**: 001-chatbot-backend
**Date**: 2026-02-21
**Audience**: Developers setting up local development environment

---

## Prerequisites

- Python 3.12+
- PostgreSQL (or Neon Serverless PostgreSQL account)
- OpenAI API key
- Phase 2 backend running (for task repository access)
- Better Auth frontend deployed (for JWT verification)

---

## Environment Setup

### 1. Install Dependencies

```bash
# Navigate to Phase-3 directory
cd Phase-3

# Initialize uv project named "backend"
uv init backend

# Navigate to backend directory
cd backend

# Install project dependencies
uv add fastapi sqlmodel psycopg[binary] psycopg[pool] pyjwt httpx uvicorn openai

# Install dev dependencies
uv add --dev pytest pytest-asyncio httpx ruff mypy
```

### 2. Configure Environment Variables

Create `.env` file in `Phase-3/backend/`:

```bash
# Database (same as Phase 2)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Better Auth (JWT verification)
BETTER_AUTH_URL=https://phase3-frontend.vercel.app
BETTER_AUTH_SECRET=your-shared-secret-with-frontend

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# CORS (Phase 3 frontend URL)
ALLOWED_ORIGINS=https://phase3-frontend.vercel.app,http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

**Important**: `BETTER_AUTH_SECRET` must match Phase 2 and Phase 3 frontend.

### 3. Database Tables

Tables are created automatically on server startup via SQLModel:

```python
# app/main.py includes:
@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**No manual migration needed** - tables created when you start the server.

---

## Running Locally

### Start Development Server

```bash
# From Phase-3/backend directory
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Output:
# ✓ Database tables created/verified
# INFO: Uvicorn running on http://0.0.0.0:8000

# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Verify Server Health

```bash
# Liveness check
curl http://localhost:8000/health/live
# Expected: {"status": "ok"}

# Readiness check
curl http://localhost:8000/health/ready
# Expected: {"status": "ready", "database": "connected", "openai": "accessible"}

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: conversations, messages (plus Phase 2 tables: tasks, user, etc.)
```

---

## Testing the Chat Endpoint

### 1. Get JWT Token

Sign in via Phase 3 frontend to obtain JWT token, or use Better Auth API directly:

```bash
# Sign in via Better Auth
curl -X POST https://phase3-frontend.vercel.app/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Extract JWT token from response
# Token will be in response body or Set-Cookie header
```

### 2. Send Chat Message

```bash
# Start new conversation
curl -X POST http://localhost:8000/api/YOUR_USER_ID/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "✓ Task added: Buy groceries",
#   "tool_calls": [
#     {
#       "tool": "add_task",
#       "parameters": {"user_id": "...", "title": "Buy groceries"},
#       "result": {"task_id": 5, "status": "created", "title": "Buy groceries"}
#     }
#   ]
# }
```

### 3. Continue Conversation

```bash
# Use conversation_id from previous response
curl -X POST http://localhost:8000/api/YOUR_USER_ID/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "What tasks do I have?"
  }'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "You have 1 pending task:\n1. Buy groceries",
#   "tool_calls": [
#     {
#       "tool": "list_tasks",
#       "parameters": {"user_id": "...", "status": "pending"},
#       "result": [{"id": 5, "title": "Buy groceries", "completed": false}]
#     }
#   ]
# }
```

---

## Project Structure

```
Phase-3/backend/
├── app/
│   ├── main.py                      # FastAPI app entry point
│   ├── core/
│   │   ├── config.py                # Settings (env vars)
│   │   ├── auth.py                  # JWT verification
│   │   └── database.py              # Async DB session
│   ├── models/
│   │   ├── conversation.py          # SQLModel: Conversation
│   │   └── message.py               # SQLModel: Message
│   ├── schemas/
│   │   ├── chat.py                  # Pydantic: Request/Response
│   │   └── mcp.py                   # Pydantic: MCP tool schemas
│   ├── repositories/
│   │   ├── conversation_repository.py
│   │   └── message_repository.py
│   ├── services/
│   │   └── chat_service.py          # AI agent orchestration
│   ├── mcp/
│   │   ├── server.py                # MCP server init
│   │   └── tools/                   # 5 MCP tools
│   └── api/
│       └── v1/
│           ├── chat.py              # Chat endpoint
│           └── health.py            # Health checks
├── tests/
│   ├── contract/                    # API contract tests
│   ├── integration/                 # End-to-end tests
│   └── unit/                        # Unit tests
├── alembic/
│   └── versions/                    # Database migrations
├── pyproject.toml                   # Dependencies
├── .env                             # Environment variables
└── README.md                        # Documentation
```

---

## Development Workflow

### 1. Make Changes

Edit code in `app/` directory following N-Tier architecture:
- **Routes** (`api/v1/`): HTTP handling, JWT verification
- **Services** (`services/`): Business logic, AI agent orchestration
- **Repositories** (`repositories/`): Database operations
- **MCP Tools** (`mcp/tools/`): Tool implementations

### 2. Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/integration/test_chat_flow.py

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

### 3. Add Dependencies

```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update dependencies
uv sync
```

### 4. Code Quality

```bash
# Format code
uv run ruff format app/

# Lint code
uv run ruff check app/

# Type check
uv run mypy app/
```

---

## Common Issues

### Issue: "Failed to fetch JWKS"

**Cause**: `BETTER_AUTH_URL` incorrect or frontend not deployed

**Solution**:
1. Verify `BETTER_AUTH_URL` in `.env` matches Phase 3 frontend URL
2. Test JWKS endpoint: `curl https://phase3-frontend.vercel.app/api/auth/jwks`
3. Ensure frontend is deployed and accessible

### Issue: "OpenAI API error"

**Cause**: Invalid API key or rate limit exceeded

**Solution**:
1. Verify `OPENAI_API_KEY` in `.env`
2. Check OpenAI dashboard for quota/usage
3. Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### Issue: "Database connection failed"

**Cause**: Invalid `DATABASE_URL` or database not accessible

**Solution**:
1. Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
2. Test connection: `psql $DATABASE_URL -c "SELECT 1"`
3. Check Neon dashboard if using Neon Serverless

### Issue: "Task not found" when using MCP tools

**Cause**: Phase 2 task repository not accessible or user_id mismatch

**Solution**:
1. Verify Phase 2 backend is running and accessible
2. Check user_id in JWT matches path parameter
3. Verify task exists: Query Phase 2 database directly

### Issue: "Tables not created on startup"

**Cause**: SQLModel models not imported or database connection failed

**Solution**:
1. Verify models imported in `app/main.py`: `from app.models.conversation import Conversation`
2. Check database connection in startup logs
3. Verify `DATABASE_URL` is correct
4. Check server logs for SQLModel errors

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Next Steps

1. **Implement Backend**: Run `/sp.tasks` to generate implementation tasks
2. **Write Tests**: Follow TDD approach (Red-Green-Refactor)
3. **Deploy**: Deploy to Hugging Face Spaces or similar platform
4. **Integrate Frontend**: Connect Phase 3 frontend to backend API

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/chat-api.yaml](./contracts/chat-api.yaml)
- **MCP Tools**: [contracts/mcp-tools.yaml](./contracts/mcp-tools.yaml)
- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
- **Official MCP SDK**: https://modelcontextprotocol.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/

---

## Support

For issues or questions:
1. Check [spec.md](./spec.md) for requirements
2. Review [plan.md](./plan.md) for architecture decisions
3. Consult [research.md](./research.md) for technical patterns
4. Open GitHub issue with detailed description
