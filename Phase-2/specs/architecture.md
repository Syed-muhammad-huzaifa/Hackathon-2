# System Architecture – Hackathon II  
**Phase II: Full-Stack Web Application**  
**The Evolution of Todo – From CLI to Secure Multi-User Dashboard-Driven Web App**

## 1. Architecture Overview

This architecture defines a **modern, secure, production-grade full-stack todo application** for Hackathon II (Panaversity).  

It follows a **layered client-server REST architecture** with:

- **Public zone** → Landing page + dedicated authentication flows
- **Protected zone** → Single Dashboard route containing **all authenticated functionality**
- Strict **user data isolation** at API and database level
- JWT-based authentication (Better Auth on frontend, verification on backend)
- **Integrated analytics** inside the dashboard (counts, completion rates, basic visualizations)
- Strong foundation for future phases: AI chatbot integration (Phase III), Kubernetes orchestration (Phase IV), event-driven features (Phase V)

Core user journey:
1. Visitor lands on **public landing page** (marketing-style intro + prominent Sign Up / Sign In buttons)
2. Clicks Sign Up or Sign In → navigates to dedicated pages
3. Successful authentication → immediate redirect to **/dashboard**
4. All task management, filtering, searching, sorting, and analytics happen **inside the dashboard**

Design principles (expert perspective):
- Single source of truth for authenticated experience → Dashboard as the "control center"
- Progressive enhancement → Server Components for initial loads, Client Components for interactivity
- Security-first → Row-level security + JWT path validation
- Performance → Indexed queries, minimal client-side state
- Extensibility → Dashboard layout supports future tabs/sections (chatbot, settings, advanced analytics)

## 2. High-Level Architecture Diagram 
┌───────────────────────────────────────┐
│         Public Zone (Unauthenticated) │
│                                       │
│   Landing Page (/)                    │
│   • Hero section, app value prop      │
│   • Sign Up / Sign In prominent CTAs  │
└──────────────────────┬────────────────┘
│ HTTPS
▼
┌───────────────────────────────────────┐           ┌───────────────────────────────────────┐
│  Sign Up Page (/signup)               │◄─────────►│  Backend – FastAPI                    │
│  Sign In Page (/signin)               │  REST API │  • JWT Verification Middleware       │
│  • Better Auth forms                  │           │  • SQLModel ORM & Aggregations        │
│  • Redirect to /dashboard on success  │           │  • Task CRUD + Analytics Endpoints    │
└───────────────────────────────────────┘           │  • Strict user_id ownership checks     │
└───────────────────────┬───────────────┘
│
▼
┌─────────────────────────────┐
│  Neon Serverless PostgreSQL │
│  • users table (Better Auth)│
│  • tasks table (user_id FK) │
└─────────────────────────────┘
After Login ──►
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Protected Dashboard (/dashboard)                              │
│                                                                                               │
│  • Dashboard Layout (sidebar/top nav with logout, user info)                                  │
│  • Task Management Area:                                                                      │
│    - Task List (view, inline edit, delete buttons, complete toggle)                           │
│    - Add Task Form (floating or top section)                                                  │
│    - Filters (status, priority), Sort (date, title), Search bar                               │
│  • Analytics Widgets Section:                                                                 │
│    - Cards: Total Tasks, Pending, Completed, Completion %                                     │
│    - Simple Chart: Pie/Bar showing completion distribution                                    │
│    - Optional: Tasks over time (line chart – last 7 days)                                     │
│                                                                                               │
└───────────────────────────────────────────────────────────────────────────────────────────────┘

## 3. Detailed Component Breakdown

### 3.1 Frontend (Next.js – Phase-2/frontend/)

**Technologies**:
- Next.js 16+ (App Router)
- TypeScript (strict)
- Tailwind CSS
- Better Auth (JWT issuance)
- Recharts or Chart.js for analytics visualizations
- shadcn/ui or custom components

**Route Structure**:
- `/` → Landing page (public)
- `/signup` → Dedicated sign-up page
- `/signin` → Dedicated sign-in page
- `/dashboard` → Protected dashboard (all features live here)

**Dashboard Features (all in one route)**:
- Task CRUD UI (list + form + actions)
- Filter controls (dropdowns, toggles)
- Sort options
- Keyword search input
- Analytics cards & charts (fetched via API)

**Protection**:
- Middleware (`middleware.ts` at root) checks JWT/session → redirects unauthenticated to `/signin`

**Folder Structure**:
frontend/
├── app/
│   ├── layout.tsx                 # Root layout (public)
│   ├── page.tsx                   # Landing page (/)
│   ├── signup/
│   │   └── page.tsx
│   ├── signin/
│   │   └── page.tsx
│   └── dashboard/
│       ├── layout.tsx             # Protected layout (nav, sidebar, logout)
│       └── page.tsx               # Dashboard content (tasks + analytics)
├── components/
│   ├── landing/                   # Hero, CTA buttons
│   ├── auth/                      # SignUpForm, SignInForm
│   └── dashboard/
│       ├── TaskList.tsx
│       ├── TaskForm.tsx
│       ├── FilterControls.tsx
│       ├── AnalyticsCards.tsx
│       └── CompletionChart.tsx
├── lib/
│   └── api.ts                     # API client with JWT
└── CLAUDE.md

### 3.2 Backend (FastAPI – Phase-2/backend/)

**Endpoints**:
- Task CRUD: `/api/{user_id}/tasks`, `/api/{user_id}/tasks/{id}`, etc.
- Analytics: `/api/{user_id}/analytics` (returns JSON with counts, completion %, etc.)

**Middleware**: JWT verification + path user_id validation

**Folder Structure**:

### 3.3 Database (Neon Serverless PostgreSQL)

- Schema unchanged
- Supports fast analytics via indexed queries (COUNT, GROUP BY completed, date_trunc for time-based stats)

## 4. Authentication & Flow Summary

1. Visitor → Landing page → Sign Up/Sign In CTA
2. Auth page → Better Auth → JWT issued → redirect to `/dashboard`
3. Middleware protects dashboard → verifies JWT
4. Dashboard loads → fetches tasks + analytics data
5. All interactions stay in dashboard

## 5. Non-Functional Highlights

- **Security**: JWT + row-level filters, input validation
- **Performance**: Aggregates cached if needed (future), Neon auto-scale
- **UX**: Responsive, loading skeletons, toast notifications
- **Observability**: OpenAPI docs, structured logging
- **DevOps**: Monorepo, docker-compose local, Vercel frontend

## Key Specifications
1. @specs/overview.md - Overview about the project
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/database/schema.md - Database schema and relationships
6. @specs/ui/components.md - React component library
7. @specs/ui/pages.md - Next.js pages and routing

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md