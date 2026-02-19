# Implementation Plan: Backend API for Task Management

**Branch**: `002-todo-backend-api` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-backend-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a secure, multi-tenant FastAPI backend that provides RESTful CRUD operations for task management. The API enforces strict data isolation between users through JWT authentication and user_id filtering at the repository layer. Implementation follows N-Tier architecture (Routes → Services → Repositories) with async-first patterns for all I/O operations. Bottom-up implementation approach: Database Models → Repositories → Services → API Routes.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI (latest stable), SQLModel (async ORM), pyjwt (JWT verification), psycopg3 (async PostgreSQL driver), Pydantic (validation)
**Storage**: Neon Serverless PostgreSQL with async connection pooling
**Testing**: pytest with pytest-asyncio for async tests, FastAPI TestClient for integration tests
**Target Platform**: Linux server (containerized deployment on Render/Railway/DigitalOcean)
**Project Type**: Web API (backend only - frontend is separate feature)
**Performance Goals**: < 150ms p95 for single task operations, < 500ms for task list retrieval (up to 1000 tasks), support 100 concurrent users
**Constraints**: < 200ms p95 API response time, async-first for all I/O, 100% type hint coverage, mandatory user_id filtering on all queries
**Scale/Scope**: 100 concurrent users baseline, 1000 tasks per user, 4 CRUD endpoints, 3-layer architecture (Routes/Services/Repositories)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Verification |
|-----------|--------|--------------|
| **Spec-First Integrity** | ✅ PASS | Complete specification exists at `specs/002-todo-backend-api/spec.md` with all functional requirements, user stories, and acceptance criteria defined |
| **N-Tier Layered Architecture** | ✅ PASS | Plan explicitly defines 3-layer structure: API Routes (Presentation) → Services (Business Logic) → Repositories (Data Access). Bottom-up implementation ensures proper layer boundaries |
| **Mandatory Multi-tenancy** | ✅ PASS | Spec requires 100% of queries include user_id filtering (FR-002, SC-002). Repository layer will enforce user_id on all queries. Service layer validates authenticated user matches request user |
| **Asynchronous First** | ✅ PASS | All database operations use async SQLModel with psycopg3 async driver. All route handlers, services, and repositories declared with `async def`. No blocking I/O in request paths |
| **Backend Standards** | ✅ PASS | FastAPI + SQLModel + Python 3.12+ + 'uv' dependency management. 100% type hint coverage required. Pydantic validation for all request/response schemas |
| **Security Standards** | ✅ PASS | JWT verification with Better Auth shared secret. All endpoints require authentication. Input validation at both route and service layers |
| **Performance Constraints** | ✅ PASS | Target < 150ms p95 for single operations (spec requirement). Async patterns and proper indexing support this goal |
| **Type Safety** | ✅ PASS | Python 3.12+ with 100% type hint coverage on all functions. Pydantic models for validation |

**Gate Result**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 Research

**Re-evaluation After Phase 1 Design**:

| Principle | Status | Verification |
|-----------|--------|--------------|
| **N-Tier Layer Boundaries** | ✅ PASS | data-model.md clearly separates SQLModel (data layer), Pydantic schemas (API layer), and documents business logic location (service layer). No layer leakage detected |
| **Multi-tenancy in Design** | ✅ PASS | data-model.md enforces user_id filtering in all queries. Composite indexes start with user_id. Repository methods accept user_id as first parameter |
| **API Contracts** | ✅ PASS | contracts/task-api.yaml defines all endpoints with user_id path parameter. JWT authentication required. Standardized error responses documented |
| **Async Patterns** | ✅ PASS | data-model.md shows async SQLModel usage. research.md documents async session management and psycopg3 async driver |
| **Type Safety** | ✅ PASS | All models and schemas include complete type annotations. Pydantic validation for all request/response data |

**Final Gate Result**: ✅ ALL CHECKS PASSED - Design artifacts comply with constitution principles. Ready for Phase 2 (tasks generation via /sp.tasks)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Phase-2/backend/
├── app/
│   ├── api/                    # Presentation Layer (Routes)
│   │   ├── __init__.py
│   │   ├── dependencies.py     # FastAPI dependencies (auth, DB session)
│   │   ├── middleware.py       # Auth middleware, error handlers
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       └── tasks.py        # Task CRUD endpoints
│   ├── services/               # Service Layer (Business Logic)
│   │   ├── __init__.py
│   │   └── task_service.py     # Task business logic, validation
│   ├── repositories/           # Repository Layer (Data Access)
│   │   ├── __init__.py
│   │   └── task_repository.py  # Task database operations
│   ├── models/                 # SQLModel entities + Pydantic schemas
│   │   ├── __init__.py
│   │   └── task.py             # Task model and schemas
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Environment configuration
│   │   ├── database.py         # Database connection, session management
│   │   └── auth.py             # JWT verification utilities
│   └── main.py                 # FastAPI application entry point
├── tests/
│   ├── conftest.py             # Pytest fixtures (test DB, auth tokens)
│   ├── unit/                   # Unit tests (service layer)
│   │   └── test_task_service.py
│   ├── integration/            # Integration tests (API endpoints)
│   │   └── test_task_routes.py
│   └── contract/               # Contract tests (schema validation)
│       └── test_task_schemas.py
├── pyproject.toml              # uv project configuration
├── requirements.txt            # Generated by uv
├── .env.example                # Environment variable template
└── README.md                   # Setup and development instructions
```

**Structure Decision**: Web application backend structure following existing Phase-2 conventions. Root directory is `app/` (not `src/`). API routes are versioned under `api/v1/`. Models and schemas are co-located in `models/` directory. The N-Tier architecture is reflected with clear separation between api/ (Presentation), services/ (Business Logic), and repositories/ (Data Access) layers.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All constitution principles are satisfied by the planned architecture.

- N-Tier architecture is explicitly required by constitution and spec
- Multi-tenancy enforcement is a core requirement (FR-002, SC-002)
- Async-first is mandated by constitution for all I/O operations
- No additional complexity beyond constitutional requirements

---

## Phase 0: Research (Completed)

**Output**: `research.md`

**Key Decisions Documented**:
1. JWT verification with Better Auth shared secret
2. Domain exception pattern for error handling
3. FastAPI dependency injection for N-Tier architecture
4. Async SQLModel with psycopg3 driver
5. Multi-tenancy enforcement at repository layer
6. Layered testing strategy (unit/integration/contract)
7. 'uv' dependency management
8. SQLModel auto-create schema strategy

**ADR Candidates Identified**:
- "JWT Token Verification Strategy for Multi-tenant API"
- "FastAPI Dependency Injection for N-Tier Architecture"

---

## Phase 1: Design & Contracts (Completed)

**Outputs**:
- `data-model.md` - Database entities, validation rules, state transitions
- `contracts/task-api.yaml` - OpenAPI 3.1.0 specification
- `quickstart.md` - Developer setup and getting started guide

**Data Model Summary**:
- 1 entity (Task) with 8 fields
- 3 indexes (1 primary key + 2 composite for multi-tenancy)
- 5 validation rules
- 4 status states with defined transitions
- SQLModel and Pydantic schemas defined

**API Contract Summary**:
- 5 endpoints (GET list, POST create, GET single, PATCH update, DELETE)
- JWT Bearer authentication required
- Standardized success/error response formats
- Multi-tenancy enforced via user_id path parameter

**Quickstart Guide**:
- Prerequisites and installation steps
- Environment configuration
- Database setup (Neon and local options)
- Development workflow commands
- API usage examples
- Troubleshooting guide

---

## Implementation Phases (for /sp.tasks)

The implementation will follow a bottom-up approach:

### Phase 1: Foundation
- Database models (SQLModel entities)
- Database connection and session management
- Configuration management
- JWT verification utilities

### Phase 2: Data Access Layer
- Task repository with async methods
- Multi-tenancy enforcement in queries
- Transaction management

### Phase 3: Business Logic Layer
- Task service with validation
- Domain exceptions
- Business rule enforcement

### Phase 4: Presentation Layer
- FastAPI routes and dependencies
- Request/response handling
- Global exception handlers
- CORS and middleware configuration

### Phase 5: Testing
- Unit tests (service layer)
- Integration tests (API endpoints)
- Contract tests (schema validation)
- Multi-tenancy verification tests

---

## Next Steps

1. **Generate ADRs** (optional): Run `/sp.adr <title>` for each ADR candidate identified in research.md
2. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation tasks based on this plan
3. **Implementation**: Execute tasks following bottom-up approach (Foundation → Data Access → Business Logic → Presentation → Testing)

---

## Artifacts Summary

| Artifact | Path | Purpose |
|----------|------|---------|
| Specification | `specs/002-todo-backend-api/spec.md` | Feature requirements and user stories |
| Implementation Plan | `specs/002-todo-backend-api/plan.md` | This document - architecture and design |
| Research | `specs/002-todo-backend-api/research.md` | Architectural decisions and best practices |
| Data Model | `specs/002-todo-backend-api/data-model.md` | Database entities and validation rules |
| API Contract | `specs/002-todo-backend-api/contracts/task-api.yaml` | OpenAPI specification |
| Quickstart Guide | `specs/002-todo-backend-api/quickstart.md` | Developer setup instructions |

**Planning Status**: ✅ COMPLETE - Ready for task generation via `/sp.tasks`
