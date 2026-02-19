# Research: Backend API for Task Management

**Feature**: 002-todo-backend-api
**Date**: 2026-02-16
**Purpose**: Document architectural decisions, technology patterns, and best practices for implementation

## Overview

This document captures research findings and architectural decisions for the Backend API. All decisions are made in accordance with the constitution principles and feature requirements.

## Architectural Decisions

### 1. JWT Verification with Better Auth

**Decision**: Use JWT token verification with shared secret (BETTER_AUTH_SECRET) between frontend and backend.

**Rationale**:
- Better Auth (frontend) issues JWT tokens signed with BETTER_AUTH_SECRET
- Backend verifies token signature, expiry, and payload integrity using pyjwt library
- Stateless authentication - no session storage required on backend
- Tokens contain user_id claim for multi-tenancy enforcement
- 7-day token validity (configurable)

**Implementation Pattern**:
```python
# app/core/auth.py
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload  # Contains user_id, email, exp, iat
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Alternatives Considered**:
- Session-based auth: Rejected because it requires session storage and doesn't align with Better Auth's JWT approach
- OAuth2 password flow: Rejected because Better Auth handles authentication; backend only verifies tokens

**ADR Required**: Yes - "JWT Token Verification Strategy for Multi-tenant API"

---

### 2. Error Handling Strategy

**Decision**: Use HTTPException in service layer for all error conditions.

**Rationale**:
- Service layer raises FastAPI HTTPException with appropriate status codes
- Consistent with existing Phase-2 backend patterns
- Simple and direct - no need for custom exception mapping
- Service layer controls both business logic and HTTP response codes
- Easier to understand for developers familiar with FastAPI

**Implementation Pattern**:
```python
# app/services/task_service.py
from fastapi import HTTPException, status

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def get_task(self, user_id: str, task_id: str) -> Task:
        task = await self.repository.find_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task

    async def update_task(self, user_id: str, task_id: str, updates: dict) -> Task:
        task = await self.repository.find_by_id(user_id, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Business rule: cannot update deleted tasks
        if task.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update deleted task"
            )

        return await self.repository.update(user_id, task_id, updates)
```

**Alternatives Considered**:
- Domain exceptions with global handlers: Rejected because it adds complexity and doesn't align with existing Phase-2 patterns
- Route-level error handling: Rejected because it couples HTTP concerns to routes and duplicates error logic

**ADR Required**: No - this follows existing Phase-2 backend conventions

---

### 3. Dependency Injection Pattern

**Decision**: Use FastAPI's Depends() with factory functions for service and repository injection.

**Rationale**:
- FastAPI's native dependency injection system
- Enables easy testing with mock dependencies
- Clear dependency graph: Route → Service → Repository → Database Session
- Async-compatible
- No additional DI framework needed

**Implementation Pattern**:
```python
# app/api/dependencies.py
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

def get_task_repository(session: AsyncSession = Depends(get_db_session)) -> TaskRepository:
    return TaskRepository(session)

def get_task_service(repository: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repository)

# app/api/v1/tasks.py
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: dict = Depends(verify_jwt),
    service: TaskService = Depends(get_task_service)
):
    # Verify user_id matches authenticated user
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    tasks = await service.list_tasks(user_id)
    return {"status": "success", "data": tasks}
```

**Alternatives Considered**:
- Manual instantiation in routes: Rejected because it makes testing difficult and couples routes to concrete implementations
- Third-party DI framework (dependency-injector): Rejected because FastAPI's built-in system is sufficient and simpler

**ADR Required**: Yes - "FastAPI Dependency Injection for N-Tier Architecture"

---

## Technology Best Practices

### 4. Async SQLModel with PostgreSQL

**Pattern**: Use SQLModel with async session and psycopg3 async driver.

**Key Practices**:
- All database operations use `await session.exec(statement)`
- Connection pooling configured in database.py
- Async context managers for session lifecycle
- Proper transaction handling with `async with session.begin()`

**Implementation Pattern**:
```python
# app/core/database.py
from sqlmodel.ext.asyncio.session import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg://user:pass@host/db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# app/repositories/task_repository.py
class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_user_id(self, user_id: str) -> list[Task]:
        statement = select(Task).where(Task.user_id == user_id)
        result = await self.session.exec(statement)
        return result.all()
```

**References**:
- SQLModel async documentation: https://sqlmodel.tiangolo.com/advanced/async/
- psycopg3 async driver: https://www.psycopg.org/psycopg3/docs/

---

### 5. Multi-tenancy at Repository Layer

**Pattern**: Enforce user_id filtering in repository methods, not in SQL queries.

**Key Practices**:
- Every repository method accepts user_id as first parameter
- All SELECT queries include `WHERE user_id = :user_id`
- UPDATE/DELETE queries verify user_id before execution
- Return 404 (not 403) for non-owned resources to prevent existence leakage
- Service layer validates path user_id matches authenticated user_id

**Implementation Pattern**:
```python
# app/repositories/task_repository.py
class TaskRepository:
    async def find_by_id(self, user_id: str, task_id: str) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id  # MANDATORY: Always filter by user_id
        )
        result = await self.session.exec(statement)
        return result.first()

    async def update(self, user_id: str, task_id: str, updates: dict) -> Task | None:
        # First verify ownership
        task = await self.find_by_id(user_id, task_id)
        if not task:
            return None  # Will result in 404 from service layer

        # Apply updates
        for key, value in updates.items():
            setattr(task, key, value)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task
```

**Security Verification**:
- Unit tests MUST verify User A cannot access User B's tasks
- Integration tests MUST verify 404 response for non-owned resources
- Code review MUST check every query includes user_id filter

---

### 6. Testing Strategy

**Approach**: Layered testing matching N-Tier architecture.

**Test Categories**:

1. **Unit Tests (Service Layer)**:
   - Test business logic in isolation
   - Mock repository dependencies
   - Verify multi-tenancy logic (user_id validation)
   - Test error conditions (not found, unauthorized)

2. **Integration Tests (API Routes)**:
   - Use FastAPI TestClient
   - Test full request/response cycle
   - Verify authentication and authorization
   - Test cross-user access prevention
   - Use test database with proper setup/teardown

3. **Contract Tests (Schemas)**:
   - Verify Pydantic schema validation
   - Test request/response serialization
   - Ensure API contract compliance

**Implementation Pattern**:
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def auth_token_user_a():
    return create_test_jwt(user_id="user-a")

# tests/integration/test_task_routes.py
def test_user_cannot_access_other_user_tasks(client, auth_token_user_a, auth_token_user_b):
    # User A creates a task
    response = client.post(
        "/api/user-a/tasks",
        headers={"Authorization": f"Bearer {auth_token_user_a}"},
        json={"title": "User A's task"}
    )
    task_id = response.json()["data"]["id"]

    # User B attempts to access User A's task
    response = client.get(
        f"/api/user-a/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token_user_b}"}
    )
    assert response.status_code == 403  # Forbidden - user_id mismatch in path
```

---

## Environment Setup

### 7. 'uv' Dependency Management

**Pattern**: Use 'uv' for all Python dependency management.

**Commands**:
```bash
# Initialize project
uv init

# Add dependencies
uv add fastapi sqlmodel pyjwt psycopg[binary]

# Add dev dependencies
uv add --dev pytest pytest-asyncio httpx

# Sync environment
uv sync

# Run application
uv run uvicorn src.main:app --reload
```

**Configuration** (pyproject.toml):
```toml
[project]
name = "todo-backend-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "sqlmodel>=0.0.14",
    "pyjwt>=2.8.0",
    "psycopg[binary]>=3.1.0",
    "uvicorn[standard]>=0.27.0",
    "python-dotenv>=1.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.26.0",
    "ruff>=0.1.0"
]
```

---

## Database Schema Management

### 8. SQLModel Auto-Create Strategy

**Pattern**: Use SQLModel's `create_all()` method on FastAPI startup to automatically create tables.

**Implementation** (app/main.py):
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.models.task import Task  # Import all models to register with metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Shutdown: Clean up resources
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

**Advantages**:
- Simple setup - no migration files to manage
- Automatic table creation on startup
- Good for development and prototyping
- Schema changes automatically applied on restart

**Considerations**:
- No migration history tracking
- Cannot rollback schema changes
- Schema changes require application restart
- Good for development and small-scale production deployments
- For large production systems with existing data, consider implementing a migration strategy

---

## Summary

All architectural decisions align with constitution principles:
- ✅ N-Tier architecture enforced through dependency injection
- ✅ Multi-tenancy enforced at repository layer with user_id filtering
- ✅ Async-first with SQLModel and psycopg3 async driver
- ✅ JWT verification with Better Auth shared secret
- ✅ Type safety with 100% type hints and Pydantic validation
- ✅ 'uv' for dependency management

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md)
