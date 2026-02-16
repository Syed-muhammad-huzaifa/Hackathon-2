# UI Pages Specification  
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. Purpose

This document defines the structure, layout, routing, and high-level content of every major page in the Todo web application for Phase II.

All pages are built with **Next.js 16+ App Router** and follow these principles:
- Clear separation between **public** (unauthenticated) and **protected** (authenticated) areas
- Protected pages redirect unauthenticated users to `/signin`
- Dashboard is the single central hub for all authenticated features (task CRUD + analytics)
- Use **Server Components** for data fetching where possible
- Use **Client Components** only for interactive elements
- Responsive design (mobile-first with Tailwind CSS)
- Dark mode support
- Consistent navigation, error handling, and loading states

## 2. Routing & Protection Summary

| Route          | Access        | Layout Used              | Redirect If Unauth | Main Content / Purpose                              |
|----------------|---------------|--------------------------|---------------------|-----------------------------------------------------|
| `/`            | Public        | Root Layout              | —                   | Landing / marketing page                            |
| `/signup`      | Public        | Root Layout              | —                   | New user registration form                          |
| `/signin`      | Public        | Root Layout              | —                   | Existing user login form                            |
| `/dashboard`   | Protected     | Dashboard Layout         | Redirect to /signin | All task management + analytics (core app experience) |

**Protection Mechanism**  
- Implemented via `middleware.ts` at project root  
- Checks valid JWT/session (via Better Auth)  
- If missing/invalid → redirect to `/signin?from=/dashboard`  
- Preserves intended destination for post-login redirect

## 3. Page Details

### 3.1 Landing Page – `/` (Root)

**Layout**: Root Layout (`app/layout.tsx`)  
**Purpose**: Public entry point – attract users, explain value, drive to auth

**Key Sections**:
- Hero / Header
  - Large headline: "Todo – Simple, Secure Task Management"
  - Subheadline: "Organize your life privately with a modern web app"
  - Two prominent CTAs: "Get Started (Sign Up)" → /signup, "Sign In" → /signin
- Features / Benefits (3–4 cards or list)
  - "Personal task lists – only you can see them"
  - "Easy CRUD operations"
  - "Clean dashboard with analytics"
  - "Built with modern tech (Next.js + FastAPI)"
- Footer: Copyright, links (if any), current year

**Visual Style**:
- Full-width hero with gradient or subtle background
- Centered content on mobile
- Responsive grid for benefits section

**Interactivity**:
- No data fetching
- CTA buttons navigate directly

### 3.2 Sign Up Page – `/signup`

**Layout**: Root Layout  
**Purpose**: Allow new users to create an account

**Content & Structure**:
- Centered card/form container
- Page title: "Create Your Account"
- Form fields (via AuthForm component):
  - Name (optional input)
  - Email (required, email validation)
  - Password (required, min length, show/hide toggle)
  - Submit button: "Sign Up"
- Link below form: "Already have an account? Sign In" → /signin
- Loading state: spinner on submit
- Success → redirect to /dashboard + toast "Account created!"
- Errors → field-specific messages + toast for general errors

**SEO/Meta**:
- Title: "Sign Up – Todo App"
- Description: "Create a free account to start managing your tasks securely"

### 3.3 Sign In Page – `/signin`

**Layout**: Root Layout  
**Purpose**: Allow existing users to log in

**Content & Structure**:
- Centered card/form
- Page title: "Sign In to Your Account"
- Form fields:
  - Email (required)
  - Password (required, show/hide)
  - Submit button: "Sign In"
- Link below: "Don't have an account? Sign Up" → /signup
- Optional: "Forgot password?" (out of scope for Phase II)
- Loading + success/error handling same as signup
- Success → redirect to /dashboard + toast "Welcome back!"

**SEO/Meta**:
- Title: "Sign In – Todo App"

### 3.4 Dashboard Page – `/dashboard`

**Layout**: Dashboard Layout (`app/dashboard/layout.tsx`)  
**Purpose**: The only protected page – contains **all** authenticated functionality

**Dashboard Layout Structure**:
- Top Navbar / Header
  - App logo / name (clickable → /dashboard)
  - User avatar / name dropdown
  - Logout button
  - Theme toggle (light/dark/system)
- Optional Sidebar (collapsible on mobile)
  - Navigation items (future: Settings, Profile, Help)
  - Current: just "Dashboard" active
- Main Content Area
  - Full-width responsive container

**Main Content Sections (in dashboard/page.tsx)**:
1. **Header / Welcome**
   - "Welcome back, {user.name || 'User'}!"
   - Quick stats summary (total tasks today / pending)

2. **Add Task Section**
   - Prominent TaskForm (inline or floating action button)
   - Title input + description textarea + submit

3. **Task Controls Bar**
   - Filter dropdown (All / Pending / Completed)
   - Sort dropdown (Newest / Oldest / A–Z / Z–A)
   - Search input (debounced)

4. **Task List Area**
   - <TaskList /> component
   - Shows tasks or <EmptyState /> if none
   - Infinite scroll or pagination (simple offset/limit for Phase II)

5. **Analytics Section** (below or sidebar)
   - <AnalyticsCards /> grid (total, pending, completed, %)
   - <CompletionChart /> (pie or bar)

**Loading & Error States**:
- Full-page skeleton on initial load
- Per-section skeletons for refetches
- Error boundary + retry button if API fails
- Toast for success/error feedback

**SEO/Meta**:
- Title: "Dashboard – Todo App"
- Noindex (private page) – add `<meta name="robots" content="noindex" />`

## 4. Global UI Patterns

- Consistent padding/margin (4–6 spacing scale)
- Max-width container (e.g., 7xl or 6xl) for readability
- Toasts positioned top-right
- Modals/dialogs for edit + delete confirm
- Relative time formatting (e.g., "3 hours ago") via date-fns

## 5. Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/database/schema.md - Database schema and relationships
6. @specs/ui/components.md - React component library
7. @specs/overview.md - Overview about the project

## 6. References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

**This file is the single source of truth for page-level UI structure in Phase II.**  
All page/layout code generation must reference this specification.
