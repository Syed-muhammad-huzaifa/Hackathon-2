# CLAUDE.md — Master Agent Orchestrator

## 1. Project Context
This is a Full-Stack Monorepo for a production-grade Todo Application. All development is **Spec-Driven**, meaning the documentation in `/specs` is the absolute "Source of Truth." 

## 2. Reference Documents (Source of Truth)
The Agent **must** read these before any code modification:
- **Project Mission:** `specs/overview.md`
- **Global Architecture:** `specs/architecture.md` (Strict Layered Pattern)
- **Database Schema:** `specs/database/schema.md`
- **API Contract:** `specs/api/rest-endpoints.md`
- **Frontend Design:** `specs/ui/components.md` & `specs/ui/pages.md`

## 3. Monorepo Structure
- `/specs`: Markdown definitions of all features and architecture.
- `/backend`: FastAPI service managed by **uv**.
- `/frontend`: Next.js 15+ application.

## 4. Operational Commands

### 4.1 Backend Management (via uv)
- **Initialize/Sync:** `cd backend && uv sync`
- **Run Dev Server:** `cd backend && uv run uvicorn app.main:app --reload`
- **Add Dependency:** `uv add <package>`

### 4.2 Frontend Management (via npm)
- **Install:** `cd frontend && npm install`
- **Run Dev Server:** `npm run dev`

## 5. Implementation Workflow
1. **Analyze:** Check the relevant `.md` in `/specs` for requirements.
2. **Plan:** Create an implementation plan that follows the **Layered Pattern** (Repository -> Service -> Route).
3. **Execute:** - Use `async` for all Python logic.
    - Use `TypeScript` for all Frontend logic.
    - Maintain strict type safety.
4. **Verify:** Check that ownership validation (multi-tenancy) is enforced in the Service layer.

## 6. Guardrails
- **No Layer Skipping:** Never allow a Route to call a Repository directly.
- **No "Guessing":** If a database field or API endpoint is not in the specs, ask for clarification or update the spec first.
- **Environment:** Always use `.env` files for sensitive keys (Database URL, Auth Secrets).