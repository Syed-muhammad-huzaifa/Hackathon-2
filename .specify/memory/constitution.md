<!--
Sync Impact Report:
Version: 1.0.0 (Initial constitution for Phase-2)
Modified Principles: N/A (initial version)
Added Sections: All sections (initial creation)
Removed Sections: None
Templates Status:
  ✅ plan-template.md - Aligned with constitution check requirements
  ✅ spec-template.md - Aligned with user story and requirements structure
  ✅ tasks-template.md - Aligned with test-first and phase-based approach
Follow-up TODOs: None
-->

# Phase-2 Todo Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Every line of code MUST originate from an explicit specification document. No code shall be written, modified, or suggested without a traceable reference to a specification file in `/specs/`.

**Rules:**
- All implementation work requires a `@specs/[file].md` reference in code comments
- Specifications are written BEFORE any code generation begins
- If a feature is not in specs → update specs first, then implement
- Code reviews MUST verify spec traceability for every change
- Spec files are the single source of truth; code is derivative

**Rationale:** Ensures intentional design, prevents scope creep, maintains documentation accuracy, and enables AI-assisted development with clear requirements.

### II. User Data Isolation (ZERO-TOLERANCE)

Every user's data MUST be completely isolated from all other users. No user shall ever access, view, modify, or delete another user's tasks under any circumstances.

**Rules:**
- Every database query MUST include `WHERE user_id = :authenticated_user_id`
- Every API endpoint path MUST contain `{user_id}` parameter
- Backend middleware MUST verify `path.user_id === jwt.user_id` → else 403 Forbidden
- Frontend MUST never allow manual `user_id` manipulation in URLs or requests
- All list/search/filter operations MUST be scoped to authenticated user only
- Database indexes MUST include `user_id` as first column for performance
- Return 404 (not 403) for non-owned resources to prevent existence leakage

**Rationale:** Privacy and security are non-negotiable. Data leakage destroys user trust and violates fundamental security principles.

### III. JWT Authentication & Authorization

All protected routes and API endpoints MUST enforce JWT-based authentication with strict token validation and user verification.

**Rules:**
- Better Auth issues JWT tokens on successful signup/signin
- Shared secret (`BETTER_AUTH_SECRET`) MUST be identical in frontend and backend
- Backend MUST verify: signature validity, token expiry, payload integrity
- Invalid/missing/expired tokens → 401 Unauthorized + redirect to `/signin`
- User ID mismatch between JWT and path → 403 Forbidden
- Tokens stored in httpOnly cookies (preferred) or secure localStorage
- Session validity: 7 days default (configurable)
- HTTPS enforced in production (no exceptions)
- Passwords MUST be hashed (handled by Better Auth)
- No secrets hardcoded in code or committed to git

**Rationale:** Secure authentication is the foundation of multi-user applications. Weak auth = complete system compromise.

### IV. API-First Design with Consistent Contracts

All backend endpoints MUST follow a consistent RESTful design with standardized request/response formats and proper HTTP semantics.

**Rules:**
- Base path: `/api/{user_id}/[resource]`
- Response format (success): `{ status: "success", data: {...}, message?: string, meta?: {...} }`
- Response format (error): `{ status: "error", code: string, message: string, details?: {...} }`
- HTTP status codes: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Server Error)
- All timestamps in ISO 8601 UTC format with Z suffix
- Input validation on both frontend (UX) and backend (security)
- Pydantic models for request/response validation in FastAPI
- OpenAPI documentation auto-generated and accessible
- CORS configured to allow only trusted frontend origins

**Rationale:** Consistent APIs reduce bugs, improve developer experience, enable auto-documentation, and simplify testing.

### V. Responsive & Accessible UI

All user interfaces MUST be fully responsive across devices and accessible to users with disabilities, following modern web standards.

**Rules:**
- Mobile-first design approach with Tailwind CSS
- Breakpoints: mobile (default), tablet (md:), desktop (lg:, xl:)
- Server Components by default; Client Components only for interactivity
- Semantic HTML elements (button, input, label, nav, main, etc.)
- ARIA labels on icon-only buttons and interactive elements
- Keyboard navigation support (tab order, focus states, enter/space activation)
- Focus indicators visible (ring-2 ring-indigo-500)
- Color contrast ratios meet WCAG AA standards minimum
- Loading states (skeletons) for async operations
- Error boundaries for graceful failure handling
- Toast notifications for user feedback (success/error)
- Dark mode support via Tailwind class strategy

**Rationale:** Accessibility is a right, not a feature. Responsive design ensures usability across all devices and contexts.

### VI. Performance & Scalability Standards

The application MUST meet defined performance benchmarks and scale efficiently to support concurrent users without degradation.

**Rules:**
- Initial dashboard load: < 2 seconds on standard broadband
- API response time (p95): < 500ms for CRUD operations
- Search response: < 300ms after last keystroke (debounced)
- Database queries MUST use proper indexes (user_id, completed, created_at)
- No N+1 query problems (use proper joins/eager loading)
- Pagination support: default 50 items, max 100 per page
- Optimistic UI updates with rollback on error
- Connection pooling for database (handled by Neon)
- Baseline capacity: 100 concurrent users, 1000 tasks per user
- Frontend bundle size monitoring (avoid unnecessary dependencies)

**Rationale:** Performance directly impacts user experience and retention. Slow apps are abandoned apps.

### VII. Test-First Development (Recommended)

Testing is strongly encouraged to ensure code quality, catch regressions early, and validate specifications.

**Rules:**
- Write tests BEFORE implementation when feasible (Red-Green-Refactor)
- Tests MUST fail initially to prove they test the right behavior
- Test categories: Contract tests (API contracts), Integration tests (user journeys), Unit tests (business logic)
- Tests organized by user story for independent validation
- Each user story MUST be independently testable
- Manual testing checklist for acceptance criteria validation
- Error scenarios MUST be tested (invalid input, unauthorized access, not found)
- Test data MUST NOT leak between tests (proper setup/teardown)

**Rationale:** Tests provide confidence in changes, document expected behavior, and enable safe refactoring.

## Technology Stack (Fixed & Non-Negotiable)

**Frontend:**
- Next.js 16+ (App Router only)
- TypeScript (strict mode)
- Tailwind CSS
- Better Auth (JWT plugin)
- shadcn/ui components
- Recharts or Chart.js (analytics)

**Backend:**
- FastAPI
- SQLModel (ORM)
- Python 3.13+
- pyjwt (JWT verification)
- Alembic (migrations)

**Database:**
- PostgreSQL (Neon Serverless)

**Deployment:**
- Frontend: Vercel (or similar)
- Backend: Render/Railway/DigitalOcean (or similar)
- Database: Neon Serverless PostgreSQL

**Rationale:** Standardized stack reduces complexity, improves maintainability, and leverages proven technologies.

## Development Workflow

**Spec-Driven Process:**
1. Write/update specification in `/specs/[feature]/`
2. Review and approve specification
3. Generate implementation plan (`/sp.plan`)
4. Generate tasks (`/sp.tasks`)
5. Implement code with spec references
6. Test against acceptance criteria
7. Create Prompt History Record (PHR) for traceability
8. Commit with descriptive message + Co-Authored-By: Claude

**File Organization:**
- Specifications: `Phase-2/specs/`
- Frontend code: `Phase-2/frontend/`
- Backend code: `Phase-2/backend/`
- Prompt history: `history/prompts/`
- Architecture decisions: `history/adr/`

**Code Quality Gates:**
- TypeScript strict mode with no `any` types
- Python type hints on all functions
- Linting passes (ESLint, Ruff/Black)
- No console.log in production code
- Environment variables for all configuration
- `.env.example` documents all required variables

## Security Requirements

**Mandatory Security Practices:**
- Input validation and sanitization on all user input
- SQL injection prevention via parameterized queries (SQLModel handles this)
- XSS prevention via React's automatic escaping
- CSRF protection via SameSite cookies
- Rate limiting on authentication endpoints (future enhancement)
- Secrets stored in environment variables only
- No sensitive data in logs or error messages
- HTTPS enforced in production
- Security headers configured (CSP, X-Frame-Options, etc.)

**Prohibited Practices:**
- Hardcoded credentials or API keys
- Storing passwords in plain text
- Exposing internal error details to users
- Allowing SQL injection vectors
- Trusting client-side validation alone

## Governance

**Constitution Authority:**
This constitution supersedes all other development practices and guidelines. When conflicts arise, constitution rules take precedence.

**Amendment Process:**
- Amendments require documentation of rationale and impact analysis
- Version number MUST increment per semantic versioning:
  - MAJOR: Backward-incompatible principle changes or removals
  - MINOR: New principles added or material expansions
  - PATCH: Clarifications, wording improvements, non-semantic fixes
- All dependent templates MUST be updated to maintain consistency
- Sync Impact Report MUST be generated and prepended to constitution file

**Compliance Verification:**
- All pull requests MUST verify compliance with constitution principles
- Code reviews MUST check for spec traceability and security requirements
- Complexity additions MUST be justified in plan.md Complexity Tracking section
- Violations MUST be documented and approved before merging

**Runtime Guidance:**
- Frontend developers: See `Phase-2/frontend/CLAUDE.md`
- Backend developers: See `Phase-2/backend/CLAUDE.md`
- Root guidance: See `Phase-2/CLAUDE.md`
- All guidance files MUST align with this constitution

**Version**: 1.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-12
