# Feature: Task CRUD Operations  
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. Purpose

This specification defines the complete **Task CRUD** (Create, Read, Update, Delete) functionality for the Todo application in Phase II, including the Mark Complete toggle.

The feature must:
- Allow authenticated users to fully manage their personal todo list
- Enforce strict **user data isolation** (users can only interact with their own tasks)
- Support basic filtering, sorting, and search for usability
- Provide a clean foundation for future advanced features (recurring tasks, priorities, due dates in Phase V)
- Be fully implemented via spec-driven development (Claude Code generates code from this spec)

All CRUD operations must be:
- Protected by JWT authentication
- Scoped to the authenticated user's `user_id`
- Validated on both frontend (UI) and backend (API)
- Logged with proper timestamps

## 2. User Stories

As an **authenticated user**,  
I want to **create** a new task with a title and optional description,  
so that I can capture things I need to do.

As an **authenticated user**,  
I want to **view** all my tasks in a list with their status (completed or pending),  
so that I can see what I have pending and what I've already done.

As an **authenticated user**,  
I want to **update** the title or description of an existing task,  
so that I can correct mistakes or add more details later.

As an **authenticated user**,  
I want to **delete** a task that is no longer needed,  
so that my list stays clean and relevant.

As an **authenticated user**,  
I want to **mark a task as complete** or **incomplete**,  
so that I can track my progress visually.

As an **authenticated user**,  
I want to **filter** my task list by status (all, pending, completed),  
so that I can focus on what still needs attention.

As an **authenticated user**,  
I want to **sort** my tasks by creation date or title,  
so that I can prioritize or review them logically.

As an **authenticated user**,  
I want to **search** my tasks by keyword in title or description,  
so that I can quickly find specific items.

## 3. Acceptance Criteria

### 3.1 Create Task
- Route: POST `/api/{user_id}/tasks`
- Required field: `title` (1–200 characters, trimmed)
- Optional field: `description` (max 2000 characters)
- `user_id` in path must match authenticated JWT user_id → else 403
- Auto-set: `completed = false`, `created_at` & `updated_at` = now()
- Response: 201 Created + full task object
- Frontend validation: show error if title is empty
- Backend validation: reject empty title, trim whitespace

### 3.2 Read / List Tasks
- Route: GET `/api/{user_id}/tasks`
- Always filtered: `WHERE user_id = :authenticated_user_id`
- Default sort: newest first (`created_at DESC`)
- Query params supported:
  - `status`: `all` (default), `pending`, `completed`
  - `sort`: `created_desc`, `created_asc`, `title_asc`, `title_desc`
  - `search`: keyword (case-insensitive, partial match on title OR description)
  - `limit` & `offset` for pagination
- Response includes `meta` with total count
- If no tasks → return empty array + total: 0

### 3.3 Read Single Task
- Route: GET `/api/{user_id}/tasks/{task_id}`
- Must be owned by user → else 404 (not 403 to avoid leaking existence)
- Response: full task object or 404

### 3.4 Update Task
- Route: PUT `/api/{user_id}/tasks/{task_id}`
- Supports partial updates (only send changed fields)
- Only `title` and `description` updatable in Phase II
- `updated_at` auto-updated
- Must be owned → else 404
- Response: 200 + updated task object

### 3.5 Delete Task
- Route: DELETE `/api/{user_id}/tasks/{task_id}`
- Must be owned → else 404
- Hard delete (no soft-delete in Phase II)
- Response: 200 + success message

### 3.6 Toggle Completion
- Route: PATCH `/api/{user_id}/tasks/{task_id}/complete`
- Body optional: `{ "completed": true/false }`
  - If omitted → toggle current value
- Must be owned → else 404
- `updated_at` auto-updated
- Response: 200 + updated task object

### 3.7 UI Requirements (Dashboard Integration)
- All CRUD operations happen **inside the /dashboard** page
- Task List component shows:
  - Title + description (truncated if long)
  - Status badge (pending/completed)
  - Created/updated dates (relative time preferred)
  - Edit & Delete buttons/icons
  - Checkbox/toggle for complete
- Add Task: floating or top form (title input + description textarea + submit)
- Filters/Sort/Search: controls above the list
- Optimistic updates: show changes immediately, rollback on error
- Error handling: toast notifications for failures (e.g., "Task not found", "Unauthorized")

### 3.8 Performance & Security
- All queries **must** include `WHERE user_id = :authenticated_user_id`
- Indexes required: `user_id`, `user_id + completed`, `created_at`
- No N+1 queries (use proper joins if needed in future)
- Input sanitization: backend trims strings, rejects invalid data
- No rate limiting on CRUD in Phase II (add in future if needed)

## 4. Edge Cases

- Empty title on create → 400 "Title is required"
- Non-existent task_id → 404
- Trying to access another user's task → 403 (API) or redirect (UI)
- Very long description → truncate on display, but store full
- Rapid toggles → last write wins (no optimistic locking in Phase II)
- No tasks → show empty state UI ("No tasks yet. Add one!")

## 5. Tech Stack & Integration

- **Frontend**: Next.js (App Router), React hooks, Tailwind CSS
- **Backend**: FastAPI + SQLModel
- **Database**: Neon PostgreSQL (schema: @specs/database/schema.md)
- **API**: Defined in @specs/api/rest-endpoints.md
- **Auth**: Better Auth + JWT → enforced in middleware

## Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/authentication.md - Authentication and JWT flow
3. @specs/api/rest-endpoints.md - Complete API endpoint documentation
4. @specs/database/schema.md - Database schema and relationships
5. @specs/ui/components.md - React component library
6. @specs/ui/pages.md - Next.js pages and routing
7. @specs/overview.md - Overview about the project

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

**This specification is the single source of truth for Task CRUD in Phase II.**  
All code generation must reference this file.