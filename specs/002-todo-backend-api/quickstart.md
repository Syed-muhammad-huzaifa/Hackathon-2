# Quickstart Guide: Backend API for Task Management

**Feature**: 002-todo-backend-api
**Date**: 2026-02-16
**Purpose**: Developer setup and getting started guide

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database (Neon Serverless recommended)
- Git
- 'uv' package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Initial Setup

### 1. Clone and Navigate to Backend Directory

```bash
cd Phase-2/backend
```

### 2. Install Dependencies with 'uv'

```bash
# Initialize uv project (if not already done)
uv init

# Install all dependencies
uv sync

# Verify installation
uv run python --version  # Should show Python 3.12+
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# Better Auth Configuration
BETTER_AUTH_SECRET=your-shared-secret-here  # MUST match frontend secret

# Application Configuration
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**Important**: The `BETTER_AUTH_SECRET` MUST be identical to the secret used by the frontend Better Auth configuration.

### 4. Database Setup

#### Option A: Using Neon Serverless PostgreSQL (Recommended)

1. Create a Neon account at https://neon.tech
2. Create a new project and database
3. Copy the connection string (format: `postgresql://user:password@host/dbname`)
4. Update `DATABASE_URL` in `.env` with the Neon connection string
5. Modify for async: `postgresql+psycopg://user:password@host/dbname`

#### Option B: Local PostgreSQL

```bash
# Create database
createdb todo_api_dev

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+psycopg://localhost/todo_api_dev
```

### 5. Database Schema Setup

Tables are automatically created when the FastAPI application starts using SQLModel's `create_all()` method. No manual migration steps required.

The application will create all necessary tables on first startup.

### 6. Start Development Server

```bash
# Run with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at http://localhost:8000
# Tables will be automatically created on first startup
```

### 7. Verify Installation

Open your browser and navigate to:

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health (if implemented)

## Project Structure

```
Phase-2/backend/
├── app/
│   ├── api/                    # Presentation Layer
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   ├── middleware.py       # Auth middleware, error handlers
│   │   └── v1/
│   │       └── tasks.py        # Task CRUD endpoints
│   ├── services/               # Service Layer
│   │   └── task_service.py     # Business logic
│   ├── repositories/           # Repository Layer
│   │   └── task_repository.py  # Data access
│   ├── models/                 # SQLModel entities + Pydantic schemas
│   │   └── task.py             # Task model and schemas
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database connection
│   │   └── auth.py             # JWT verification
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── pyproject.toml              # Project configuration
├── .env                        # Environment variables (not in git)
└── .env.example                # Environment template (in git)
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_task_service.py

# Run integration tests only
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code with ruff
uv run ruff format app/ tests/

# Lint code
uv run ruff check app/ tests/

# Type checking (if using mypy)
uv run mypy app/
```

### Database Schema Management

```bash
# Tables are automatically created on application startup
# To recreate tables (CAUTION: drops all data):
# 1. Drop tables manually in PostgreSQL or via psql
# 2. Restart the application - tables will be recreated

# Verify tables exist
psql $DATABASE_URL -c "\dt"

# View table schema
psql $DATABASE_URL -c "\d tasks"
```

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Sync environment after adding dependencies
uv sync
```

## API Usage Examples

### Authentication

All API requests require a JWT token in the Authorization header:

```bash
# Example with curl
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-123/tasks
```

### Create a Task

```bash
curl -X POST http://localhost:8000/api/user-123/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "priority": "high"
  }'
```

### List Tasks

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-123/tasks
```

### Get Specific Task

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/user-123/tasks/TASK_UUID
```

### Update Task

```bash
curl -X PATCH http://localhost:8000/api/user-123/tasks/TASK_UUID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/user-123/tasks/TASK_UUID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing with JWT Tokens

### Generate Test JWT Token

For local development, you can generate test JWT tokens:

```python
# scripts/generate_test_token.py
import jwt
from datetime import datetime, timedelta

SECRET = "your-better-auth-secret"  # Same as BETTER_AUTH_SECRET in .env

payload = {
    "user_id": "user-123",
    "email": "test@example.com",
    "exp": datetime.utcnow() + timedelta(days=7),
    "iat": datetime.utcnow()
}

token = jwt.encode(payload, SECRET, algorithm="HS256")
print(f"Test JWT Token:\n{token}")
```

Run the script:

```bash
uv run python scripts/generate_test_token.py
```

## Troubleshooting

### Database Connection Issues

**Problem**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
- Verify DATABASE_URL in `.env` is correct
- Check PostgreSQL is running (if local)
- For Neon, verify connection string format: `postgresql+psycopg://...`
- Test connection: `uv run python -c "from app.core.database import engine; print(engine)"`

### JWT Verification Failures

**Problem**: `401 Unauthorized - Invalid token`

**Solution**:
- Verify BETTER_AUTH_SECRET matches frontend configuration
- Check token hasn't expired (exp claim)
- Ensure token format is correct: `Bearer <token>`
- Verify token signature with jwt.io

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
- Ensure you're running commands with `uv run` prefix
- Verify you're in the backend directory
- Run `uv sync` to ensure all dependencies are installed

### Schema Issues

**Problem**: Tables not created or schema out of sync

**Solution**:
```bash
# Restart the application - tables will be auto-created
uv run uvicorn app.main:app --reload

# If tables need to be recreated (CAUTION: drops all data):
# 1. Connect to database and drop tables
psql $DATABASE_URL -c "DROP TABLE IF EXISTS tasks CASCADE;"

# 2. Restart application - tables will be recreated
uv run uvicorn app.main:app --reload
```

## Performance Optimization

### Database Indexes

Ensure proper indexes exist for multi-tenancy queries:

```sql
-- Verify indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'tasks';

-- Should see:
-- idx_tasks_user_created: (user_id, created_at)
-- idx_tasks_user_status: (user_id, status)
```

### Connection Pooling

For production, configure connection pooling in `app/core/database.py`:

```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,          # Max connections in pool
    max_overflow=10,       # Additional connections if pool exhausted
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600      # Recycle connections after 1 hour
)
```

## Next Steps

1. **Implement Routes**: Start with `app/api/v1/tasks.py`
2. **Implement Services**: Add business logic in `app/services/task_service.py`
3. **Implement Repositories**: Add data access in `app/repositories/task_repository.py`
4. **Write Tests**: Follow TDD approach - write tests first
5. **Run Tests**: Verify multi-tenancy and authorization logic
6. **Deploy**: Follow deployment guide for production setup

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Better Auth Documentation**: https://www.better-auth.com/
- **Neon PostgreSQL**: https://neon.tech/docs
- **uv Documentation**: https://github.com/astral-sh/uv

## Support

For issues or questions:
- Check specification: `specs/002-todo-backend-api/spec.md`
- Review architecture: `specs/002-todo-backend-api/plan.md`
- Review research: `specs/002-todo-backend-api/research.md`
- Check API contracts: `specs/002-todo-backend-api/contracts/task-api.yaml`
