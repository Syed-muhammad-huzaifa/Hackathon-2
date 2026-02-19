---
id: "0004"
title: "Add auth signup signin routes"
stage: green
date: "2026-02-16"
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-todo-backend-api
branch: 002-todo-backend-api
user: syedhuzaifa
command: "add signup signin auth routes using better-auth and jwt"
labels: ["auth", "better-auth", "jwt", "signup", "signin", "fastapi"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "Phase-2/backend/app/api/v1/auth.py"
  - "Phase-2/backend/app/main.py"
tests:
  - "Manual test via /docs Swagger UI"
---

## Prompt

can you made signup signin route ? the main thing in auth ? we are using better auth in frontend also i added context-7 mcp server for documentation and schema validation

## Response

Added `app/api/v1/auth.py` with three endpoints:

- `POST /auth/sign-up` — proxies to Better Auth `/api/auth/sign-up/email`, exchanges session cookie for JWT, returns `{status, token, user}`
- `POST /auth/sign-in` — proxies to Better Auth `/api/auth/sign-in/email`, exchanges session cookie for JWT, returns `{status, token, user}`
- `GET /auth/me` — verifies Bearer JWT via JWKS and returns current user `{id, email, name}`

Architecture: FastAPI proxies auth requests to Better Auth (Next.js server) using `httpx`. After Better Auth authenticates and sets a session cookie, FastAPI calls `/api/auth/token` (Better Auth JWT plugin) to exchange the session for a JWT. The JWT is returned to the caller and used for all subsequent task API calls.

**Requires Better Auth JWT plugin on frontend:**
```typescript
import { jwt } from "better-auth/plugins"
export const auth = betterAuth({ plugins: [jwt()], ... })
```

**Full auth flow:**
1. `POST /auth/sign-up` or `POST /auth/sign-in` → get JWT
2. Use JWT as `Authorization: Bearer <token>` on all task endpoints
3. `GET /auth/me` to verify token and fetch user profile

Updated `app/main.py` to register the auth router.

## Outcome

Server hot-reloaded successfully. All three auth routes available in Swagger UI at `/docs`.
