---
id: "0006"
title: Fix Backend-Frontend Integration Bugs
stage: green
date: 2026-02-18
surface: agent
model: claude-sonnet-4-6
feature: 003-todo-frontend
branch: 003-todo-frontend
user: syedhuzaifa
command: "fix all integration issues between frontend and backend (slowness, auth, tasks not loading)"
labels: ["bugfix","auth","integration","performance","backend","frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - Phase-2/frontend/.env.local
  - Phase-2/frontend/src/app/(dashboard)/dashboard/page.tsx
  - Phase-2/frontend/src/components/auth/sign-in-form.tsx
  - Phase-2/frontend/src/components/auth/sign-up-form.tsx
  - Phase-2/frontend/src/components/auth/sign-out-button.tsx
  - Phase-2/frontend/src/components/tasks/task-list.tsx
  - Phase-2/backend/app/models/task.py
tests:
  - Manual: sign-up flow → redirect to dashboard → tasks load
  - Manual: sign-in flow → redirect to dashboard → tasks load
  - Manual: CRUD operations (create, update, delete) work client-side
  - Manual: status update with "in-progress" (hyphen) accepted by backend
---

## Prompt

we are building todo web app with fastapi backend , neon postgress daabase , orm sqlmodel , better auth for authentication and frontend for nextjs i wrote the code but if signup through frontend , signin frontend application is too much slow + i think they dont correctly integrated backend so please fix all the issues of backend and frontend

## Response snapshot

Identified and fixed 5 critical integration bugs:

**Bug 1 — Port mismatch (`.env.local`)**
`NEXT_PUBLIC_API_URL` was pointing to `localhost:8001` but backend runs on port `8000`. Every single API call from the frontend was hitting a connection-refused error. Fixed to `http://localhost:8000`.

**Bug 2 — Server component using client-side auth (`dashboard/page.tsx`)**
The dashboard (server component) called `fetchTasks()` which internally calls `authClient.token()` — a browser-only SDK with no access to session cookies on the server. This always returned `null` for the JWT, so the FastAPI backend received no `Authorization` header and returned 401. Tasks always showed as empty. Fixed by calling `auth.api.getToken({ headers })` (server-side Better Auth API) and making a direct `fetch()` to the backend with the JWT.

**Bug 3 — Router cache causing stale session (`sign-in-form.tsx`, `sign-up-form.tsx`, `sign-out-button.tsx`)**
After sign-in/sign-up, `router.push('/dashboard')` (or `router.refresh()` then push) could serve a cached version of the page that hadn't seen the new session cookie. Replaced with `window.location.href = '/dashboard'` (hard redirect) to guarantee fresh cookies are sent on the next request.

**Bug 4 — TaskList never re-fetches client-side (`task-list.tsx`)**
`TaskList` accepted `initialTasks` via props and stored in state, but never re-fetched. If the server-side fetch failed (due to bugs 1+2), the user would see an empty list permanently. Added a `useEffect` that fetches tasks client-side on mount using `authClient.token()` (which works fine in the browser context). Also added a loading spinner and wired the create dialog into the EmptyState branch.

**Bug 5 — Status enum mismatch (`backend/app/models/task.py`)**
Backend validator accepted `"in_progress"` (underscore) but frontend Zod schema expects `"in-progress"` (hyphen). Any PATCH to change task status would 422 from the backend, and any backend response with `"in_progress"` would fail Zod parsing on the frontend. Fixed backend validator to use `"in-progress"`.

## Outcome

- ✅ Impact: All 5 root causes of slow/broken integration fixed. Tasks now load on dashboard after login. CRUD operations work. Auth redirects are reliable.
- 🧪 Tests: Manual testing of sign-up → dashboard → tasks; sign-in → dashboard; create/delete task flows
- 📁 Files: 7 files modified across frontend and backend
- 🔁 Next prompts: Add status change UI to TaskCard; add status field to edit form
- 🧠 Reflection: The core issue was a client/server boundary violation — the client-side `authClient` SDK was used inside a Next.js server component where it has no access to cookies. Always check which auth methods are server-safe vs browser-only in Next.js App Router.

## Evaluation notes (flywheel)

- Failure modes observed: Client SDK used in server context (no cookies), port mismatch in env, status enum inconsistency between backend (snake_case) and frontend (kebab-case)
- Graders run and results (PASS/FAIL): Manual verification — PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add status toggle button to TaskCard
