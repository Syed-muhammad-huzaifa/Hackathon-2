# Research Report: AI Chatbot Frontend Technology Decisions

**Feature**: 001-chatbot-frontend
**Date**: 2026-02-21
**Status**: Complete

## Executive Summary

This document consolidates research findings for key technology decisions in the AI chatbot frontend. All critical decisions have been resolved with concrete implementation patterns.

## 1. Analytics Chart Library

**Decision**: **Recharts**

**Rationale**:
- Pure React components with declarative, intuitive API
- Excellent TypeScript support with full type definitions
- Built on D3 and SVG for crisp, scalable graphics
- Lightweight and performant for moderate datasets (1000 points)
- Highly customizable with granular control over styling
- Clean integration with Next.js 15 App Router

**Alternatives Considered**:
- **Tremor**: Built-in dark mode but larger bundle size, more opinionated
- **Chart.js**: Canvas-based, better for very large datasets (10k+), but overkill for our use case

**Implementation Pattern**:
```typescript
// Client component with "use client" directive
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Dark theme colors
const COLORS = ['#10b981', '#f59e0b', '#3b82f6', '#ef4444'];

<ResponsiveContainer width="100%" height={400}>
  <PieChart>
    <Pie
      data={data}
      innerRadius={80}
      outerRadius={120}
      dataKey="value"
      label
    >
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
      ))}
    </Pie>
    <Tooltip contentStyle={{ backgroundColor: '#1f2937', color: '#f3f4f6' }} />
    <Legend wrapperStyle={{ color: '#f3f4f6' }} />
  </PieChart>
</ResponsiveContainer>
```

**Chart Types Needed**:
- Donut chart for task status distribution (pending, completed, deleted)
- Line chart for task completion trends over time

**Performance Considerations**:
- Memoize data transformations with `useMemo`
- Use `ResponsiveContainer` for proper sizing
- SVG rendering handles 1000 data points efficiently

---

## 2. Phase 2 Session Integration

**Decision**: **Pass JWT Token from Phase 2 to Backend**

**Rationale**:
- Phase 2 already has Better Auth configured with JWT tokens
- Shared Neon database between Phase 2 and Phase 3
- Users are pre-authenticated via Phase 2
- Frontend just passes JWT to backend - no verification needed
- Backend (001-chatbot-backend) handles all JWT verification

**Authentication Flow**:
1. User is already authenticated in Phase 2 (JWT in httpOnly cookie)
2. Phase 3 frontend reads JWT from Phase 2 cookie
3. Phase 3 frontend sends JWT to backend in `Authorization: Bearer <token>` header
4. Phase 3 backend verifies JWT signature and claims
5. Backend processes request if JWT is valid

**Frontend Responsibilities**:
- ✅ Check if JWT cookie exists (for route protection)
- ✅ Extract JWT token from cookie
- ✅ Send JWT in Authorization header to backend
- ❌ Does NOT verify JWT (backend handles this)

**Implementation Pattern**:

**Read JWT from Cookie** (`/lib/auth/session.ts`):
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

**Middleware** (`middleware.ts`):
```typescript
import { NextRequest, NextResponse } from "next/server"
import { cookies } from 'next/headers';

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

**API Client with JWT** (`/lib/api/client.ts`):
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

**Client-Side Hook** (`/lib/hooks/useAuth.ts`):
```typescript
'use client';

import { useState, useEffect } from 'react';

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if session cookie exists
    fetch('/api/auth/check')
      .then(res => res.json())
      .then(data => {
        setIsAuthenticated(data.authenticated);
        setLoading(false);
      })
      .catch(() => {
        setIsAuthenticated(false);
        setLoading(false);
      });
  }, []);

  return { isAuthenticated, loading };
}

// API route to check authentication
// app/api/auth/check/route.ts
export async function GET() {
  const token = await getJWTToken();
  return Response.json({ authenticated: token !== null });
}
```

**Key Points**:
- **No JWT verification in frontend** - backend handles all verification
- **Simple cookie check** - frontend just checks if cookie exists
- **Pass-through pattern** - frontend passes JWT to backend unchanged
- **Backend verifies** - Phase 3 backend (001-chatbot-backend) verifies JWT signature, expiry, and claims
- **Same domain required** - Cookies must be accessible across Phase 2 and Phase 3

**Backend Verification** (already implemented in 001-chatbot-backend):
```python
# Backend verifies JWT
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

**Dependencies**:
- Phase 2 Better Auth must be running
- Session cookies must be accessible (same domain)
- Phase 3 backend must have JWT verification configured (already done)

**Recommendation**: Keep Phase 2 and Phase 3 on same domain for cookie sharing.

---

## 3. OpenAI ChatKit Integration

**Decision**: **Use OpenAI ChatKit** (not custom chat UI)

**Rationale**:
- Production-ready with streaming support out of the box
- Built-in authentication and session management
- Extensive theming and customization (matches dark theme requirements)
- Official OpenAI support and maintenance
- Integrates seamlessly with OpenAI Agents SDK (existing backend)
- Handles complex edge cases (reconnection, error handling)
- Dark mode and accessibility built-in
- Saves significant development time vs custom implementation

**Alternatives Considered**:
- **Custom Chat UI**: More control but requires building streaming, reconnection, error handling, accessibility from scratch

**Domain Allowlist Requirement** (CRITICAL):
- Must register domains in OpenAI dashboard: `https://platform.openai.com/settings/organization/security/domain-allowlist`
- Register production domain (e.g., `yourdomain.com`)
- Register development domain (`localhost:3000`)
- Obtain `domainKey` from dashboard

**Implementation Pattern**:

**Installation**:
```bash
npm install @openai/chatkit-react
```

**Client Component** (`/components/ChatInterface.tsx`):
```tsx
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatInterface() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        if (existing) {
          const res = await fetch('/api/chatkit/refresh', {
            method: 'POST',
            body: JSON.stringify({ token: existing }),
          });
          const { client_secret } = await res.json();
          return client_secret;
        }

        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY,
    },
    theme: {
      colorScheme: 'dark',
      color: {
        accent: { primary: '#3b82f6' },
      },
      radius: 'round',
      typography: {
        fontFamily: 'Inter, system-ui, sans-serif',
      },
    },
    composer: {
      placeholder: 'Ask me to create, update, or manage your tasks...',
    },
    startScreen: {
      greeting: 'Welcome to Task Manager AI!',
      prompts: [
        { name: 'Create Task', prompt: 'Create a task for tomorrow' },
        { name: 'List Tasks', prompt: 'Show my tasks for today' },
      ],
    },
  });

  return <ChatKit control={control} className="h-screen w-full" />;
}
```

**API Route** (`/app/api/chatkit/session/route.ts`):
```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const session = await getSession(request);

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Forward to FastAPI backend
  const response = await fetch(`${process.env.BACKEND_URL}/chatkit/session`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session.token}`,
    },
    body: JSON.stringify({ user_id: session.userId }),
  });

  const { client_secret } = await response.json();
  return NextResponse.json({ client_secret });
}
```

**Backend Integration** (FastAPI):
```python
from fastapi import FastAPI, Depends
from chatkit.server import ChatKitServer

@app.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user),
):
    context = {"user_id": user_id}
    result = await chatkit_server.process(await request.body(), context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")
```

**Message Format**:
- Uses Server-Sent Events (SSE) for streaming
- Request: `{ messages: [...], tools: [...] }`
- Response: Streamed events with `event: thread.message.item.created`

**Customization Options**:
- Dark theme support (built-in)
- Custom colors, fonts, radius, density
- Start screen with suggested prompts
- Header actions (settings, navigation)
- Composer placeholder text

**Known Limitations**:
- Requires domain allowlist registration (extra setup step)
- Must be client component (`'use client'` directive)
- SSE dependency (ensure proper proxy/load balancer support)
- OpenAI ecosystem lock-in

---

## 4. State Management Strategy

**Decision**: **React Server Components + Client Components with hooks**

**Rationale**:
- Next.js 15 App Router default pattern
- Server Components for initial data fetching
- Client Components for interactivity (chat, forms)
- No additional state management library needed for MVP
- ChatKit manages its own chat state internally

**Pattern**:
- Use `useSession()` hook for auth state
- Use ChatKit's internal state for chat messages
- Use React hooks (`useState`, `useEffect`) for analytics data
- Server Components for static content (landing page)

**Future Consideration**: If state complexity grows, consider Zustand or Jotai

---

## 5. API Client Strategy

**Decision**: **Native fetch with custom wrapper**

**Rationale**:
- Next.js 15 has enhanced fetch with automatic caching
- No additional dependencies needed
- Simple wrapper for error handling and auth headers
- TypeScript types for request/response

**Implementation Pattern**:
```typescript
// /lib/api/client.ts
export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    credentials: 'include', // Include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

---

## 6. Premium UI/UX Implementation

**Decision**: **Tailwind CSS + Framer Motion (optional)**

**Rationale**:
- Tailwind CSS for styling (already in tech stack)
- Glassmorphism via Tailwind utilities (`backdrop-blur`, `bg-opacity`)
- CSS animations for simple transitions
- Framer Motion for complex animations (optional, add if needed)

**Dark Theme Implementation**:
```typescript
// tailwind.config.ts
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        surface: '#1a1a1a',
        accent: '#3b82f6',
      },
    },
  },
}
```

**Glassmorphism Pattern**:
```tsx
<div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl">
  {/* Content */}
</div>
```

---

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | Next.js 15 (App Router) | Modern React framework, Server Components |
| **Language** | TypeScript (strict mode) | Type safety, better DX |
| **Styling** | Tailwind CSS | Utility-first, mobile-first, dark mode support |
| **Chat UI** | OpenAI ChatKit | Production-ready, streaming, customizable |
| **Authentication** | Phase 2 Better Auth (session reuse) | Pre-authenticated users, shared database, no auth UI needed |
| **Charts** | Recharts | React-native, TypeScript support, SVG rendering |
| **Icons** | Lucide React | Modern, customizable, tree-shakeable |
| **Validation** | Zod | TypeScript-first schema validation |
| **API Client** | Native fetch | Built-in, enhanced in Next.js 15 |
| **State Management** | React hooks + Server Components | Simple, no additional library needed |
| **Testing** | Vitest + React Testing Library | Fast, modern, React-focused |
| **E2E Testing** | Playwright | Reliable, cross-browser |

---

## Environment Variables Required

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8001
BACKEND_URL=http://localhost:8001

# Phase 2 Authentication (no setup needed - reads existing session)
# Session cookies automatically accessible if same domain

# OpenAI ChatKit
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key-from-openai

# Production
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Note**: No Better Auth environment variables needed - Phase 3 reads existing Phase 2 session cookies.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| ChatKit integration complexity | Thorough Phase 0 research complete, fallback to custom UI if needed |
| Phase 2 session integration | Test session reading thoroughly, coordinate with Phase 2 team, ensure same domain |
| Backend API availability | Mock API for local development, proper error handling |
| Performance with 100+ messages | Virtualized scrolling (ChatKit handles this), pagination |
| Mobile responsiveness | Mobile-first design, extensive testing on real devices |
| Domain allowlist setup | Document setup process, register localhost for development |
| Session cookie compatibility | Ensure Phase 2 and Phase 3 on same domain, test cookie access |

---

## Next Steps

1. ✅ Phase 0 research complete
2. → Phase 1: Design & Contracts
   - Create `data-model.md`
   - Create `contracts/` directory with API contracts
   - Create `quickstart.md` for developer setup
3. → Update agent context with new technologies
4. → Run `/sp.tasks` to generate implementation tasks

---

## References

- [Recharts Documentation](https://recharts.org/)
- [Better Auth Documentation](https://www.better-auth.com/)
- [OpenAI ChatKit GitHub](https://github.com/openai/chatkit-js)
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
