# Database Schema Specification  
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. Overview

This document defines the complete database schema for the Todo application in Phase II.  

Key goals:
- Support multi-user isolation (each user owns their tasks only)
- Enable basic task CRUD operations
- Provide efficient filtering, sorting, and search
- Support simple analytics (counts, completion rates)
- Integrate seamlessly with Better Auth (which manages the `users` table)
- Use PostgreSQL features (Neon Serverless) for performance and scalability

**Database Engine**: PostgreSQL (Neon Serverless)  
**ORM**: SQLModel (combines SQLAlchemy + Pydantic)  
**Migration Tool**: Alembic
**Connection**: Via environment variable `DATABASE_URL`

## 2. Tables

### 2.1 users (Managed by Better Auth)

This table is **created and managed by Better Auth** library.  
Do **not** define or migrate it manually in the app — Better Auth handles it.

| Column         | Type          | Constraints                  | Description                              |
|----------------|---------------|------------------------------|------------------------------------------|
| id             | varchar(255)  | PRIMARY KEY                  | Unique user identifier (string UUID)     |
| email          | varchar(255)  | UNIQUE, NOT NULL             | User's email address                     |
| name           | varchar(255)  | NULLABLE                     | User's display name                      |
| password_hash  | text          | NOT NULL                     | Hashed password (handled by Better Auth) |
| created_at     | timestamptz   | DEFAULT now()                | Account creation timestamp               |
| updated_at     | timestamptz   | DEFAULT now() ON UPDATE now()| Last update timestamp                    |

**Indexes** (created by Better Auth):
- UNIQUE on `email`
- PRIMARY KEY on `id`

### 2.2 tasks (Application-owned table)

This is the main table managed by the application via SQLModel.

| Column         | Type          | Constraints                                      | Description                                      |
|----------------|---------------|--------------------------------------------------|--------------------------------------------------|
| id             | bigserial     | PRIMARY KEY, AUTO_INCREMENT                      | Unique task identifier (integer)                 |
| user_id        | varchar(255)  | NOT NULL, FOREIGN KEY → users.id                 | Owner of the task (references users.id)          |
| title          | varchar(200)  | NOT NULL                                         | Task title (required, max 200 chars)             |
| description    | text          | NULLABLE                                         | Optional longer description                      |
| completed      | boolean       | NOT NULL, DEFAULT false                          | Completion status                                |
| created_at     | timestamptz   | NOT NULL, DEFAULT now()                          | When the task was created                        |
| updated_at     | timestamptz   | NOT NULL, DEFAULT now() ON UPDATE now()          | Last modification timestamp                      |

**Foreign Key Constraints**
- `tasks.user_id` → `users.id`  
  - `ON DELETE CASCADE` (if user is deleted, their tasks are removed)

**Indexes** (critical for performance)
- `idx_tasks_user_id` → ON `user_id` (fast filtering by user)
- `idx_tasks_user_completed` → ON (`user_id`, `completed`) (fast status filtering)
- `idx_tasks_created_at` → ON `created_at DESC` (default sort by newest)
- `idx_tasks_title_trgm` → GIN index on `title` using `pg_trgm` extension (optional, for fuzzy search if enabled)

**Notes on Indexes**
- `user_id` is the most frequent filter → composite indexes including `user_id` are essential
- For search on `title`/`description`, consider adding trigram index later if performance becomes an issue

## 3. Relationships

- One-to-Many: One user → Many tasks
- No other tables in Phase II (e.g., no tags, priorities, due dates yet)

## 4. Data Integrity Rules

- `title` must not be empty or exceed 200 characters
- `user_id` must exist in `users` table (enforced by FK)
- `completed` defaults to `false`
- Timestamps auto-managed (no manual setting required)
- No duplicate tasks per user by ID (PK enforces this)

## 5. Migration & Setup Notes

- Use **Alembic** for migrations:
  - `alembic init migrations`
  - Define initial migration for `tasks` table
- SQLModel models should mirror this schema exactly:
  ```python
  class Task(SQLModel, table=True):
      id: Optional[int] = Field(default=None, primary_key=True)
      user_id: str = Field(foreign_key="users.id")
      title: str = Field(max_length=200)
      description: Optional[str] = Field(default=None)
      completed: bool = Field(default=False)
      created_at: datetime = Field(default_factory=datetime.utcnow)
      updated_at: datetime = Field(default_factory=datetime.utcnow)
  ```
- Connection string: `postgresql://user:password@host:5432/dbname` (from Neon)

## 6. Analytics Support (Phase II Basic)

The schema supports the following efficient queries for `/api/{user_id}/analytics`:

- **Total tasks**: `SELECT COUNT(*) FROM tasks WHERE user_id = :user_id`
- **Completed**: `SELECT COUNT(*) FROM tasks WHERE user_id = :user_id AND completed = true`
- **Pending**: Total - Completed
- **Completion rate**: `(completed / total) * 100`
- **Tasks this week**: `WHERE user_id = :user_id AND created_at >= NOW() - INTERVAL '7 days'`

All queries are fast thanks to `user_id` indexes.

## 7. Future Extensions (Phase III+)

- Add columns: priority (enum: low/medium/high), due_date (timestamptz), tags (array or JSONB)
- Add table: task_events (for audit/recurring in Phase V)
- Add indexes for new filters

## 8. Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/ui/components.md - React component library
6. @specs/ui/pages.md - Next.js pages and routing
7. @specs/overview.md - Overview about the project

## 9. References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

This schema is the single source of truth for the database in Phase II.