# API Specification - Phase II

## 1. Overview
This document serves as the formal contract between the Next.js frontend and the FastAPI backend. Every endpoint is designed to work within a **Layered Architecture**, ensuring that the Presentation layer (Routes) never interacts directly with the database.

## 2. Base Configuration
- **Base URL:** `http://localhost:8000/api/v1`
- **Authentication:** Bearer Token (JWT) required for all `/tasks` routes.
- **Header:** `Authorization: Bearer <token>`
- **Content-Type:** `application/json`



## 3. Endpoints & Layered Flow

### 3.1 Authentication
*Managed by Better Auth on the frontend; validated via middleware on the backend.*
- `POST /auth/signup`: User registration.
- `POST /auth/login`: User authentication.

### 3.2 Task Management (Protected)

#### A. List All Tasks
- **Endpoint:** `GET /tasks`
- **Internal Flow:** `tasks_route` -> `task_service.get_all(user_id)` -> `task_repo.fetch_all(user_id)`
- **Response:** `200 OK`
  ```json
  [
    {
      "id": "uuid",
      "title": "String",
      "description": "String",
      "is_completed": false
    }
  ]
  ```

#### B. Create Task
- **Endpoint:** `POST /tasks`
- **Internal Flow:** `tasks_route` -> `task_service.create(data, user_id)` -> `task_repo.insert(data)`
- **Payload:**

```json
{
  "title": "String",
  "description": "String"
}
```

- **Response:** `201 Created`

#### C. Update Task (Partial)
- **Endpoint:** `PATCH /tasks/{id}`
- **Internal Flow:** `tasks_route` -> `task_service.update(id, data, user_id)` -> `task_repo.patch(id, data)`
- **Payload:** `{ "is_completed": true }` or `{ "title": "New Title" }`
- **Response:** `200 OK`

#### D. Delete Task
- **Endpoint:** `DELETE /tasks/{id}`
- **Internal Flow:** `tasks_route` -> `task_service.delete(id, user_id)` -> `task_repo.remove(id)`
- **Response:** `204 No Content`

## 4. Status Codes & Error Logic

| Code | Meaning | Layer Responsible |
|------|---------|-------------------|
| 200/201 | Success | Route (final response) |
| 400 | Bad Request | Route (Pydantic validation) |
| 401 | Unauthorized | Core/Deps (JWT verification) |
| 403 | Forbidden | Service (Ownership check: task.user_id != current_user_id) |
| 404 | Not Found | Repository/Service (ID does not exist) |

## 5. Security Protocol

1. **Extraction:** The `user_id` is extracted from the JWT by the `get_current_user` dependency.
2. **Injection:** The `user_id` is passed as an argument through the Service to the Repository.
3. **Isolation:** The Repository must always include `.where(Task.user_id == user_id)` in its SQL queries.

## 6. Implementation Notes for Agent

- Use `fastapi.APIRouter` in `app/api/v1/tasks.py`.
- Define `TaskCreate` and `TaskUpdate` Pydantic models in `app/models/schemas.py`.
- Ensure all route functions are `async`.