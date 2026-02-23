# Database Models

SQLModel models for task management with Neon PostgreSQL.

---

## Task Model

Complete task model with all required fields.

```python
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for storing user tasks."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, description="User identifier")
    title: str = Field(max_length=500, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False
            }
        }
```

**Field explanations**:
- `id`: Auto-incrementing primary key
- `user_id`: Indexed for fast user-specific queries
- `title`: Required, max 500 characters
- `description`: Optional additional details
- `completed`: Boolean flag for completion status
- `created_at`: Automatically set on creation
- `updated_at`: Updated on every modification

---

## Database Setup

### Neon PostgreSQL Connection

```python
import os
from sqlmodel import create_engine, Session

# Get connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before using
)

# Create tables
def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)
```

### Environment Configuration

```bash
# .env file
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Neon-specific notes**:
- Always use `sslmode=require` for Neon connections
- Connection string format: `postgresql://user:password@host/database?sslmode=require`
- Enable connection pooling for serverless environments

---

## Database Operations

### Create Task

```python
def create_task(user_id: str, title: str, description: str | None = None) -> Task:
    """Create a new task."""
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

### List Tasks

```python
from sqlmodel import select

def list_tasks(user_id: str, status: str = "all") -> list[Task]:
    """List tasks for a user."""
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        statement = statement.order_by(Task.created_at.desc())
        tasks = session.exec(statement).all()
        return list(tasks)
```

### Complete Task

```python
def complete_task(user_id: str, task_id: int) -> Task | None:
    """Mark a task as complete."""
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return None

        task.completed = True
        task.updated_at = datetime.now()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

### Delete Task

```python
def delete_task(user_id: str, task_id: int) -> Task | None:
    """Delete a task."""
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return None

        session.delete(task)
        session.commit()
        return task
```

### Update Task

```python
def update_task(
    user_id: str,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> Task | None:
    """Update a task."""
    with Session(engine) as session:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        task.updated_at = datetime.now()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

---

## Error Handling

### Database Errors

```python
def safe_create_task(user_id: str, title: str, description: str | None = None) -> Task | None:
    """Create task with error handling."""
    try:
        with Session(engine) as session:
            task = Task(user_id=user_id, title=title, description=description)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    except Exception as e:
        print(f"Database error: {e}")
        return None
```

### Connection Retry

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_task_with_retry(user_id: str, title: str, description: str | None = None) -> Task:
    """Create task with automatic retry."""
    return create_task(user_id, title, description)
```

---

## Migrations

### Alembic Setup

```python
# alembic/env.py
from sqlmodel import SQLModel
from models import Task

target_metadata = SQLModel.metadata
```

### Create Migration

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migration
alembic upgrade head
```

---

## Testing

### Test Database Operations

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel

@pytest.fixture
def test_engine():
    """Create test database engine."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

def test_create_task(test_engine):
    """Test task creation."""
    with Session(test_engine) as session:
        task = Task(user_id="test_user", title="Test task")
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.user_id == "test_user"
        assert task.title == "Test task"
        assert task.completed == False
```

---

## Production Checklist

Before deploying:

- [ ] DATABASE_URL configured with Neon connection string
- [ ] SSL mode enabled (sslmode=require)
- [ ] Connection pooling configured
- [ ] Indexes created on user_id
- [ ] Error handling implemented
- [ ] Connection retry logic added
- [ ] Database migrations set up
- [ ] Backup strategy configured
