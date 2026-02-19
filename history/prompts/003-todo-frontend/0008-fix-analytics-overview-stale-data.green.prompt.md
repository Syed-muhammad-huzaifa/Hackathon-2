---
id: "0008"
title: Fix analytics and overview stale data after task mutation
stage: green
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 003-todo-frontend
branch: 003-todo-frontend
user: syedhuzaifa
command: "fix stale data on analytics/overview after task creation"
labels: ["bug", "caching", "router-cache", "next.js", "revalidation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/actions.ts (created)
  - frontend/src/components/tasks/task-list.tsx (modified)
tests:
  - Manual: create task on /dashboard/tasks, navigate to /dashboard — stats update
  - Manual: create task, navigate to /dashboard/analytics — charts update
---

## Prompt

i found one issue if i added task then analytics and overview page is not updated whats the issue please fix it

## Response snapshot

**Root Cause:** Next.js Router Cache. `router.refresh()` only invalidates the cache for the **current route** (`/dashboard/tasks`). When navigating to `/dashboard` or `/dashboard/analytics`, Next.js serves a stale RSC payload from the client-side router cache, so the data appears unchanged.

**Fix:**
1. Created `frontend/src/app/actions.ts` — a Server Action that calls `revalidatePath` for all three dashboard routes (`/dashboard`, `/dashboard/analytics`, `/dashboard/tasks`).
2. Updated `task-list.tsx` — imported `revalidateDashboard` and called it (with `await`) before `router.refresh()` in all four mutation handlers: `handleTaskCreated`, `handleTaskUpdated`, `handleStatusChange`, `handleTaskDeleted`.

`revalidatePath` invalidates Next.js's Full Route Cache AND clears the corresponding entries from the client-side Router Cache, so all routes show fresh data immediately on navigation.

## Outcome

- ✅ Impact: Analytics and overview pages now reflect new/updated/deleted tasks immediately after any mutation on the tasks page
- 🧪 Tests: Manual verification — create task, navigate to overview and analytics to confirm counts update
- 📁 Files: 1 file created, 1 file modified
- 🔁 Next prompts: None anticipated; bug is fully resolved
- 🧠 Reflection: `router.refresh()` alone is insufficient for cross-route cache invalidation in Next.js App Router. Server Actions with `revalidatePath` are the correct pattern for this.

## Evaluation notes (flywheel)

- Failure modes observed: Stale Router Cache not cleared by `router.refresh()` for non-current routes
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
