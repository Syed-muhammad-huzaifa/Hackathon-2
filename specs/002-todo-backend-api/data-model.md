# Data Model: Backend API for Task Management

**Feature**: 002-todo-backend-api
**Date**: 2026-02-16
**Purpose**: Define database entities, relationships, validation rules, and state transitions

## Overview

This document defines the data model for the Task Management API. The model enforces multi-tenancy through user_id relationships and supports all CRUD operations defined in the specification.

## Entities

### Task

**Description**: Represents a unit of work to be completed by a user. Each task belongs to exactly one user and contains descriptive information, status tracking, and timestamps.

**Database Table**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique task identifier |
| user_id | VARCHAR(255) | NOT NULL, INDEX | Owner's user identifier from Better Auth |
| title | VARCHAR(500) | NOT NULL | Task title (max 500 characters) |
| description | TEXT | NULLABLE | Detailed task description (optional) |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'pending' | Task status: 'pending', 'in_progress', 'completed', 'deleted' |
| priority | VARCHAR(50) | NULLABLE, DEFAULT 'medium' | Task priority: 'low', 'medium', 'high' (optional) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes**:
- PRIMARY KEY: `id`
- COMPOSITE INDEX: `(user_id, created_at DESC)` - Optimizes user task list queries
- COMPOSITE INDEX: `(user_id, status)` - Optimizes filtered queries by status
- INDEX: `user_id` - Enforces multi-tenancy filtering

**Validation Rules**:

1. **Title Validation**:
   - MUST NOT be empty or whitespace-only
   - MUST be between 1 and 500 characters
   - Trimmed of leading/trailing whitespace

2. **Description Validation**:
   - Optional field (can be NULL or empty)
   - Maximum length: 10,000 characters (prevents abuse)
   - Trimmed of leading/trailing whitespace

3. **Status Validation**:
   - MUST be one of: 'pending', 'in_progress', 'completed', 'deleted'
   - Default: 'pending'
   - Cannot transition from 'deleted' to any other status

4. **Priority Validation**:
   - MUST be one of: 'low', 'medium', 'high', or NULL
   - Default: 'medium'

5. **User ID Validation**:
   - MUST NOT be empty
   - MUST match authenticated user's ID for all operations
   - Format: String (matches Better Auth user ID format)

**State Transitions**:

```
pending → in_progress → completed
   ↓           ↓            ↓
deleted ← ← ← ← ← ← ← ← ← ←
```

**Allowed Transitions**:
- `pending` → `in_progress`, `completed`, `deleted`
- `in_progress` → `pending`, `completed`, `deleted`
- `completed` → `pending`, `in_progress`, `deleted`
- `deleted` → (no transitions allowed - terminal state)

**Business Rules**:

1. **Multi-tenancy Enforcement**:
   - ALL queries MUST include `WHERE user_id = :authenticated_user_id`
   - Users can ONLY access their own tasks
   - Attempting to access another user's task returns 404 (not 403) to prevent existence leakage

2. **Soft Delete**:
   - Deletion sets `status = 'deleted'` (soft delete)
   - Deleted tasks excluded from default list queries
   - Deleted tasks cannot be updated (business rule enforced in service layer)

3. **Timestamps**:
   - `created_at` set on insert, never modified
   - `updated_at` automatically updated on every modification

4. **Immutable Fields**:
   - `id` - Cannot be changed after creation
   - `user_id` - Cannot be changed after creation (task ownership is permanent)
   - `created_at` - Cannot be changed after creation

---

### User (Reference Only)

**Description**: Represents an authenticated user. This entity is managed by Better Auth and is NOT stored in the backend database. The backend only references user_id from JWT tokens.

**Source**: Better Auth authentication service

**Referenced Fields**:
- `user_id` (string) - Unique user identifier from Better Auth JWT payload
- `email` (string) - User email from JWT payload (for logging/debugging only)

**Note**: The backend does NOT manage user registration, authentication, or profile data. All user management is handled by Better Auth.

---

## Relationships

### Task → User (Many-to-One)

- **Relationship**: Each Task belongs to exactly one User
- **Foreign Key**: `tasks.user_id` references User (external to this database)
- **Cardinality**: Many Tasks : One User
- **Enforcement**: Application-level (user_id validated against JWT token)
- **Cascade**: Not applicable (users managed externally)

**Query Pattern**:
```sql
-- Get all tasks for a user
SELECT * FROM tasks
WHERE user_id = :user_id
  AND status != 'deleted'
ORDER BY created_at DESC;

-- Get a specific task for a user
SELECT * FROM tasks
WHERE id = :task_id
  AND user_id = :user_id;
```

---

### SQLModel Implementation

### Task Model

```python
# app/models/task.py
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, field_validator

class Task(SQLModel, table=True):
    """
    Task database model.

    Represents a user's task with multi-tenancy enforcement.
    All queries MUST filter by user_id.

    @spec: specs/002-todo-backend-api/spec.md (FR-002, FR-010)
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    user_id: str = Field(nullable=False, index=True, max_length=255)
    title: str = Field(nullable=False, max_length=500)
    description: Optional[str] = Field(default=None, nullable=True)
    status: str = Field(default="pending", nullable=False, max_length=50)
    priority: Optional[str] = Field(default="medium", nullable=True, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-abc-123",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "status": "in_progress",
                "priority": "high",
                "created_at": "2026-02-16T10:00:00Z",
                "updated_at": "2026-02-16T14:30:00Z"
            }
        }


# Pydantic Schemas for API

class TaskCreateRequest(BaseModel):
    """
    Schema for creating a new task.

    @spec: specs/002-todo-backend-api/spec.md (FR-004)
    """
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=10000, description="Task description")
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$", description="Task priority")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None


class TaskUpdateRequest(BaseModel):
    """
    Schema for updating an existing task.

    @spec: specs/002-todo-backend-api/spec.md (FR-005)
    """
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|deleted)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace")
            return v
        return None


class TaskResponse(BaseModel):
    """
    Schema for task response.

    @spec: specs/002-todo-backend-api/spec.md (FR-003, FR-009)
    """
    id: UUID
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """
    Schema for task list response.

    @spec: specs/002-todo-backend-api/spec.md (FR-003)
    """
    status: str = "success"
    data: list[TaskResponse]
    meta: dict = Field(default_factory=lambda: {"total": 0})


class TaskSingleResponse(BaseModel):
    """
    Schema for single task response.

    @spec: specs/002-todo-backend-api/spec.md (FR-003, FR-004, FR-005)
    """
    status: str = "success"
    data: TaskResponse
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    @spec: specs/002-todo-backend-api/spec.md (FR-009)
    """
    status: str = "error"
    code: str
    message: str
    details: Optional[dict] = None
```

---

## Schema Creation

### SQLModel Auto-Create on Startup

Tables are automatically created when the FastAPI application starts using SQLModel's `create_all()` method.

**Implementation** (app/main.py):

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.database import engine
from app.models.task import Task  # Import to register with metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    Creates database tables on startup.

    @spec: specs/002-todo-backend-api/spec.md (FR-010)
    """
    # Startup: Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Shutdown: Dispose engine
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

**SQL Generated** (PostgreSQL):

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(50) DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Composite index for user task list queries
CREATE INDEX IF NOT EXISTS idx_tasks_user_created
ON tasks (user_id, created_at DESC);

-- Composite index for filtered queries
CREATE INDEX IF NOT EXISTS idx_tasks_user_status
ON tasks (user_id, status);

-- Single column index for user_id
CREATE INDEX IF NOT EXISTS idx_tasks_user_id
ON tasks (user_id);
```

**Note**: Schema changes require application restart. For production environments with existing data, consider implementing a migration strategy for controlled schema versioning.

---

## Summary

**Entities**: 1 (Task)
**Relationships**: 1 (Task → User, many-to-one, external reference)
**Indexes**: 3 (primary key + 2 composite indexes for multi-tenancy queries)
**Validation Rules**: 5 (title, description, status, priority, user_id)
**State Transitions**: 4 states with defined transition rules

**Multi-tenancy Enforcement**:
- ✅ All queries include user_id filter
- ✅ Composite indexes start with user_id for performance
- ✅ Application-level validation in repository layer
- ✅ 404 responses for non-owned resources (prevents existence leakage)

**Constitution Compliance**:
- ✅ Spec-First: All fields traced to spec requirements
- ✅ N-Tier: Clear separation between SQLModel (data), Pydantic (API), and business logic
- ✅ Multi-tenancy: user_id mandatory on all operations
- ✅ Type Safety: 100% type hints on all models and schemas
