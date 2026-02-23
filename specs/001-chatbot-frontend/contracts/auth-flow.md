# Phase 2 Session Integration Flow

**Feature**: 001-chatbot-frontend
**Date**: 2026-02-21

## Overview

This document describes how Phase 3 frontend integrates with Phase 2 Better Auth authentication. **Phase 3 does NOT implement authentication** - it reads existing session cookies from Phase 2 and passes JWT tokens to the backend for verification.

**Key Principle**: Frontend is a pass-through - Phase 2 handles authentication, Phase 3 backend verifies JWT.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Phase 2 (Better Auth)                           │
│                                                                      │
│  ┌──────────────┐                                                   │
│  │ Sign-Up/     │                                                   │
│  │ Sign-In      │                                                   │
│  │ Forms        │                                                   │
│  └──────┬───────┘                                                   │
│         │                                                            │
│         │ Better Auth creates session                               │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Session Cookie (httpOnly, secure)                        │      │
│  │  Name: better-auth.session_token                          │      │
│  │  Value: JWT token                                         │      │
│  │  Domain: shared with Phase 3                              │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               │ Cookie accessible to Phase 3
                               │ (same domain)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 3 Frontend (Next.js 15)                     │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                    Middleware                             │      │
│  │  - Checks if session cookie exists                       │      │
│  │  - Redirects to Phase 2 sign-in if missing               │      │
│  └──────┬───────────────────────────────────────────────────┘      │
│         │                                                            │
│         │ Cookie exists                                              │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              Protected Routes (Chat/Analytics)            │      │
│  │  - getJWTToken() reads cookie value                      │      │
│  │  - Does NOT verify JWT (backend handles this)            │      │
│  └──────┬───────────────────────────────────────────────────┘      │
│         │                                                            │
│         │ API calls with JWT                                        │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                  Backend API Client                       │      │
│  │  - Extracts JWT from cookie                              │      │
│  │  - Sends in Authorization: Bearer <token> header         │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               │ Authorization: Bearer <JWT>
                               ▼
                    ┌──────────────────────┐
                    │   Phase 3 Backend    │
                    │   (FastAPI)          │
                    │                      │
                    │ - Verifies JWT       │
                    │ - Validates user_id  │
                    │ - Returns data       │
                    └──────────────────────┘
```

---

## Flow Diagrams

### 1. Initial Authentication (Phase 2)

**Note**: This happens in Phase 2, NOT Phase 3.

```
User                Phase 2 Frontend      Phase 2 Better Auth
 │                     │                      │
 │  Sign up/Sign in    │                      │
 │────────────────────>│                      │
 │                     │                      │
 │                     │ Better Auth flow     │
 │                     │─────────────────────>│
 │                     │                      │
 │                     │                      │ Create session
 │                     │                      │ Generate JWT
 │                     │                      │
 │                     │ Set-Cookie (httpOnly)│
 │                     │<─────────────────────│
 │                     │                      │
 │  Authenticated      │                      │
 │<────────────────────│                      │
 │                     │                      │
```

### 2. Phase 3 Protected Route Access

```
User                Phase 3 Frontend      Middleware
 │                     │                      │
 │  Navigate to /chat  │                      │
 │────────────────────>│                      │
 │                     │                      │
 │                     │ Request /chat        │
 │                     │─────────────────────>│
 │                     │                      │
 │                     │                      │ Check cookie exists
 │                     │                      │ (better-auth.session_token)
 │                     │                      │
 │                     │                      │ Cookie exists?
 │                     │                      │──────────┐
 │                     │                      │          │
 │                     │                      │<─────────┘
 │                     │                      │
 │                     │ Allow access         │
 │                     │<─────────────────────│
 │                     │                      │
 │  Render chat page   │                      │
 │<────────────────────│                      │
 │                     │                      │
```

### 3. Phase 3 API Call with JWT

```
User                Phase 3 Frontend      Phase 3 Backend
 │                     │                      │
 │  Send chat message  │                      │
 │────────────────────>│                      │
 │                     │                      │
 │                     │ getJWTToken()        │
 │                     │ (read cookie)        │
 │                     │                      │
 │                     │ POST /api/{user_id}/ │
 │                     │      chat            │
 │                     │ Authorization:       │
 │                     │   Bearer <JWT>       │
 │                     │─────────────────────>│
 │                     │                      │
 │                     │                      │ Verify JWT signature
 │                     │                      │ Check expiration
 │                     │                      │ Validate user_id
 │                     │                      │ Process request
 │                     │                      │
 │                     │ Response             │
 │                     │<─────────────────────│
 │                     │                      │
 │  Display response   │                      │
 │<────────────────────│                      │
 │                     │                      │
```

### 4. Unauthenticated Access Attempt

```
User                Phase 3 Frontend      Middleware
 │                     │                      │
 │  Navigate to /chat  │                      │
 │────────────────────>│                      │
 │                     │                      │
 │                     │ Request /chat        │
 │                     │─────────────────────>│
 │                     │                      │
 │                     │                      │ Check cookie exists
 │                     │                      │
 │                     │                      │ Cookie missing!
 │                     │                      │──────────┐
 │                     │                      │          │
 │                     │                      │<─────────┘
 │                     │                      │
 │                     │ Redirect to Phase 2  │
 │                     │ sign-in              │
 │                     │<─────────────────────│
 │                     │                      │
 │  Navigate to        │                      │
 │  Phase 2 sign-in    │                      │
 │<────────────────────│                      │
 │                     │                      │
```

---

## Implementation Details

### Frontend: Read JWT from Cookie

**File**: `/lib/auth/session.ts`

```typescript
import { cookies } from 'next/headers';

export async function getJWTToken(): Promise<string | null> {
  const cookieStore = cookies();
  const sessionCookie = cookieStore.get('better-auth.session_token');

  if (!sessionCookie) {
    return null;
  }

  // Just return the token - backend will verify it
  return sessionCookie.value;
}

export async function isAuthenticated(): Promise<boolean> {
  const token = await getJWTToken();
  return token !== null;
}
```

**Key Points**:
- ✅ Reads cookie value
- ❌ Does NOT decode JWT
- ❌ Does NOT verify JWT signature
- ❌ Does NOT check expiration

### Frontend: Middleware

**File**: `middleware.ts`

```typescript
import { NextRequest, NextResponse } from "next/server"

export async function middleware(request: NextRequest) {
  const sessionCookie = request.cookies.get('better-auth.session_token');

  // Protect chat and analytics routes
  if (request.nextUrl.pathname.startsWith("/chat") ||
      request.nextUrl.pathname.startsWith("/analytics")) {
    if (!sessionCookie) {
      // Redirect to Phase 2 login
      return NextResponse.redirect(new URL("/sign-in", request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/chat/:path*", "/analytics/:path*"]
}
```

**Key Points**:
- ✅ Checks if cookie exists
- ❌ Does NOT verify JWT validity
- Redirects to Phase 2 sign-in if cookie missing

### Frontend: API Client with JWT

**File**: `/lib/api/client.ts`

```typescript
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // Get JWT token from cookie (server-side)
  const token = await getJWTToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Send JWT to backend
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

**Key Points**:
- ✅ Extracts JWT from cookie
- ✅ Sends JWT in Authorization header
- ❌ Does NOT verify JWT

### Backend: JWT Verification

**File**: `app/core/auth.py` (Phase 3 Backend)

```python
from fastapi import Depends, HTTPException
from app.core.auth import get_current_user

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # Verifies JWT
):
    # Backend checks user_id matches JWT claims
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Process request...
```

**Key Points**:
- ✅ Verifies JWT signature
- ✅ Checks expiration
- ✅ Validates user_id matches JWT subject
- ✅ Returns 403 if mismatch

---

## Session Cookie Properties

```
Set-Cookie: better-auth.session_token=<JWT>;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/;
  Domain=.yourdomain.com;
  Max-Age=604800
```

**Properties**:
- `HttpOnly`: Prevents JavaScript access (XSS protection)
- `Secure`: Only sent over HTTPS in production
- `SameSite=Lax`: CSRF protection
- `Domain`: Must be shared between Phase 2 and Phase 3
- `Max-Age=604800`: 7 days (configured in Phase 2)

**Critical**: Phase 2 and Phase 3 must be on the same domain for cookie sharing.

---

## Security Considerations

### 1. Frontend Responsibilities

**Phase 3 Frontend**:
- ✅ Check if JWT cookie exists (for route protection)
- ✅ Extract JWT token from cookie
- ✅ Send JWT in Authorization header to backend
- ❌ Does NOT verify JWT (backend handles this)

### 2. Backend Responsibilities

**Phase 3 Backend**:
- ✅ Verify JWT signature using Phase 2 JWKS endpoint
- ✅ Check JWT expiration
- ✅ Validate user_id matches JWT subject
- ✅ Return 401 if JWT invalid
- ✅ Return 403 if user_id mismatch

### 3. Trust Model

- **Phase 2**: Trusted authentication authority
- **Phase 3 Frontend**: Untrusted (just passes JWT)
- **Phase 3 Backend**: Verifies all claims

### 4. Attack Scenarios

| Attack | Mitigation |
|--------|------------|
| XSS (steal JWT) | httpOnly cookie prevents JavaScript access |
| CSRF | SameSite=Lax cookie attribute |
| JWT tampering | Backend verifies signature |
| Expired JWT | Backend checks expiration |
| User ID spoofing | Backend validates user_id matches JWT subject |
| Cookie theft | HTTPS only, Secure flag |

---

## Error Handling

### Frontend Errors

| Scenario | Action |
|----------|--------|
| Cookie missing | Redirect to Phase 2 sign-in |
| API returns 401 | Redirect to Phase 2 sign-in (session expired) |
| API returns 403 | Show "Access denied" error |

### Backend Errors

| Scenario | HTTP Status | Error Code | User Message |
|----------|-------------|------------|--------------|
| Missing Authorization header | 401 | UNAUTHORIZED | "Authentication required" |
| Invalid JWT signature | 401 | UNAUTHORIZED | "Invalid session" |
| Expired JWT | 401 | UNAUTHORIZED | "Session expired. Please sign in again." |
| User ID mismatch | 403 | FORBIDDEN | "Access denied" |

---

## Environment Variables

### Phase 3 Frontend

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8001

# No Better Auth environment variables needed
# Phase 3 reads existing Phase 2 session cookies
```

### Phase 3 Backend

```bash
# .env
BETTER_AUTH_URL=http://localhost:3000  # Phase 2 URL for JWKS
DATABASE_URL=postgresql://...  # Shared Neon database
```

**Note**: No `BETTER_AUTH_SECRET` needed in Phase 3 - backend fetches JWKS from Phase 2.

---

## Testing Checklist

- [ ] User authenticated in Phase 2 can access Phase 3 chat
- [ ] User not authenticated in Phase 2 redirected to Phase 2 sign-in
- [ ] JWT sent in Authorization header to backend
- [ ] Backend verifies JWT signature correctly
- [ ] Backend rejects expired JWT (401)
- [ ] Backend rejects tampered JWT (401)
- [ ] Backend rejects user_id mismatch (403)
- [ ] Session persists across Phase 2 and Phase 3
- [ ] Sign-out in Phase 2 clears Phase 3 access
- [ ] Same domain cookie sharing works

---

## Troubleshooting

### Issue: "Session not found" in Phase 3

**Cause**: Cookie not accessible to Phase 3

**Solution**:
- Ensure Phase 2 and Phase 3 on same domain
- Check cookie Domain attribute includes both
- Verify cookie Path is `/` (accessible to all routes)

### Issue: "Invalid token signature" in backend

**Cause**: Backend cannot verify JWT from Phase 2

**Solution**:
- Verify `BETTER_AUTH_URL` points to Phase 2
- Check Phase 2 JWKS endpoint is accessible: `GET /api/auth/.well-known/jwks.json`
- Ensure Phase 2 Better Auth is running

### Issue: "User ID mismatch" error

**Cause**: Frontend sending wrong user_id in API path

**Solution**:
- Extract user_id from JWT claims (backend does this)
- Frontend should use user_id from session, not hardcode

### Issue: Cookie not shared between Phase 2 and Phase 3

**Cause**: Different domains or incorrect cookie configuration

**Solution**:
- Deploy Phase 2 and Phase 3 on same domain (e.g., `app.yourdomain.com`)
- Or use subdomains with shared cookie domain (e.g., `.yourdomain.com`)
- Check cookie Domain attribute in browser DevTools

---

## References

- [Better Auth Documentation](https://www.better-auth.com/)
- [Better Auth JWT Plugin](https://www.better-auth.com/docs/plugins/jwt)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Phase 3 Backend JWT Verification](../../Phase-3/backend/app/core/auth.py)
