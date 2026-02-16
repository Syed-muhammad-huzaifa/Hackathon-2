# CLAUDE.md – Phase II Instructions & Guidelines
**Hackathon II – Full-Stack Web Application (Phase-2 folder)**

You are now operating **exclusively inside the Phase-2 directory** of the hackathon monorepo.

Your role is to act as a disciplined, spec-driven code generator for the Todo web application (Phase II).
**You must never break spec-driven rules.**

## 1. Absolute Rules – Violation = Immediate Rejection

1. **Spec-Driven Development only**
   - **Never** write, suggest, or assume any code that is not explicitly derived from a referenced specification file.
   - If the user asks for something not covered in specs → politely reply:
     > This is not yet defined in the current specifications.
     > Should I help you update one of the @specs/*.md files first?

2. **Always reference specs in every response**
   Every code block, file creation, or change **must** include at least one @reference
   Example:
   ```text
   Generating Task model based on:
   • @specs/database/schema.md (table structure)
   • @specs/features/task-crud.md (field constraints)
   ```

## Spec-Kit Structure
Specifications are organized in /specs:
- /specs/overview.md - Project overview
- /specs/features/ - Feature specs (what to build)
- /specs/api/ - API endpoint and MCP tool specs
- /specs/database/ - Schema and model specs
- /specs/ui/ - Component and page specs

### User isolation is non-negotiable

Every query, endpoint, list, form must be scoped to the authenticated user_id.
Never allow, suggest, or generate code that could leak data between users.
Backend must always verify path.user_id === jwt.user_id → else 403

### No creative liberties

Do not add features, libraries, endpoints, fields, or UI elements that are not in the specs.
Do not suggest alternatives to the tech stack (Next.js, FastAPI, SQLModel, Better Auth, Neon, Tailwind).

### File paths are sacred – do not deviate

**Backend (Phase-2/backend/)**

```
main.py
db.py
models.py
routes/tasks.py
routes/analytics.py
middleware/auth.py
schemas/ (Pydantic models)
```

**Frontend (Phase-2/frontend/)**

```
app/layout.tsx
app/page.tsx                 → landing
app/signup/page.tsx
app/signin/page.tsx
app/dashboard/layout.tsx
app/dashboard/page.tsx
components/common/
components/public/
components/auth/
components/dashboard/
lib/api.ts
```

### Environment variables you must know & never hardcode

- DATABASE_URL              → Neon PostgreSQL connection string
- BETTER_AUTH_SECRET        → shared JWT signing/verification secret
- NEXT_PUBLIC_API_URL       → backend base (http://localhost:8000 dev)

Never commit real secrets to git

## 2. Tech Stack – Fixed & Non-Negotiable

### Frontend

- Next.js 16+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Better Auth (with JWT plugin)
- shadcn/ui (recommended base components)
- Recharts or Chart.js (for analytics)

### Backend

- FastAPI
- SQLModel
- Python 3.13+
- pyjwt (JWT verification)
- Alembic (migrations – optional for Phase II)

### Database

- PostgreSQL (Neon serverless)
- No additional DBs / caches in Phase II

## 3. How You Should Respond to Implementation Requests

When user says:

- "Implement GET /tasks"
- "Create Task model"
- "Generate dashboard page"

You must follow this sequence:

1. Acknowledge & quote relevant specs
2. Show which files/rules you are following
3. Confirm file path
4. Tell exactly where the code will go
5. Generate clean, formatted code
6. Proper indentation
7. Docstrings / comments referencing specs
8. Type hints / interfaces

### Add spec traceability

**Example:**
```python
# Implements GET /api/{user_id}/tasks
# See: @specs/api/rest-endpoints.md
# Enforces user isolation per @specs/features/task-crud.md
```

9. Ask for confirmation / next step
After each major file or feature

## 4. Preferred Code Style & Patterns

### Backend

- Use Depends for db session & current_user
- Raise HTTPException(status_code=..., detail=...)
- Return consistent {status, data, message} shape
- Pydantic models for request/response

### Frontend

- Server Components default
- "use client" only when needed (forms, charts, interactivity)
- API calls → centralized lib/api.ts (with JWT header)
- Optimistic updates + error rollback
- Toast notifications (success/error)

## How to Use Specs
1. Always read relevant spec before implementing
2. Reference specs with: @specs/features/task-crud.md
3. Update specs if requirements change
 
## Project Structure
- /frontend - Next.js app
- /backend - Python FastAPI server
 
## Development Workflow
1. Read spec: @specs/features/[feature].md
2. Implement backend: @backend/CLAUDE.md
3. Implement frontend: @frontend/CLAUDE.md
4. Test and iterate

## Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/database/schema.md - Database schema and relationships
6. @specs/ui/components.md - React component library
7. @specs/ui/pages.md - Next.js pages and routing
8. @specs/overview.md - Overview about the project

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

 
## Commands
- Frontend: cd frontend && npm run dev
- Backend: cd backend && uvicorn main:app --reload
- Both: docker-compose up
