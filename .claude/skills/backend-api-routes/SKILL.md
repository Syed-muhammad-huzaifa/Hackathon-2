# Backend API Routes Skill

**Purpose**: Guidance for creating FastAPI route handlers following project patterns and requirements.

## Overview

All API routes MUST be organized under `/api/` prefix, use dependency injection for database sessions, validate requests/responses with Pydantic models, and enforce user isolation through JWT middleware.

## Key Patterns

### 1. Route Structure and Organization

**File Location**: `/backend/routes/auth.py` and `/backend/routes/tasks.py`

**Pattern**: Routes organized by resource, all under `/api/` prefix

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter(prefix="/api", tags=["tasks"])

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Route implementation
    pass
```

**Pattern Rules**:
- All routes MUST use `APIRouter` with `/api` prefix
- Use `tags` parameter for OpenAPI documentation grouping
- Routes MUST use dependency injection for database sessions
- Routes MUST use JWT verification dependency for protected endpoints

### 2. Dependency Injection for Database Sessions

**Pattern**: Use FastAPI dependency injection for database sessions

```python
from fastapi import Depends
from sqlmodel import Session
from backend.db import get_db

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    db: Session = Depends(get_db)
):
    # Use db session here
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return {"success": True, "data": tasks}
```

**Pattern Rules**:
- Always use `Depends(get_db)` for database session
- Session is automatically closed after request
- Use type hints: `Session = Depends(get_db)`

### 3. JWT Token Verification Dependency

**Pattern**: Use dependency injection for JWT verification and user extraction

```python
from fastapi import Depends, HTTPException, status
from backend.middleware.jwt import verify_jwt_token

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Verify user_id matches JWT token user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )
    # Route implementation
    pass
```

**Pattern Rules**:
- All protected routes MUST use `Depends(verify_jwt_token)`
- MUST verify `user_id` from JWT matches URL path `user_id`
- Return 403 Forbidden if user_id mismatch
- `current_user` dict contains: `{"user_id": str, "email": str}`

### 4. Request/Response Validation with Pydantic

**Pattern**: Use Pydantic models for request/response validation

```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"  # 'low'|'medium'|'high'
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[datetime]
    tags: Optional[List[str]]
    completed: bool
    created_at: datetime
    updated_at: datetime

@router.post("/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Create task using service layer
    task = task_service.create_task(db, user_id, task_data)
    return {"success": True, "data": task}
```

**Pattern Rules**:
- All request bodies MUST use Pydantic models
- All responses MUST use `response_model` parameter
- Use type hints and Optional for optional fields
- Validate enum values (priority: 'low'|'medium'|'high')

### 5. HTTP Status Codes

**Pattern**: Use appropriate HTTP status codes

```python
from fastapi import HTTPException, status

# Success responses
return {"success": True, "data": result}  # 200 OK (default)

# Created response
return {"success": True, "data": created_item}  # 201 Created
# Use status_code=201 in decorator: @router.post(..., status_code=201)

# Error responses
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,  # Validation error
    detail="Invalid input data"
)

raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,  # Authentication error
    detail="Invalid or missing JWT token"
)

raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,  # Authorization error
    detail="User ID mismatch"
)

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,  # Resource not found
    detail="Task not found"
)

raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  # Server error
    detail="Internal server error"
)
```

**Pattern Rules**:
- Use `status.HTTP_*` constants from FastAPI
- 200 OK for successful GET, PUT, PATCH, DELETE
- 201 Created for successful POST (creation)
- 400 Bad Request for validation errors
- 401 Unauthorized for authentication failures
- 403 Forbidden for authorization failures (user mismatch)
- 404 Not Found for missing resources
- 500 Internal Server Error for unexpected errors

### 6. Query Parameters Handling

**Pattern**: Use Pydantic models or FastAPI Query for query parameters

```python
from fastapi import Query
from typing import Optional

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    status: Optional[str] = Query(None, regex="^(all|pending|completed)$"),
    sort: Optional[str] = Query(None, regex="^(created|title|updated|priority|due_date)$"),
    search: Optional[str] = Query(None, max_length=200),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    due_date: Optional[str] = Query(None, regex="^\\d{4}-\\d{2}-\\d{2}$"),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    page: Optional[int] = Query(1, ge=1),
    limit: Optional[int] = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Parse tags if provided
    tag_list = tags.split(",") if tags else None
    
    # Use service layer for query
    result = task_service.get_tasks(
        db, user_id,
        status=status, sort=sort, search=search,
        priority=priority, due_date=due_date,
        tags=tag_list, page=page, limit=limit
    )
    return {"success": True, "data": result.data, "meta": result.meta}
```

**Pattern Rules**:
- Use `Query()` for query parameters with validation
- Use `regex` for enum validation
- Use `ge`, `le` for numeric range validation
- Provide default values (page=1, limit=20)
- Parse comma-separated values (tags) manually

### 7. Path Parameters

**Pattern**: Extract path parameters from URL

```python
@router.get("/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Get task with user isolation
    task = task_service.get_task_by_id(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"success": True, "data": task}
```

**Pattern Rules**:
- Path parameters are automatically extracted
- Use type hints (task_id: int) for type conversion
- Always validate user_id matches JWT token

### 8. File Upload (Import)

**Pattern**: Handle file uploads for import functionality

```python
from fastapi import UploadFile, File

@router.post("/{user_id}/tasks/import")
async def import_tasks(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Validate file type
    if file.content_type not in ["text/csv", "application/json"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV and JSON are supported"
        )
    
    # Read file content
    content = await file.read()
    
    # Use service layer for import
    result = task_service.import_tasks(db, user_id, content, file.filename)
    return {"success": True, "data": result}
```

**Pattern Rules**:
- Use `UploadFile = File(...)` for file uploads
- Validate file content type
- Read file content with `await file.read()`
- Pass to service layer for processing

### 9. File Download (Export)

**Pattern**: Return file download response

```python
from fastapi.responses import Response

@router.get("/{user_id}/tasks/export")
async def export_tasks(
    user_id: str,
    format: str = Query(..., regex="^(csv|json)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Use service layer for export
    file_content = task_service.export_tasks(db, user_id, format)
    
    # Determine content type and filename
    content_type = "text/csv" if format == "csv" else "application/json"
    filename = f"tasks_export.{format}"
    
    return Response(
        content=file_content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Pattern Rules**:
- Use `Response` from `fastapi.responses`
- Set appropriate `media_type`
- Set `Content-Disposition` header for file download
- Generate filename with format extension

### 10. Service Layer Integration

**Pattern**: Routes delegate to service layer for business logic

```python
from backend.services.task_service import TaskService

task_service = TaskService()

@router.post("/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Validate user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Delegate to service layer
    task = task_service.create_task(db, user_id, task_data)
    
    return {"success": True, "data": task}
```

**Pattern Rules**:
- Routes handle HTTP concerns (validation, status codes, responses)
- Service layer handles business logic
- Always pass `db` session and `user_id` to service methods
- Service methods return domain objects, routes format responses

### 11. Error Handling in Routes

**Pattern**: Handle errors consistently

```python
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

@router.post("/{user_id}/tasks")
async def create_task(
    user_id: str,
    task_data: TaskCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    try:
        # Validate user_id
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="User ID mismatch")
        
        # Delegate to service
        task = task_service.create_task(db, user_id, task_data)
        return {"success": True, "data": task}
    
    except ValueError as e:
        # Validation errors from service layer
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        # Database constraint violations
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except Exception as e:
        # Unexpected errors
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Pattern Rules**:
- Catch specific exceptions (ValueError, IntegrityError)
- Rollback database session on errors
- Return appropriate HTTP status codes
- Log unexpected errors (use logging module)

### 12. Response Format Standardization

**Pattern**: All responses follow consistent format

```python
# Success response
{
    "success": True,
    "data": <response_data>
}

# Success response with metadata (pagination)
{
    "success": True,
    "data": [<items>],
    "meta": {
        "total": 100,
        "page": 1,
        "limit": 20,
        "totalPages": 5
    }
}

# Error response (from HTTPException)
{
    "detail": "Error message"
}
```

**Pattern Rules**:
- All success responses include `"success": True`
- Data in `"data"` field
- Pagination metadata in `"meta"` field
- Errors use HTTPException which returns `{"detail": "message"}`

## Steps for Adding New API Endpoint

1. **Define Pydantic Models** (in `/backend/schemas/requests.py` and `responses.py`)
   - Create request model for request body
   - Create response model for response data

2. **Add Route Handler** (in `/backend/routes/` appropriate file)
   - Use `@router.get/post/put/patch/delete()` decorator
   - Add path parameters and query parameters
   - Add dependencies: `db: Session = Depends(get_db)`
   - Add JWT verification: `current_user: dict = Depends(verify_jwt_token)`
   - Validate user_id matches JWT token
   - Delegate to service layer

3. **Implement Service Method** (in `/backend/services/`)
   - Add business logic method
   - Handle database operations
   - Return domain objects

4. **Register Route** (in `/backend/main.py`)
   - Import router
   - Include router in FastAPI app: `app.include_router(router)`

5. **Add Tests** (in `/backend/tests/api/`)
   - Test successful cases
   - Test error cases (401, 403, 404, 400)
   - Test user isolation

### 13. Statistics Endpoint

**Pattern**: Get task statistics for user

```python
@router.get("/{user_id}/tasks/statistics")
async def get_statistics(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    """Get task statistics (total, completed, pending, overdue)"""
    # Verify user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Get statistics from service
    stats = task_service.get_statistics(db, user_id)
    
    return {
        "success": True,
        "data": {
            "total": stats["total"],
            "completed": stats["completed"],
            "pending": stats["pending"],
            "overdue": stats["overdue"]
        }
    }
```

**Pattern Rules**:
- Verify user_id matches JWT token
- Delegate to service layer
- Return statistics in consistent format

### 14. Bulk Operations Endpoint

**Pattern**: Perform bulk operations on tasks

```python
from backend.schemas.requests import BulkOperationRequest

@router.post("/{user_id}/tasks/bulk")
async def bulk_operations(
    user_id: str,
    bulk_data: BulkOperationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    """Perform bulk operations (delete, complete, pending, priority)"""
    # Verify user_id
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    
    # Validate action
    if bulk_data.action not in ["delete", "complete", "pending", "priority"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    # Validate priority if action is priority
    if bulk_data.action == "priority" and bulk_data.priority not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid priority value")
    
    # Perform bulk operation
    affected = task_service.bulk_operations(
        db,
        user_id,
        bulk_data.action,
        bulk_data.task_ids,
        priority=bulk_data.priority if bulk_data.action == "priority" else None
    )
    
    return {
        "success": True,
        "data": {
            "affected": affected
        }
    }
```

**Pattern Rules**:
- Verify user_id matches JWT token
- Validate action parameter
- Validate priority if action is priority
- Use transactions for atomic operations
- Return count of affected items

### 15. CORS Middleware Configuration

**Pattern**: Configure CORS for frontend integration

```python
# In main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Get CORS origins from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Pattern Rules**:
- Use FastAPI CORSMiddleware
- Get origins from CORS_ORIGINS environment variable
- Allow credentials for JWT cookies (if used)
- Allow all methods and headers for flexibility
- Configure per environment (development/production)

### 16. Rate Limiting Middleware

**Pattern**: Implement rate limiting to prevent abuse

```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request

# Create limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.get("/{user_id}/tasks")
@limiter.limit("100/minute")  # 100 requests per minute
async def get_tasks(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_jwt_token)
):
    # Route implementation
    pass
```

**Pattern Rules**:
- Use slowapi for rate limiting
- Configure limits per endpoint
- Use IP address for rate limit key
- Return 429 Too Many Requests when exceeded
- Configure different limits for different endpoints

### 17. Request Logging Middleware

**Pattern**: Log all requests and security events

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = datetime.utcnow()
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"User: {request.headers.get('Authorization', 'No token')[:20]}..."
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        # Log security events
        if response.status_code == 401:
            logger.warning(
                f"Security Event: Unauthorized access attempt - "
                f"Path: {request.url.path} - "
                f"IP: {request.client.host}"
            )
        elif response.status_code == 403:
            logger.warning(
                f"Security Event: Forbidden access attempt - "
                f"Path: {request.url.path} - "
                f"IP: {request.client.host}"
            )
        
        return response

# Add to app
app.add_middleware(RequestLoggingMiddleware)
```

**Pattern Rules**:
- Log all incoming requests
- Log response status and processing time
- Log security events (401, 403)
- Include IP address for security events
- Use appropriate log levels (INFO, WARNING)
- Don't log sensitive data (passwords, tokens)

## Common Patterns Summary

- ✅ All routes under `/api/` prefix
- ✅ Use dependency injection for database sessions
- ✅ Use JWT verification dependency for protected routes
- ✅ Validate user_id matches JWT token (403 if mismatch)
- ✅ Use Pydantic models for request/response validation
- ✅ Use appropriate HTTP status codes
- ✅ Delegate business logic to service layer
- ✅ Return consistent response format
- ✅ Handle errors with HTTPException
- ✅ Use type hints throughout
- ✅ Configure CORS middleware
- ✅ Implement rate limiting
- ✅ Add request logging middleware

