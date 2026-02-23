# Tool Implementation

Complete implementation patterns for all 5 MCP task management tools.

---

## Tool Handler Structure

MCP tool handlers receive arguments and return TextContent responses:

```python
from mcp.types import TextContent
import json

async def tool_handler(arguments: dict) -> list[TextContent]:
    """Handle tool call."""
    try:
        # Extract arguments
        # Perform operation
        # Return result
        return [TextContent(
            type="text",
            text=json.dumps(result)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]
```

---

## Tool 1: add_task Implementation

```python
from mcp.types import TextContent
from sqlmodel import Session
from models import Task, engine
import json

async def add_task_handler(arguments: dict) -> list[TextContent]:
    """Create a new task."""
    try:
        user_id = arguments["user_id"]
        title = arguments["title"]
        description = arguments.get("description")

        # Validate input
        if not title.strip():
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Title cannot be empty",
                    "code": "VALIDATION_ERROR"
                })
            )]

        # Create task in database
        with Session(engine) as session:
            task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            # Return success response
            return [TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task.id,
                    "status": "created",
                    "title": task.title
                })
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "code": "DATABASE_ERROR"
            })
        )]
```

---

## Tool 2: list_tasks Implementation

```python
from sqlmodel import select

async def list_tasks_handler(arguments: dict) -> list[TextContent]:
    """List tasks for a user."""
    try:
        user_id = arguments["user_id"]
        status = arguments.get("status", "all")

        with Session(engine) as session:
            # Build query
            statement = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            # Order by creation date (newest first)
            statement = statement.order_by(Task.created_at.desc())

            # Execute query
            tasks = session.exec(statement).all()

            # Format response
            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            return [TextContent(
                type="text",
                text=json.dumps(task_list)
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "code": "DATABASE_ERROR"
            })
        )]
```

---

## Tool 3: complete_task Implementation

```python
from datetime import datetime

async def complete_task_handler(arguments: dict) -> list[TextContent]:
    """Mark a task as completed."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]

        with Session(engine) as session:
            # Find task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = session.exec(statement).first()

            # Check if task exists
            if not task:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Task not found",
                        "code": "TASK_NOT_FOUND"
                    })
                )]

            # Update task
            task.completed = True
            task.updated_at = datetime.now()
            session.add(task)
            session.commit()
            session.refresh(task)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task.id,
                    "status": "completed",
                    "title": task.title
                })
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "code": "DATABASE_ERROR"
            })
        )]
```

---

## Tool 4: delete_task Implementation

```python
async def delete_task_handler(arguments: dict) -> list[TextContent]:
    """Delete a task."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]

        with Session(engine) as session:
            # Find task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = session.exec(statement).first()

            # Check if task exists
            if not task:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Task not found",
                        "code": "TASK_NOT_FOUND"
                    })
                )]

            # Store task info before deletion
            task_info = {
                "task_id": task.id,
                "status": "deleted",
                "title": task.title
            }

            # Delete task
            session.delete(task)
            session.commit()

            return [TextContent(
                type="text",
                text=json.dumps(task_info)
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "code": "DATABASE_ERROR"
            })
        )]
```

---

## Tool 5: update_task Implementation

```python
async def update_task_handler(arguments: dict) -> list[TextContent]:
    """Update a task's title or description."""
    try:
        user_id = arguments["user_id"]
        task_id = arguments["task_id"]
        new_title = arguments.get("title")
        new_description = arguments.get("description")

        # Validate at least one field to update
        if new_title is None and new_description is None:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Must provide title or description to update",
                    "code": "VALIDATION_ERROR"
                })
            )]

        with Session(engine) as session:
            # Find task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            task = session.exec(statement).first()

            # Check if task exists
            if not task:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Task not found",
                        "code": "TASK_NOT_FOUND"
                    })
                )]

            # Update fields
            if new_title is not None:
                if not new_title.strip():
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "Title cannot be empty",
                            "code": "VALIDATION_ERROR"
                        })
                    )]
                task.title = new_title.strip()

            if new_description is not None:
                task.description = new_description

            task.updated_at = datetime.now()
            session.add(task)
            session.commit()
            session.refresh(task)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "task_id": task.id,
                    "status": "updated",
                    "title": task.title
                })
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "code": "DATABASE_ERROR"
            })
        )]
```

---

## Complete Tool Router

```python
from mcp.server import Server
from mcp.types import TextContent

server = Server("task-server")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handlers."""

    handlers = {
        "add_task": add_task_handler,
        "list_tasks": list_tasks_handler,
        "complete_task": complete_task_handler,
        "delete_task": delete_task_handler,
        "update_task": update_task_handler
    }

    handler = handlers.get(name)
    if not handler:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Unknown tool: {name}",
                "code": "UNKNOWN_TOOL"
            })
        )]

    return await handler(arguments)
```

---

## Error Handling Patterns

### Database Connection Errors

```python
async def safe_handler(arguments: dict) -> list[TextContent]:
    """Handler with connection error handling."""
    try:
        with Session(engine) as session:
            # Database operations
            pass
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Database connection failed",
                "code": "CONNECTION_ERROR",
                "details": str(e)
            })
        )]
```

### Validation Errors

```python
async def validated_handler(arguments: dict) -> list[TextContent]:
    """Handler with input validation."""
    # Validate required fields
    if "user_id" not in arguments:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "user_id is required",
                "code": "VALIDATION_ERROR"
            })
        )]

    # Validate field types
    if not isinstance(arguments.get("task_id"), int):
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "task_id must be an integer",
                "code": "VALIDATION_ERROR"
            })
        )]

    # Proceed with operation
    # ...
```

---

## Testing Tool Handlers

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel

@pytest.fixture
def test_engine():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.mark.asyncio
async def test_add_task(test_engine):
    """Test add_task handler."""
    arguments = {
        "user_id": "test_user",
        "title": "Test task",
        "description": "Test description"
    }

    result = await add_task_handler(arguments)
    response = json.loads(result[0].text)

    assert "task_id" in response
    assert response["status"] == "created"
    assert response["title"] == "Test task"

@pytest.mark.asyncio
async def test_list_tasks(test_engine):
    """Test list_tasks handler."""
    # Create test tasks first
    await add_task_handler({"user_id": "test_user", "title": "Task 1"})
    await add_task_handler({"user_id": "test_user", "title": "Task 2"})

    # List tasks
    result = await list_tasks_handler({"user_id": "test_user", "status": "all"})
    tasks = json.loads(result[0].text)

    assert len(tasks) == 2
    assert tasks[0]["title"] in ["Task 1", "Task 2"]
```

---

## Best Practices

### Stateless Design

- Each tool call is independent
- No server-side state between calls
- All state stored in database
- Tools can be called in any order

### Error Handling

- Always return TextContent (never raise exceptions)
- Use consistent error format
- Include error codes for programmatic handling
- Log errors for debugging

### Database Operations

- Use context managers (with Session)
- Commit after successful operations
- Refresh objects after commit
- Handle connection errors gracefully

### Response Format

- Always return JSON strings
- Use consistent structure
- Include relevant metadata
- Keep responses concise
