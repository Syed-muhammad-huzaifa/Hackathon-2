# Implementation Plan: Todo Frontend Application

**Branch**: `003-todo-frontend` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-frontend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Next.js 15 frontend application for the Todo backend with landing page, authentication (Better Auth), dashboard with task CRUD operations, and analytics charts. The application must integrate with the existing Phase-2 backend API, maintain strict type safety, and provide a responsive mobile-first experience.

## Technical Context

**Language/Version**: TypeScript (strict mode), Next.js 15 (App Router)
**Primary Dependencies**: Next.js 15, Tailwind CSS, Better Auth (JWT plugin), shadcn/ui, Recharts, Lucide Icons, Framer Motion (animations), next/font (premium typography)
**Storage**: N/A (frontend consumes backend REST API at `/api/{user_id}/tasks`)
**Testing**: Vitest + React Testing Library for component tests, Playwright for E2E tests
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - last 2 versions), mobile-first responsive design
**Project Type**: Web (frontend only, integrates with existing backend)
**Performance Goals**: Initial page load < 3s on 3G, dashboard load < 2s, task operations < 1s, chart rendering < 1s, smooth 60fps animations
**Constraints**: Mobile-first responsive (320px-1920px), WCAG AA accessibility, zero TypeScript 'any' types, httpOnly cookies for JWT storage, dark theme primary interface, premium UI with glassmorphism effects
**Scale/Scope**: 4 user stories (P1: Auth, P2: CRUD, P3: Analytics), 48 functional requirements (including 10 premium UI/UX requirements), 5 main pages (landing, sign-up, sign-in, dashboard, analytics section)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-First Integrity (NON-NEGOTIABLE)
- **Status**: PASS
- **Evidence**: Complete specification exists at `specs/003-todo-frontend/spec.md` with 38 functional requirements, 4 user stories, and 10 success criteria
- **Compliance**: All code will reference spec via `@spec: specs/003-todo-frontend/spec.md (FR-XXX)` comments

### ✅ Multi-tenancy (ZERO-TOLERANCE)
- **Status**: PASS
- **Evidence**:
  - FR-009: "System MUST protect dashboard routes and redirect unauthenticated users"
  - Spec explicitly states: "Frontend MUST never allow manual user_id manipulation in URLs or requests"
  - All API calls will use authenticated user's ID from JWT, never from user input
- **Compliance**:
  - User ID extracted from JWT token only (never from URL params or form input)
  - API client will automatically inject authenticated user_id into requests
  - No manual user_id editing in UI

### ✅ Type Safety (NON-NEGOTIABLE)
- **Status**: PASS
- **Evidence**: Technical Constraints specify "TypeScript (strict mode) with zero 'any' types"
- **Compliance**:
  - `tsconfig.json` with `strict: true`, `noImplicitAny: true`
  - All API responses typed with Zod schemas
  - All component props fully typed
  - ESLint rule: `@typescript-eslint/no-explicit-any: error`

### ✅ Security Standards
- **Status**: PASS
- **Evidence**:
  - FR-003: Better Auth integration
  - Security & Privacy section: "JWT tokens must be stored securely (httpOnly cookies preferred)"
  - FR-005: Email format validation
  - FR-006: Clear error messages for auth failures
- **Compliance**:
  - Better Auth configured with httpOnly cookies (no localStorage)
  - All API calls include authentication tokens
  - Input validation on all forms (client-side UX + backend security)
  - HTTPS enforced in production

### ✅ Accessibility Standards
- **Status**: PASS
- **Evidence**: FR-034: "System MUST be fully responsive and work on mobile, tablet, and desktop"
- **Compliance**:
  - Semantic HTML elements (`<nav>`, `<main>`, `<button>`, `<form>`)
  - ARIA labels on interactive elements
  - Keyboard navigation support (Tab, Enter, Escape)
  - WCAG AA contrast ratios (4.5:1 for text)
  - Focus indicators visible

### ✅ Responsive Design
- **Status**: PASS
- **Evidence**:
  - FR-034: "fully responsive and work on mobile, tablet, and desktop screen sizes"
  - SC-007: "Application is fully functional on mobile devices (320px width minimum) and desktop (1920px width)"
  - FR-047: "System MUST follow mobile-first design principles with touch-optimized interactions"
- **Compliance**:
  - Mobile-first Tailwind CSS approach
  - Breakpoints: mobile (default), tablet (md:), desktop (lg:, xl:)
  - Touch-friendly targets (min 44x44px)
  - Responsive charts with proper scaling

### ✅ Premium UI/UX Design (NEW)
- **Status**: PASS
- **Evidence**:
  - FR-039: Dark theme as primary interface
  - FR-040: Premium typography (Inter, Geist, SF Pro)
  - FR-041: Smooth animations and transitions
  - FR-042: Glassmorphism/neumorphism design patterns
  - FR-043: Gradient accents and modern color palettes
  - FR-044: Micro-interactions (ripples, skeletons, animations)
  - FR-045: Unique and creative layout
  - FR-046: Custom iconography (Lucide Icons)
  - FR-048: Background patterns and mesh effects
- **Compliance**:
  - Dark theme with deep backgrounds (#0a0a0a, #111111)
  - Premium fonts loaded via next/font optimization
  - Framer Motion for smooth animations (60fps target)
  - Glassmorphism: backdrop-blur + rgba transparency
  - Gradient buttons and accent elements
  - Lucide Icons for consistent iconography
  - Bento grid layout for dashboard uniqueness
  - Animated gradient backgrounds with mesh effects

### ⚠️ N-Tier Architecture (NON-NEGOTIABLE)
- **Status**: NOT APPLICABLE (Frontend)
- **Rationale**: N-Tier architecture applies to backend (Routes → Services → Repositories). Frontend uses component-based architecture with clear separation:
  - **Presentation Layer**: React components (pages, UI components)
  - **Data Layer**: API client services (fetch wrappers)
  - **State Layer**: React hooks and context (if needed)
- **Compliance**: Components will not contain API logic; API calls isolated in service modules

### ⚠️ Asynchronous First (NON-NEGOTIABLE)
- **Status**: PARTIAL COMPLIANCE (Frontend context)
- **Rationale**: Frontend uses async/await for all API calls. React Server Components are async by default in Next.js 15 App Router.
- **Compliance**:
  - All API calls use `async/await` with fetch or httpx
  - Server Components use async data fetching
  - Client Components use React hooks (useEffect, useSWR) for async operations
  - No blocking operations in render paths

### Constitution Compliance Summary
- **Total Gates**: 9
- **Passed**: 7
- **Not Applicable**: 2 (backend-specific)
- **Failed**: 0
- **Overall Status**: ✅ COMPLIANT

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-frontend/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions, patterns)
├── data-model.md        # Phase 1 output (frontend state shape, API contracts)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (API client interfaces, Zod schemas)
│   ├── api-client.ts    # Type-safe API client
│   ├── auth.schema.ts   # Auth request/response types
│   └── task.schema.ts   # Task request/response types
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Phase-2/frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── (auth)/            # Auth route group
│   │   │   ├── sign-up/
│   │   │   │   └── page.tsx
│   │   │   └── sign-in/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/       # Protected route group
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx     # Dashboard layout with nav
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   └── globals.css        # Tailwind imports
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   └── dialog.tsx
│   │   ├── auth/             # Auth-specific components
│   │   │   ├── sign-up-form.tsx
│   │   │   └── sign-in-form.tsx
│   │   ├── tasks/            # Task-specific components
│   │   │   ├── task-list.tsx
│   │   │   ├── task-card.tsx
│   │   │   ├── task-form.tsx
│   │   │   └── task-delete-dialog.tsx
│   │   ├── analytics/        # Analytics components
│   │   │   ├── status-chart.tsx
│   │   │   ├── priority-chart.tsx
│   │   │   └── trend-chart.tsx
│   │   └── layout/           # Layout components
│   │       ├── header.tsx
│   │       ├── nav.tsx
│   │       └── footer.tsx
│   ├── lib/                  # Utilities and services
│   │   ├── api/             # API client
│   │   │   ├── client.ts    # Base API client
│   │   │   ├── auth.ts      # Auth endpoints
│   │   │   └── tasks.ts     # Task endpoints
│   │   ├── auth/            # Better Auth setup
│   │   │   └── client.ts    # Better Auth client config
│   │   ├── schemas/         # Zod validation schemas
│   │   │   ├── auth.ts
│   │   │   └── task.ts
│   │   └── utils.ts         # Helper functions
│   └── types/               # TypeScript types
│       ├── api.ts           # API response types
│       ├── auth.ts          # Auth types
│       └── task.ts          # Task types
├── public/                  # Static assets
│   ├── images/
│   └── icons/
├── tests/                   # Test files
│   ├── components/          # Component tests
│   ├── integration/         # Integration tests
│   └── e2e/                # Playwright E2E tests
├── .env.example            # Environment variables template
├── .env.local              # Local environment (gitignored)
├── next.config.js          # Next.js configuration
├── tailwind.config.ts      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
├── package.json            # Dependencies
└── README.md               # Setup instructions
```

**Structure Decision**: Web application (frontend only) using Next.js 15 App Router with route groups for organization. The structure follows Next.js conventions with clear separation between pages (app/), reusable components (components/), business logic (lib/), and types (types/). Better Auth integration lives in lib/auth/, and API client in lib/api/.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution requirements are met or not applicable to frontend architecture.

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion*

### ✅ All Gates Still Pass

**Design Artifacts Created**:
- `research.md`: Technology decisions documented (Better Auth, Recharts, React Hook Form, native fetch)
- `data-model.md`: Frontend state shape and API contracts defined
- `contracts/`: TypeScript interfaces and Zod schemas for type safety
- `quickstart.md`: Setup instructions for developers

**Constitution Compliance Verified**:
- ✅ **Spec-First Integrity**: All contracts reference spec requirements (FR-XXX)
- ✅ **Type Safety**: Zod schemas provide runtime validation + TypeScript types (zero 'any' types)
- ✅ **Security**: httpOnly cookies, input validation, HTTPS enforcement documented
- ✅ **Multi-tenancy**: API client automatically injects user_id from JWT (no manual manipulation)
- ✅ **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation in design
- ✅ **Responsive**: Mobile-first Tailwind approach with defined breakpoints

**No New Violations Introduced**: Design maintains all constitution requirements.

---

## Phase Completion Summary

### Phase 0: Research ✅
- **Output**: `research.md`
- **Decisions**: 6 technology choices documented with rationale
- **Status**: All NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts ✅
- **Output**: `data-model.md`, `contracts/` (3 files), `quickstart.md`
- **Contracts**: TypeScript interfaces + Zod schemas for auth and tasks
- **API Client**: Type-safe client with automatic JWT injection
- **Status**: Ready for implementation

### Next Phase
Run `/sp.tasks` to generate actionable implementation tasks based on this plan.
