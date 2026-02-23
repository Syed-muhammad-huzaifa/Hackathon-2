# Tool Schemas

Complete MCP tool schema definitions for all 5 task management tools.

---

## Tool Schema Structure

MCP tools use JSON Schema for input validation:

```python
{
    "type": "object",
    "properties": {
        "param_name": {"type": "string", "description": "Parameter description"}
    },
    "required": ["param_name"]
}
```

---

## Tool 1: add_task

Create a new task for a user.

```python
{
    "name": "add_task",
    "description": "Create a new task for the user",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "title": {
                "type": "string",
                "description": "Task title",
                "maxLength": 500
            },
            "description": {
                "type": "string",
                "description": "Optional task description"
            }
        },
        "required": ["user_id", "title"]
    }
}
```

**Example input**:
```json
{
    "user_id": "user_123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
}
```

**Example output**:
```json
{
    "task_id": 5,
    "status": "created",
    "title": "Buy groceries"
}
```

---

## Tool 2: list_tasks

Retrieve tasks for a user with optional filtering.

```python
{
    "name": "list_tasks",
    "description": "List tasks for a user with optional status filter",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "status": {
                "type": "string",
                "description": "Filter by status: 'all', 'pending', or 'completed'",
                "enum": ["all", "pending", "completed"],
                "default": "all"
            }
        },
        "required": ["user_id"]
    }
}
```

**Example input**:
```json
{
    "user_id": "user_123",
    "status": "pending"
}
```

**Example output**:
```json
[
    {
        "id": 1,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2024-02-21T10:00:00Z"
    },
    {
        "id": 2,
        "title": "Call mom",
        "description": null,
        "completed": false,
        "created_at": "2024-02-21T11:00:00Z"
    }
]
```

---

## Tool 3: complete_task

Mark a task as completed.

```python
{
    "name": "complete_task",
    "description": "Mark a task as completed",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "task_id": {
                "type": "integer",
                "description": "Task ID to complete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
```

**Example input**:
```json
{
    "user_id": "user_123",
    "task_id": 3
}
```

**Example output**:
```json
{
    "task_id": 3,
    "status": "completed",
    "title": "Call mom"
}
```

---

## Tool 4: delete_task

Remove a task from the list.

```python
{
    "name": "delete_task",
    "description": "Delete a task from the user's list",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "task_id": {
                "type": "integer",
                "description": "Task ID to delete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}
```

**Example input**:
```json
{
    "user_id": "user_123",
    "task_id": 2
}
```

**Example output**:
```json
{
    "task_id": 2,
    "status": "deleted",
    "title": "Old task"
}
```

---

## Tool 5: update_task

Modify task title or description.

```python
{
    "name": "update_task",
    "description": "Update a task's title or description",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "User identifier"
            },
            "task_id": {
                "type": "integer",
                "description": "Task ID to update"
            },
            "title": {
                "type": "string",
                "description": "New task title (optional)",
                "maxLength": 500
            },
            "description": {
                "type": "string",
                "description": "New task description (optional)"
            }
        },
        "required": ["user_id", "task_id"],
        "anyOf": [
            {"required": ["title"]},
            {"required": ["description"]}
        ]
    }
}
```

**Example input**:
```json
{
    "user_id": "user_123",
    "task_id": 1,
    "title": "Buy groceries and fruits"
}
```

**Example output**:
```json
{
    "task_id": 1,
    "status": "updated",
    "title": "Buy groceries and fruits"
}
```

---

## Complete Tool List Definition

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("task-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "title": {"type": "string", "description": "Task title", "maxLength": 500},
                    "description": {"type": "string", "description": "Optional task description"}
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks for a user with optional status filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["all", "pending", "completed"],
                        "default": "all"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to complete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task from the user's list",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to delete"}
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update a task's title or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User identifier"},
                    "task_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New task title", "maxLength": 500},
                    "description": {"type": "string", "description": "New task description"}
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]
```

---

## Schema Validation

### Input Validation

MCP SDK automatically validates inputs against schemas:

```python
# Invalid input (missing required field)
{
    "title": "Buy groceries"
    # Missing user_id - will be rejected
}

# Invalid input (wrong type)
{
    "user_id": "user_123",
    "task_id": "not_a_number"  # Should be integer - will be rejected
}
```

### Custom Validation

Add additional validation in tool handlers:

```python
async def add_task_handler(arguments: dict) -> list[TextContent]:
    """Add task with custom validation."""
    user_id = arguments["user_id"]
    title = arguments["title"]

    # Custom validation
    if len(title.strip()) == 0:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Title cannot be empty"})
        )]

    if len(title) > 500:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Title too long (max 500 characters)"})
        )]

    # Proceed with task creation
    # ...
```

---

## Error Responses

### Standard Error Format

```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

### Common Errors

| Error | Code | When |
|-------|------|------|
| Task not found | TASK_NOT_FOUND | Invalid task_id |
| Invalid user | INVALID_USER | Invalid user_id |
| Validation error | VALIDATION_ERROR | Invalid input |
| Database error | DATABASE_ERROR | Database operation failed |

---

## Best Practices

### Schema Design

- Use descriptive field names
- Include helpful descriptions
- Set appropriate constraints (maxLength, enum)
- Mark required fields explicitly
- Use appropriate types (string, integer, boolean)

### Validation

- Validate at schema level (type, required, enum)
- Add custom validation in handlers
- Return clear error messages
- Include error codes for programmatic handling

### Documentation

- Document expected inputs and outputs
- Provide example requests and responses
- Explain error conditions
- Document any side effects
