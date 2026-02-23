---
id: "025"
title: "Fix chatbot DB and analytics refresh bugs"
stage: green
date: "2026-02-23"
surface: agent
model: claude-sonnet-4-6
feature: 001-chatbot-frontend
branch: 001-chatbot-frontend
user: syedhuzaifa
command: "fix critical bugs: first response slow, 2nd message not in db, analytics not updating"
labels: ["bug-fix", "backend", "frontend", "analytics", "performance"]
links:
  spec: "specs/001-chatbot-frontend/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files_created:
  - Phase-3/backend/app/mcp/server.py
  - Phase-3/backend/app/api/v1/tasks.py
files_modified:
  - Phase-3/backend/app/main.py
  - Phase-3/backend/app/services/chat_service.py
  - Phase-3/backend/app/services/chatkit_adapter.py
  - Phase-3/backend/app/mcp/tools/list_tasks.py
  - Phase-3/backend/app/repositories/task_repository.py
  - Phase-3/frontend/src/lib/api/chat-api-client.ts
  - Phase-3/frontend/src/app/(dashboard)/analytics/page.tsx
  - Phase-3/frontend/src/app/(dashboard)/history/page.tsx
tests_run: []
---

## Prompt

i can face one critical bug if i send message into chatbot first response is low, 2nd conversation or message is not added in db and one critical issue is that analytics page is not updated and other pages also ..

## Root Cause Analysis

Four distinct bugs identified:

1. **Agent input bug (NameError crash)**: `chat_service.py` line 123 used `input_messages` instead of `agent_input`. When `history` is empty (first message in any conversation), `input_messages` is never defined → `NameError` → agent never runs → no response, no DB writes.

2. **Missing `app/mcp/server.py`**: Updated `chat_service.py` imports `from app.mcp.server import ALL_TASK_TOOLS` but file didn't exist → `ImportError` → backend wouldn't start.

3. **Stale `function_tool` reference**: `list_tasks.py` had `list_tasks = function_tool(list_tasks_impl)` at module level without importing `function_tool` → `NameError`.

4. **Analytics/history LLM pollution**: `fetchTaskStats()` and `fetchCompletedTasks()` called `sendMessage()` (full LLM roundtrip) creating NEW conversations and 2 new DB messages on every page load. This caused:
   - Every analytics visit = 2 phantom messages in DB
   - No real-time data (LLM doesn't always call list_tasks)
   - Capped at 5 tasks (MCP list_tasks[:5] limit)
   - No refresh when switching pages back

5. **Performance**: `httpx.AsyncClient()` created fresh per chatbot message → TCP connection setup overhead on every message.

## Changes Made

### Backend
- **`app/mcp/server.py`** (new): Exports `ALL_TASK_TOOLS = [add_task, list_tasks, ...]` as `function_tool` wrappers — used by `ChatService` to register tools with the agent directly (no subprocess).
- **`app/api/v1/tasks.py`** (new): `GET /api/{user_id}/tasks?status=` — direct DB query, no LLM, returns `{tasks, total, completed, pending, inProgress}`.
- **`app/main.py`**: Added `tasks_router`, removed dead MCPServerStdio subprocess (agent now uses direct function tools), simplified lifespan.
- **`app/services/chat_service.py`**: Fixed `Runner.run(agent, input_messages)` → `Runner.run(agent, agent_input)`.
- **`app/services/chatkit_adapter.py`**: Replaced per-request `httpx.AsyncClient()` with module-level `_http_client` (persistent TCP connection).
- **`app/mcp/tools/list_tasks.py`**: Removed orphaned `list_tasks = function_tool(list_tasks_impl)` line.
- **`app/repositories/task_repository.py`**: Added `in_progress` status filter support.

### Frontend
- **`chat-api-client.ts`**: `fetchTaskStats()` and `fetchCompletedTasks()` now call `GET /api/{user_id}/tasks` directly — no LLM roundtrip, no DB pollution.
- **`analytics/page.tsx`**: Added `window.addEventListener("focus", load)` — page re-fetches when user navigates back.
- **`history/page.tsx`**: Same window focus re-fetch pattern.

## Outcome

- First message no longer crashes (agent_input bug fixed)
- All messages persist to DB correctly
- Analytics/history load instantly via REST (no LLM call)
- Analytics/history auto-refresh on tab/window focus
- No more phantom conversations from page loads
- Persistent httpx client reduces per-message latency
