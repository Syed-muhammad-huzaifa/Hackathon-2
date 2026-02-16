# Feature: Authentication  
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. Purpose

This specification defines the complete authentication and authorization system for the Todo web application in Phase II.

The system must provide:
- Secure user registration (signup)
- Secure user login (signin)
- Session/token management
- Strict user data isolation across the entire application
- Protection of all private routes and API endpoints

All authentication logic follows **spec-driven development** principles: this file is the source of truth.  
Implementation must be generated via Claude Code referencing this spec.

## 2. User Stories

As a **visitor** (unauthenticated user),  
I want to see a welcoming landing page with clear options to sign up or sign in,  
so that I can quickly decide to create an account or log in.

As a **new user**,  
I want to create an account with email and password,  
so that I can start managing my personal todo list.

As a **registered user**,  
I want to securely sign in with my email and password,  
so that I can access my own tasks and data.

As an **authenticated user**,  
I want my session/token to remain valid for a reasonable period,  
so that I don't have to log in repeatedly during a session.

As an **authenticated user**,  
I want to log out securely,  
so that I can end my session on shared or public devices.

As the **application**,  
I want to enforce that users can only see and modify **their own tasks**,  
so that data privacy and security are maintained.

## 3. Acceptance Criteria

### 3.1 Public Landing Page
- Accessible without authentication at route `/`
- Displays app name, short description, benefits (e.g., "Organize your life securely")
- Contains prominent buttons/links:  
  - "Sign Up" → `/signup`  
  - "Sign In" → `/signin`
- Responsive and mobile-friendly
- No task-related content or data visible

### 3.2 Sign Up (Registration)
- Dedicated route: `/signup`
- Form fields:  
  - Email (required, valid format)  
  - Password (required, min 8 chars, complexity rules enforced by Better Auth)  
  - Name (optional)
- Client-side validation (email format, password length)
- On submit:  
  - Calls Better Auth signup API  
  - Creates user record in `users` table  
  - Issues JWT token  
  - Sets session cookie  
  - Redirects to `/dashboard` on success
- Success toast/notification: "Account created successfully"
- Error handling:  
  - Email already exists → clear message "Email is already registered"  
  - Invalid input → show field-specific errors

### 3.3 Sign In (Login)
- Dedicated route: `/signin`
- Form fields:  
  - Email (required)  
  - Password (required)
- Client-side validation
- On submit:  
  - Calls Better Auth signin API  
  - Verifies credentials against `users` table  
  - Issues JWT token on success  
  - Sets session cookie  
  - Redirects to `/dashboard`
- Success toast: "Welcome back!"
- Error handling:  
  - Invalid credentials → "Invalid email or password"  
  - Rate limiting hint if applicable (future)

### 3.4 Session & Token Management
- JWT token issued by Better Auth  
  - Algorithm: HS256  
  - Payload includes at minimum: `user_id`, `email`, `exp` (expiry)
  - Expiry: 7 days (configurable via Better Auth)
- Token stored securely:  
  - httpOnly cookie preferred (for security)  
  - Or localStorage with fallback protection (if cookie not viable)
- Token automatically attached to every API request via `/lib/api.ts`
- Token refresh: handled by Better Auth session management (optional silent refresh)

### 3.5 Protected Routes & Dashboard Access
- Route `/dashboard` and all sub-routes are protected
- Protection mechanism:  
  - Next.js middleware (`middleware.ts`) checks valid JWT/session  
  - If invalid/missing → redirect to `/signin` with optional `?from=/dashboard` for return URL
- All task-related UI and API calls require valid authentication

### 3.6 Logout
- Button/link in dashboard navigation (top-right or sidebar)
- On click:  
  - Calls Better Auth logout (clears session/cookie)  
  - Redirects to `/` (landing page) or `/signin`
- Success toast: "You have been logged out"

### 3.7 User Data Isolation (Critical)
- **Frontend**:  
  - All API calls include authenticated user's `user_id` in path  
  - Never allow user to manually change `user_id` in URL or requests
- **Backend (FastAPI)**:  
  - JWT middleware extracts `user_id` from token  
  - Every endpoint path contains `{user_id}`  
  - Middleware **must** verify: `path.user_id === jwt.user_id` → else 403 Forbidden  
  - All database queries **must** include `WHERE user_id = :authenticated_user_id`
- Result: Impossible for one user to access or modify another user's tasks

### 3.8 Error & Security Handling
- 401 Unauthorized → "Please sign in to continue" + redirect to `/signin`
- 403 Forbidden → "You do not have permission to access this resource"
- Rate limiting on login attempts (handled by Better Auth or backend middleware)
- Passwords never logged or exposed
- HTTPS enforced in production (Vercel/Render)

## 4. Tech Stack & Integration

- **Frontend**: Better Auth (with JWT plugin)  
  - Handles signup, signin, session, logout
- **Backend**: Custom JWT verification middleware  
  - Uses `pyjwt` library  
  - Validates against same `BETTER_AUTH_SECRET` env var
- **Shared Secret**: `BETTER_AUTH_SECRET` – must be identical in frontend & backend `.env`
- **Database**: `users` table managed entirely by Better Auth

## 5. Edge Cases & Security Considerations

- Invalid JWT signature → 401
- Expired token → 401
- user_id mismatch → 403
- Attempt to access `/dashboard` without login → redirect to `/signin`
- Tampering with path `user_id` → 403
- Multiple devices: session valid across tabs/devices until expiry/logout
- Password reset: out of scope for Phase II

## 6. Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/api/rest-endpoints.md - Complete API endpoint documentation
4. @specs/database/schema.md - Database schema and relationships
5. @specs/ui/components.md - React component library
6. @specs/ui/pages.md - Next.js pages and routing
7. @specs/overview.md - Overview about the project

## 7. References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

**This specification is the single source of truth for authentication in Phase II.**  
All code generation for auth-related features must reference this file.
