---
id: "0005"
title: Backend Bug Fixes
stage: green
date: 2026-02-22
surface: agent
model: claude-sonnet-4-6
feature: 001-chatbot-backend
branch: 001-chatbot-frontend
user: syedhuzaifa
command: manual fix
labels: ["backend", "bug-fix", "asyncpg", "mcp", "chat-service", "database"]
links:
  spec: specs/001-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - Phase-3/backend/app/core/database.py
  - Phase-3/backend/app/services/chat_service.py
  - Phase-3/backend/app/main.py
tests:
  - null
---

## Prompt

first update the backend code then we move towards frontend

## Response snapshot

Fixed 4 bugs in the Phase-3 backend:

### Bug 1 — database.py: DATABASE_URL scheme incompatible with asyncpg

**Problem**: `.env` uses `postgresql://` (standard/psycopg format). `create_async_engine` with asyncpg requires `postgresql+asyncpg://`. Also, `channel_binding=require` is a psycopg3-only param that asyncpg rejects.

**Fix**: Added `_to_asyncpg_url()` helper that:
- Converts `postgresql://` → `postgresql+asyncpg://`
- Strips `channel_binding=...` query param via regex

### Bug 2 — chat_service.py: Tool name extraction wrong

**Problem**: Code did `tool_name = getattr(item, "name", "unknown")` — but `ToolCallItem` doesn't have a direct `.name`. For Chat Completions API, the name is on `raw_item.function.name` (Pydantic model) or `raw_item["function"]["name"]` (dict).

**Fix**: Added branching logic that handles:
- Dict format: `raw.get("function", {}).get("name")`
- Object format with `.function`: `raw.function.name`
- Responses API direct format: `raw.name`

### Bug 3 — chat_service.py: Tool results always empty `{}`

**Problem**: `ToolCallRecord(result={})` always returned empty results, losing the actual MCP tool output (task_id, status, title etc.).

**Fix**: First pass over `result.new_items` collects `tool_call_output_item` entries, keyed by `call_id`. Second pass over `tool_call_item` entries looks up the matching output and populates `result`.

### Bug 4 — main.py: Naming conflict + fragile lifespan

**Problem**: Model imports `import app.models.task` inside `async def lifespan(app: FastAPI)` shadow the `app` FastAPI parameter (Mypy error). Also `_mcp_http.lifespan(app)` wrapper was fragile in FastMCP v3.

**Fix**:
- Moved model imports to module level (above lifespan function)
- Removed `_mcp_http.lifespan(app)` wrapper (not needed for stateless HTTP requests)
- Added `env=dict(os.environ)` to MCPServerStdio params for explicit env passing

## Outcome

- ✅ Impact: Backend can now start without crashing on DB URL format; tool calls correctly extracted and matched with results; lifespan is clean
- 🧪 Tests: Syntax-checked all 3 files; no runtime test yet (need Neon DB credentials)
- 📁 Files: app/core/database.py, app/services/chat_service.py, app/main.py
- 🔁 Next prompts: User needs to create new Phase 3 Neon database and update DATABASE_URL in .env; then test with `uv run uvicorn app.main:app --reload`; then move to frontend implementation
- 🧠 Reflection: The asyncpg URL format issue was the most critical — it would have prevented the app from starting at all. The tool name extraction bug would have silently returned "unknown" for all tool calls.

## Evaluation notes (flywheel)

- Failure modes observed: Naming conflict between function parameter and import statement detected by Mypy; fixed by moving imports to module level
- Graders run and results (PASS/FAIL): Python AST parse check — PASS for all 3 files
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run `uv run uvicorn app.main:app --reload` with a valid DATABASE_URL to verify startup
