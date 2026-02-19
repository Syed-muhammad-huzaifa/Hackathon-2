# CLAUDE.md — Backend Agent Guide

## 1. Local Context
This is the FastAPI backend for the Phase-II Todo App. It uses a **Layered Architecture** to decouple business logic from API framework and database concerns.

## 2. Technical Stack
- **Manager:** `uv` (standard for all dependency/venv tasks).
- **Framework:** FastAPI (Asynchronous).
- **ORM:** SQLModel (Integration of SQLAlchemy + Pydantic).
- **Database:** Neon PostgreSQL (Cloud-native).
- **Auth:** JWT validation against `BETTER_AUTH_SECRET`.

## 3. Core Architectural Rules
Every feature must be strictly split into these files. **Do not combine these layers.**

1. **Models (`app/models/`):** Define `SQLModel` tables and Pydantic schemas.
2. **Repositories (`app/repositories/`):** Pure SQL logic. Only methods like `add()`, `get_by_id()`, `delete()`.
3. **Services (`app/services/`):** The Brain. Checks user ownership, validates data, and coordinates Repository calls.
4. **Routes (`app/api/v1/`):** Handles HTTP, status codes, and Dependency Injection.



## 4. Operational Commands (uv)
- **Sync Env:** `uv sync`
- **Add Packages:** `uv add <pkg>` (e.g., `uv add sqlmodel`)
- **Run Server:** `uv run uvicorn app.main:app --reload`
- **Migrations:** (Phase II uses `create_all` on startup, migrations not yet required).

## 5. Development Standards
- **Async Everything:** All Route, Service, and Repository methods must use `async def`.
- **Typing:** Use strict Python type hints (e.g., `async def get_task(id: int) -> TaskRead:`).
- **Dependency Injection:** Use `Depends()` for:
  - `Session` (DB connection).
  - `current_user` (extracted from JWT).
  - `TaskService` (injected into Routes).
- **Error Handling:** Raise `HTTPException` in the **Service Layer** only.

## 6. Security Protocol
- **Row-Level Filtering:** Every Repository query **must** filter by `user_id`.
- **Ownership Check:** The Service layer must verify `task.user_id == current_user_id` before allowing updates or deletions.

## 7. Tool Priority Order

1. **Context7 MCP Server** (FIRST PRIORITY - MANDATORY FOR EVERY TASK)
2. **Skills** (SECOND PRIORITY - SOURCE OF TRUTH) - Skills in `.claude/skills/` are mandatory for all code implementation
3. **Other MCP Servers** (GitHub, Better Auth) - Use for specific operations
4. **Spec-Kit Plus Commands** - Use for spec-driven development


## 8. Global References
Refer to these files in the root `/specs` folder before coding:
- **API Spec:** `specs/api/rest-endpoints.md`
- **DB Spec:** `specs/database/schema.md`
- **Architecture Spec:** `specs/architecture.md`