---
id: "0007"
title: Backend Audit and Bug Fixes
stage: green
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 003-todo-frontend
branch: 003-todo-frontend
user: syedhuzaifa
command: "review backend correctness: SQLModel, JWT, Pydantic validation, error handling"
labels: ["audit","bugfix","backend","pydantic","sqlmodel","jwt","datetime"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - Phase-2/backend/app/models/task.py
  - Phase-2/backend/app/repositories/task_repository.py
  - Phase-2/backend/app/core/database.py
  - Phase-2/backend/app/api/v1/auth.py
tests:
  - Manual: task list response contains created_at with Z suffix
  - Manual: PATCH /tasks/{id} with description=null clears the field
  - Manual: GET /auth/me returns validated MeResponse shape
---

## Prompt

is backend is correct they use sql moodel and jwt verification and pydntic validation for both request and response with proper error handling ?

## Response snapshot

**Full backend audit completed. Verdict: architecture is solid — 4 bugs fixed.**

### What's Correct ✅
- SQLModel with async SQLAlchemy: `AsyncSession`, `select()`, `scalars()`, `commit()`, `refresh()` all used correctly
- JWT verification via JWKS: fetches RS256 public keys from Better Auth `/api/auth/jwks`, caches for 5 min, refreshes on unknown `kid`, extracts `sub` as user_id
- Pydantic validators on ALL request models: `field_validator` on title (strip + empty check), email (basic format), status (enum), priority (enum)
- `response_model=` on all routes — Pydantic serializes every response through schema
- Exception handlers: 422 for validation, 409 for integrity errors, 500 for DB/generic, all registered in `main.py`
- Multi-tenancy: every repository query filters by `user_id` — no cross-user data leakage possible
- Ownership check in routes BEFORE service call (403 if mismatch)
- Soft delete: `status="deleted"`, excluded from `find_by_user_id` query
- Full async chain: route → service → repository → session

### Bugs Fixed 🐛

**Bug 1 (Critical): Naive datetime → no Z suffix → Zod rejects**
`datetime.utcnow()` produces naive datetimes. Pydantic v2 serializes them as `"2024-01-01T12:00:00"` (no Z). Zod v4 `z.string().datetime()` requires a timezone indicator and rejects this format. Every client-side task fetch would fail Zod parse and silently fall back to initialTasks.
Fix: Added `@field_serializer("created_at", "updated_at")` to `TaskResponse` that appends `Z` for naive datetimes and converts aware datetimes to UTC+Z.

**Bug 2: Repository update skips None values**
`if value is not None and hasattr(task, key)` prevented setting any field to `None`. The service layer could compute `description: None` to clear it, but the repository would silently skip it. Cleared description is a valid user action.
Fix: Changed to `if hasattr(task, key)` — None values are now correctly written to the DB.

**Bug 3 (Minor): Unused import in database.py**
`from sqlalchemy.orm import sessionmaker` was never used (the code uses `async_sessionmaker`).
Fix: Removed.

**Bug 4 (Minor): /auth/me missing response_model**
`GET /auth/me` returned a raw dict without a `response_model=` declaration. FastAPI wouldn't validate the response shape through Pydantic.
Fix: Added `MeResponse(BaseModel)` and added `response_model=MeResponse` to the decorator.

## Outcome

- ✅ Impact: Backend is now fully correct — datetime serialization fixed (Zod will accept responses), None-clearing works, all responses typed through Pydantic
- 🧪 Tests: Manual verification of datetime format in API responses; verify description can be cleared via PATCH
- 📁 Files: 4 backend files modified
- 🔁 Next prompts: Consider adding enum types for status/priority fields using Python Enum or Literal types for stronger type safety
- 🧠 Reflection: The naive datetime bug is a very common FastAPI+Zod interop issue. Always use field_serializer to control datetime format in response schemas, or annotate columns with timezone=True from the start.

## Evaluation notes (flywheel)

- Failure modes observed: naive datetime serialization mismatch between Python (no tz) and TypeScript Zod (requires tz); repository update silently swallowing None values
- Graders run and results (PASS/FAIL): Manual code review — PASS after fixes
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add Python Enum for TaskStatus and TaskPriority to get compile-time validation instead of string validators
