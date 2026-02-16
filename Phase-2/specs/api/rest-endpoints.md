# REST API Endpoints
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. General Information

### Base URL
- Local development: `http://localhost:8000`
- Production / deployment: `https://api.your-app-domain.com` (Vercel, Render, DigitalOcean, etc.)

### Authentication Requirement
**All endpoints are protected.**

- Header: `Authorization: Bearer <jwt-token>`
- Token is issued by **Better Auth** after successful login/signup
- Backend verifies:
  - Signature using shared secret (`BETTER_AUTH_SECRET`)
  - Expiry
  - Payload contains valid `user_id`
- Every endpoint path includes `{user_id}` → backend **must** enforce that the path `user_id` matches the authenticated JWT's `user_id`

### Response Format (Consistent)

**Success (200/201):**
```json
{
  "status": "success",
  "data": { ... } | [ ... ],
  "message": "optional human-readable success message",
  "meta": { "total": 42, "limit": 20, "offset": 0 }  // optional for paginated responses
}
```

**Error:**
```json
{
  "status": "error",
  "code": "unauthorized | forbidden | not_found | validation_error | server_error",
  "message": "Human-readable explanation",
  "details": { "field": "title", "issue": "too long" }  // optional
}
```

### Common Status Codes

| Code | Meaning | Typical Cases |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 400 | Bad Request | Validation failure, invalid input |
| 401 | Unauthorized | Missing / invalid / expired JWT |
| 403 | Forbidden | Valid JWT, but user_id mismatch |
| 404 | Not Found | Task does not exist or not owned by user |
| 500 | Internal Server Error | Unexpected backend failure (should be rare) |

### Timestamp Format

All dates: ISO 8601 UTC with Z suffix  
Example: "2026-02-11T19:45:23Z"

## 2. Endpoints

### 2.1 List All Tasks
`GET /api/{user_id}/tasks`

#### Path Parameters
- `user_id` (string, required) – Must match JWT's user_id

#### Query Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| status | string | no | all | all, pending, completed |
| sort | string | no | created_desc | created_desc, created_asc, title_asc, title_desc |
| search | string | no | — | Keyword search in title OR description |
| limit | integer | no | 50 | Max items per page (max 100) |
| offset | integer | no | 0 | Pagination offset |

#### Response – 200 OK

```json
{
  "status": "success",
  "data": [
    {
      "id": 42,
      "title": "Prepare Phase II specs",
      "description": "Write architecture.md and endpoints",
      "completed": false,
      "created_at": "2026-02-11T19:45:23Z",
      "updated_at": "2026-02-11T19:45:23Z"
    }
    // ...
  ],
  "meta": {
    "total": 18,
    "limit": 50,
    "offset": 0
  }
}
```

### 2.2 Create New Task
`POST /api/{user_id}/tasks`

#### Path Parameters
- `user_id` (string, required)

#### Request Body (JSON)
```json
{
  "title": "Buy groceries",                  // required, 1–200 chars
  "description": "Milk, eggs, bread"         // optional, max 2000 chars
}
```

#### Response – 201 Created

```json
{
  "status": "success",
  "data": {
    "id": 43,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-11T20:10:00Z",
    "updated_at": "2026-02-11T20:10:00Z"
  },
  "message": "Task created successfully"
}
```

### 2.3 Get Single Task
`GET /api/{user_id}/tasks/{task_id}`

#### Path Parameters
- `user_id` (string)
- `task_id` (integer)

#### Response – 200 OK

```json
{
  "status": "success",
  "data": {
    "id": 43,
    "title": "Buy groceries",
    "description": "...",
    "completed": false,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### 2.4 Update Task
`PUT /api/{user_id}/tasks/{task_id}`

#### Path Parameters
- `user_id` (string)
- `task_id` (integer)

#### Request Body (partial updates allowed)
```json
{
  "title": "Buy groceries and fruits",     // optional
  "description": "Add apples"              // optional
}
```

#### Response – 200 OK

```json
{
  "status": "success",
  "data": { /* updated task object */ },
  "message": "Task updated successfully"
}
```

### 2.5 Delete Task
`DELETE /api/{user_id}/tasks/{task_id}`

#### Response – 200 OK

```json
{
  "status": "success",
  "message": "Task deleted successfully"
}
```

### 2.6 Toggle Task Completion
`PATCH /api/{user_id}/tasks/{task_id}/complete`

#### Path Parameters
- `user_id` (string)
- `task_id` (integer)

#### Request Body (optional – toggle if omitted)
```json
{
  "completed": true     // optional – if missing → toggle current value
}
```

#### Response – 200 OK

```json
{
  "status": "success",
  "data": { /* updated task with new completed status */ },
  "message": "Task completion toggled"
}
```

### 2.7 Get Basic Analytics
`GET /api/{user_id}/analytics`

#### Path Parameters
- `user_id` (string)

#### Response – 200 OK

```json
{
  "status": "success",
  "data": {
    "total_tasks": 42,
    "completed_tasks": 18,
    "pending_tasks": 24,
    "completion_rate": 42.86,
    "tasks_this_week": 7
  }
}
```

## 3. Security & Validation Rules

- JWT Validation: Must be valid, not expired, signature correct
- Ownership Check: path.user_id === jwt.user_id → else 403
- Input Validation:
  - title: required, 1–200 chars
  - description: max 2000 chars
  - completed: boolean

- Rate Limiting: Optional for Phase II (consider adding in Phase V)
- CORS: Allow only frontend origin(s) in production

## Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/database/schema.md - Database schema and relationships
5. @specs/ui/components.md - React component library
6. @specs/ui/pages.md - Next.js pages and routing
7. @specs/overview.md - Overview about the project

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

This file is the authoritative source of truth for the REST API in Phase II.
