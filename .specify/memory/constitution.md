<!--
Sync Impact Report:
Version: 1.0.0 → 2.0.0 (MAJOR: Fundamental principle restructuring and architectural paradigm shift)
Modified Principles:
  - Spec-Driven Development → Spec-First Integrity (strengthened language)
  - User Data Isolation → Mandatory Multi-tenancy (expanded scope, stricter enforcement)
  - JWT Authentication & Authorization → Consolidated into Security Requirements section
  - API-First Design → Consolidated into Key Standards section
  - Responsive & Accessible UI → Consolidated into Key Standards section
  - Performance & Scalability → Updated criteria (500ms → 200ms), consolidated into Success Criteria
  - Test-First Development → Remains in Development Workflow (no longer top-level principle)
Added Principles:
  - N-Tier Layered Architecture (NEW - critical architectural principle)
  - Asynchronous First (NEW - performance and scalability foundation)
Removed Principles:
  - None removed, but 5 principles consolidated into supporting sections
Technology Stack Updates:
  - Python 3.13+ → 3.12+ (user specification)
  - Next.js 16 → 15 (user specification)
  - Added: 'uv' as mandatory Python dependency manager
  - Added: psycopg3 async driver requirement
  - Performance: API p95 < 500ms → < 200ms (stricter)
Templates Status:
  ✅ plan-template.md - Constitution Check section will reflect new principles
  ✅ spec-template.md - User story structure remains compatible
  ✅ tasks-template.md - Phase structure supports N-Tier and async patterns
  ⚠ commands/*.md - May need updates to reference new principle names
Follow-up TODOs:
  - Verify all command files reference correct principle names
  - Update any runtime guidance files (CLAUDE.md) to reflect N-Tier architecture
  - Consider adding N-Tier validation checklist to plan template
-->

# Phase-2 Todo Web Application Constitution

## Core Principles

### I. Spec-First Integrity (NON-NEGOTIABLE)

Every line of code MUST originate from an explicit specification document. No code shall be written, modified, or suggested without a traceable reference to a specification file in `/specs/`.

**Rules:**
- All implementation work requires a `@specs/[file].md` reference in code comments
- Specifications are written BEFORE any code generation begins
- If a feature is not in specs → update specs first, then implement
- Code reviews MUST verify spec traceability for every change
- Spec files are the single source of truth; code is derivative
- All code must be derived from and validated against specifications
- No assumptions or "best practices" override explicit spec requirements

**Rationale:** Ensures intentional design, prevents scope creep, maintains documentation accuracy, and enables AI-assisted development with clear requirements. Spec-first development eliminates ambiguity and provides a contract between design and implementation.

### II. N-Tier Layered Architecture (NON-NEGOTIABLE)

The application MUST maintain strict separation between Presentation (API/Routes), Service (Business Logic), and Repository (Data Access) layers. No layer shall bypass or directly access another layer's responsibilities.

**Rules:**
- **Presentation Layer (Routes/API)**: Handles HTTP requests, authentication, input validation, response formatting. MUST NOT contain business logic or database queries.
- **Service Layer (Business Logic)**: Implements use cases, orchestrates operations, enforces business rules. MUST NOT handle HTTP concerns or construct SQL queries.
- **Repository Layer (Data Access)**: Executes database operations, constructs queries, manages transactions. MUST NOT contain business logic or HTTP handling.
- Routes call Services; Services call Repositories; NO other cross-layer calls permitted
- Each layer has single responsibility and clear boundaries
- Data flows: Request → Route → Service → Repository → Database (and reverse)
- Dependency injection used to wire layers together
- Layer violations detected in code review are blocking issues

**Rationale:** Separation of concerns enables independent testing, maintainability, and scalability. Clear boundaries prevent "spaghetti code" and make the system easier to reason about, modify, and extend.

### III. Mandatory Multi-tenancy (ZERO-TOLERANCE)

Every user's data MUST be completely isolated from all other users. No user shall ever access, view, modify, or delete another user's tasks under any circumstances. Every data operation MUST be scoped and verified by user_id.

**Rules:**
- Every database query MUST include `WHERE user_id = :authenticated_user_id`
- Every API endpoint path MUST contain `{user_id}` parameter
- Backend middleware MUST verify `path.user_id === jwt.user_id` → else 403 Forbidden
- Frontend MUST never allow manual `user_id` manipulation in URLs or requests
- All list/search/filter operations MUST be scoped to authenticated user only
- Database indexes MUST include `user_id` as first column for performance
- Return 404 (not 403) for non-owned resources to prevent existence leakage
- Repository layer MUST enforce user_id filtering on ALL queries
- Service layer MUST validate user_id matches authenticated user
- Absolute isolation: User A cannot access or modify User B's data under any condition

**Rationale:** Privacy and security are non-negotiable. Data leakage destroys user trust and violates fundamental security principles. Multi-tenancy must be enforced at every layer to prevent accidental or malicious data access.

### IV. Asynchronous First (NON-NEGOTIABLE)

All backend I/O and database operations MUST be non-blocking using async/await patterns. Synchronous blocking operations are prohibited in request handlers.

**Rules:**
- All database operations use async SQLModel methods (`session.exec()` → `await session.exec()`)
- All external API calls use async HTTP clients (httpx, aiohttp)
- All file I/O operations use async methods (aiofiles)
- FastAPI route handlers declared with `async def`
- Repository methods declared with `async def`
- Service methods declared with `async def` when calling async repositories
- Database driver MUST support async (psycopg3 async driver for PostgreSQL)
- Connection pooling configured for async operations
- No `time.sleep()` or blocking waits in request paths
- Background tasks use FastAPI BackgroundTasks or async task queues

**Rationale:** Asynchronous operations maximize throughput and resource efficiency. Blocking operations in async frameworks cause performance degradation and prevent the application from scaling to handle concurrent users effectively.

## Key Standards

### Backend Standards
- **Framework**: FastAPI (latest stable)
- **Language**: Python 3.12+ with 100% type hint coverage
- **Dependency Management**: 'uv' (mandatory - no manual pip installs)
- **ORM**: SQLModel for async database operations
- **Database Driver**: psycopg3 async driver for PostgreSQL
- **Authentication**: Better Auth JWT verification with shared secret
- **Validation**: Pydantic models for all request/response schemas
- **API Design**: RESTful with base path `/api/{user_id}/[resource]`
- **Response Format (Success)**: `{ status: "success", data: {...}, message?: string, meta?: {...} }`
- **Response Format (Error)**: `{ status: "error", code: string, message: string, details?: {...} }`
- **HTTP Status Codes**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Server Error)

### Frontend Standards
- **Framework**: Next.js 15 (App Router only)
- **Language**: TypeScript (strict mode) with zero 'any' types
- **Styling**: Tailwind CSS with mobile-first approach
- **Components**: shadcn/ui component library
- **Authentication**: Better Auth (JWT plugin) with httpOnly cookies
- **State Management**: React Server Components by default; Client Components only for interactivity
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation, WCAG AA contrast ratios
- **Responsive Design**: Breakpoints - mobile (default), tablet (md:), desktop (lg:, xl:)
- **Error Handling**: Error boundaries and toast notifications for user feedback

### Database Standards
- **Database**: Neon Serverless PostgreSQL
- **Driver**: psycopg3 async driver
- **Migrations**: Alembic for schema versioning
- **Indexes**: All queries must have supporting indexes; user_id as first column in composite indexes
- **Connection Pooling**: Configured for async operations (handled by Neon)

### Security Standards
- **Authentication**: Better Auth with JWT tokens (7-day validity default)
- **Token Verification**: Backend MUST verify signature, expiry, and payload integrity
- **Shared Secret**: `BETTER_AUTH_SECRET` identical in frontend and backend
- **Password Hashing**: Handled by Better Auth (bcrypt/argon2)
- **HTTPS**: Enforced in production (no exceptions)
- **Input Validation**: Both frontend (UX) and backend (security)
- **SQL Injection Prevention**: Parameterized queries via SQLModel
- **XSS Prevention**: React's automatic escaping
- **CSRF Protection**: SameSite cookies
- **Secrets Management**: Environment variables only; no hardcoded credentials
- **CORS**: Configured to allow only trusted frontend origins

## Constraints

### Environment Constraints
- Python dependency management MUST use 'uv' exclusively
- No manual pip installs permitted
- All dependencies declared in `pyproject.toml` or `requirements.txt`
- Environment variables for all configuration (documented in `.env.example`)

### Performance Constraints
- API response time (p95): < 200ms for standard CRUD operations
- Initial dashboard load: < 2 seconds on standard broadband
- Search response: < 300ms after last keystroke (debounced)
- Database queries MUST use proper indexes
- No N+1 query problems (use proper joins/eager loading)
- Pagination support: default 50 items, max 100 per page

### Scalability Constraints
- Baseline capacity: 100 concurrent users, 1000 tasks per user
- Connection pooling for database (handled by Neon)
- Optimistic UI updates with rollback on error

## Success Criteria

### Layer Integrity
- **No Layer Leaks**: Routes never call Repositories; Repositories never contain business logic
- **Single Responsibility**: Each layer has clear, testable boundaries
- **Dependency Flow**: Presentation → Service → Repository (one direction only)

### Data Isolation
- **Absolute Isolation**: Verified that User A cannot access or modify User B's data
- **User ID Enforcement**: Every query filtered by authenticated user_id
- **Security Testing**: Attempted cross-user access returns 404 or 403 appropriately

### Performance
- **API Response Times**: < 200ms for standard CRUD operations (p95)
- **Async Operations**: All I/O operations non-blocking
- **Database Performance**: Proper indexes on all query paths

### Type Safety
- **Python**: 100% type hint coverage on all functions and methods
- **TypeScript**: Zero 'any' types; strict mode enabled
- **Validation**: Pydantic/Zod schemas for all API contracts

## Technology Stack (Fixed & Non-Negotiable)

**Frontend:**
- Next.js 15 (App Router only)
- TypeScript (strict mode)
- Tailwind CSS
- Better Auth (JWT plugin)
- shadcn/ui components
- Recharts or Chart.js (analytics)

**Backend:**
- FastAPI
- SQLModel (ORM)
- Python 3.12+
- 'uv' (dependency management)
- pyjwt (JWT verification)
- psycopg3 (async PostgreSQL driver)
- Alembic (migrations)

**Database:**
- PostgreSQL (Neon Serverless)

**Deployment:**
- Frontend: Vercel (or similar)
- Backend: Render/Railway/DigitalOcean (or similar)
- Database: Neon Serverless PostgreSQL

**Rationale:** Standardized stack reduces complexity, improves maintainability, and leverages proven technologies optimized for async operations and multi-tenancy.

## Development Workflow

**Spec-Driven Process:**
1. Write/update specification in `/specs/[feature]/`
2. Review and approve specification
3. Generate implementation plan (`/sp.plan`)
4. Generate tasks (`/sp.tasks`)
5. Implement code with spec references and N-Tier architecture
6. Test against acceptance criteria (layer isolation, multi-tenancy, performance)
7. Create Prompt History Record (PHR) for traceability
8. Commit with descriptive message + Co-Authored-By: Claude

**File Organization:**
- Specifications: `Phase-2/specs/`
- Frontend code: `Phase-2/frontend/`
- Backend code: `Phase-2/backend/`
- Prompt history: `history/prompts/`
- Architecture decisions: `history/adr/`

**Backend Structure (N-Tier):**
```
backend/
├── src/
│   ├── api/          # Presentation Layer (routes, dependencies)
│   ├── services/     # Service Layer (business logic)
│   ├── repositories/ # Repository Layer (data access)
│   ├── models/       # SQLModel entities
│   └── schemas/      # Pydantic request/response schemas
└── tests/
```

**Code Quality Gates:**
- TypeScript strict mode with no `any` types
- Python type hints on all functions (100% coverage)
- Linting passes (ESLint, Ruff/Black)
- No console.log in production code
- Environment variables for all configuration
- `.env.example` documents all required variables
- Layer separation verified in code review

**Testing Approach (Recommended):**
- Write tests BEFORE implementation when feasible (Red-Green-Refactor)
- Test categories: Contract tests (API contracts), Integration tests (user journeys), Unit tests (business logic)
- Tests organized by user story for independent validation
- Each user story MUST be independently testable
- Error scenarios MUST be tested (invalid input, unauthorized access, not found)
- Test data MUST NOT leak between tests (proper setup/teardown)

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
- Code reviews MUST check for:
  - Spec traceability
  - N-Tier layer separation (no layer leaks)
  - Multi-tenancy enforcement (user_id filtering)
  - Async/await usage for all I/O operations
  - Type safety (no 'any' types, 100% type hints)
  - Security requirements (JWT verification, input validation)
- Complexity additions MUST be justified in plan.md Complexity Tracking section
- Violations MUST be documented and approved before merging

**Runtime Guidance:**
- Frontend developers: See `Phase-2/frontend/CLAUDE.md`
- Backend developers: See `Phase-2/backend/CLAUDE.md`
- Root guidance: See `Phase-2/CLAUDE.md`
- All guidance files MUST align with this constitution

**Version**: 2.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-16
