# Implementation Plan: AI Chatbot Backend with MCP Server

**Branch**: `001-chatbot-backend` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chatbot-backend/spec.md`

## Summary

Build a stateless FastAPI backend that enables natural language task management through an AI chatbot. The system integrates OpenAI Agents SDK for intent recognition and MCP (Model Context Protocol) server for standardized tool execution. All conversation state persists to database, enabling horizontal scaling and resilience. The backend reuses Phase 2's database (tasks table) and authentication (Better Auth JWT), adding new Conversation and Message tables for chat history.

**Core Innovation**: Stateless architecture where every request fetches conversation history from database, processes with AI agent, executes MCP tools, and persists results—enabling server restarts without data loss and horizontal scaling without session affinity.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**:
- FastAPI (latest stable) - async web framework
- OpenAI Agents SDK - AI agent orchestration
- Official MCP SDK for Python - tool protocol implementation
- SQLModel - async ORM for database operations
- psycopg3 (async driver) - PostgreSQL connection
- pyjwt - JWT token verification
- httpx - async HTTP client for Better Auth JWKS
- uv - Python package manager (mandatory)

**Storage**: Neon Serverless PostgreSQL (shared with Phase 2)
- Existing tables: tasks, users (Better Auth)
- New tables: conversations, messages (created via SQLModel on startup)

**Testing**: pytest with pytest-asyncio for async test support
**Target Platform**: Linux server (Hugging Face Spaces or similar)
**Project Type**: Web backend (REST API)
**Project Initialization**: uv project named "backend" in Phase-3/ directory
**Performance Goals**:
- Chat response time < 5 seconds (95th percentile) including AI processing
- Support 100 concurrent chat requests
- Database query time < 100ms per operation

**Constraints**:
- Stateless server (no in-memory session state)
- Conversation history truncation at 20 messages (OpenAI token limits)
- Same database as Phase 2 (must not break existing schema)
- JWT verification must match Phase 2 pattern
- Use uv for all dependency management (no pip)
- Tables created via SQLModel on FastAPI startup (no Alembic migrations)

**Scale/Scope**:
- 100 concurrent users
- Unlimited conversations per user
- 20 messages per conversation in context window
- 5 MCP tools (add_task, list_task, complete_task, delete_task, update_task)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-First Integrity ✅ PASS

- **Status**: COMPLIANT
- **Evidence**: Complete specification exists at `specs/001-chatbot-backend/spec.md` with 18 functional requirements, 3 user stories, and 8 success criteria
- **Traceability**: All code will reference `@spec specs/001-chatbot-backend/spec.md` with specific FR numbers

### II. N-Tier Layered Architecture ✅ PASS

- **Status**: COMPLIANT
- **Architecture**:
  - **Presentation Layer**: `app/api/v1/chat.py` - HTTP endpoint, JWT verification, request/response handling
  - **Service Layer**: `app/services/chat_service.py` - OpenAI Agent orchestration, conversation management, business logic
  - **Repository Layer**: `app/repositories/conversation_repository.py`, `app/repositories/message_repository.py` - database operations
  - **MCP Layer**: `app/mcp/tools/` - MCP tool implementations (calls task repository from Phase 2)
- **Dependency Flow**: Route → ChatService → ConversationRepository/MessageRepository → Database
- **No Layer Leaks**: MCP tools will call Phase 2 task repository (not direct SQL)

### III. Mandatory Multi-tenancy ✅ PASS

- **Status**: COMPLIANT
- **Enforcement**:
  - Chat endpoint: `POST /api/{user_id}/chat` with JWT verification (`path.user_id === jwt.sub`)
  - All conversation queries: `WHERE user_id = :authenticated_user_id`
  - All message queries: `WHERE user_id = :authenticated_user_id`
  - MCP tools: Pass authenticated `user_id` to Phase 2 task repository (inherits multi-tenancy)
  - Conversation ownership validation before fetching history
- **Security**: Return 404 for non-owned conversations (prevent existence leakage)

### IV. Asynchronous First ✅ PASS

- **Status**: COMPLIANT
- **Implementation**:
  - All route handlers: `async def`
  - All service methods: `async def`
  - All repository methods: `async def`
  - Database operations: `await session.exec()`
  - OpenAI API calls: async client (httpx)
  - Better Auth JWKS fetch: async httpx client
  - No blocking operations in request path

### Additional Standards Compliance

**Backend Standards**: ✅ PASS
- FastAPI framework
- Python 3.12+ with type hints
- 'uv' for dependency management
- SQLModel for async ORM
- Pydantic for request/response validation
- RESTful API design

**Security Standards**: ✅ PASS
- JWT verification via Better Auth JWKS
- Shared BETTER_AUTH_SECRET with Phase 2
- Input validation (Pydantic schemas)
- CORS configuration for Phase 3 frontend
- No hardcoded secrets (environment variables)

**Performance Standards**: ✅ PASS
- Target: < 5 seconds for chat response (includes AI processing)
- Async operations for all I/O
- Database indexes on user_id, conversation_id
- Connection pooling (Neon handles)

### Constitution Violations: NONE

No violations detected. All core principles and standards are satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-chatbot-backend/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (PENDING)
├── data-model.md        # Phase 1 output (PENDING)
├── quickstart.md        # Phase 1 output (PENDING)
├── contracts/           # Phase 1 output (PENDING)
│   └── chat-api.yaml    # OpenAPI spec for chat endpoint
├── checklists/
│   └── requirements.md  # Spec quality checklist (COMPLETE)
└── tasks.md             # Phase 2 output via /sp.tasks (PENDING)
```

### Source Code (repository root)

```text
Phase-3/
└── backend/                         # uv project (uv init backend)
    ├── app/
    │   ├── main.py                      # FastAPI application entry point + startup event
    │   ├── core/
    │   │   ├── config.py                # Settings (env vars)
    │   │   ├── auth.py                  # JWT verification (reuse Phase 2 pattern)
    │   │   └── database.py              # Async database session
    │   ├── models/
    │   │   ├── conversation.py          # SQLModel: Conversation entity
    │   │   └── message.py               # SQLModel: Message entity
    │   ├── schemas/
    │   │   ├── chat.py                  # Pydantic: ChatRequest, ChatResponse
    │   │   └── mcp.py                   # Pydantic: MCP tool schemas
    │   ├── repositories/
    │   │   ├── conversation_repository.py  # Data access: conversations
    │   │   └── message_repository.py       # Data access: messages
    │   ├── services/
    │   │   └── chat_service.py          # Business logic: AI agent orchestration
    │   ├── mcp/
    │   │   ├── server.py                # MCP server initialization
    │   │   └── tools/
    │   │       ├── add_task.py          # MCP tool: add_task
    │   │       ├── list_tasks.py        # MCP tool: list_tasks
    │   │       ├── complete_task.py     # MCP tool: complete_task
    │   │       ├── delete_task.py       # MCP tool: delete_task
    │   │       └── update_task.py       # MCP tool: update_task
    │   └── api/
    │       └── v1/
    │           ├── chat.py              # Route: POST /api/{user_id}/chat
    │           └── health.py            # Route: GET /health (reuse Phase 2)
    ├── tests/
    │   ├── contract/
    │   │   └── test_chat_api.py         # API contract tests
    │   ├── integration/
    │   │   ├── test_chat_flow.py        # End-to-end chat scenarios
    │   │   └── test_mcp_tools.py        # MCP tool integration tests
    │   └── unit/
    │       ├── test_chat_service.py     # Service layer unit tests
    │       └── test_repositories.py     # Repository layer unit tests
    ├── pyproject.toml                   # uv dependencies and project config
    ├── .env.example                     # Environment variable template
    ├── Dockerfile                       # Container for deployment
    └── README.md                        # Setup and deployment instructions
```

**Structure Decision**: Web application structure with Phase-3/backend as uv project. This is separate from Phase-2/backend to maintain clear separation between dashboard API and chatbot API, while sharing the same database. The N-Tier architecture is enforced with distinct api/, services/, repositories/, and mcp/ directories.

**Key Changes from Standard Structure**:
- No `alembic/` directory - tables created via SQLModel on startup
- `pyproject.toml` managed by uv (not manual pip requirements.txt)
- `app/main.py` includes `@app.on_event("startup")` for table creation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This section is not applicable.

---

## Phase 0: Research & Technology Validation

**Objective**: Resolve all technical unknowns and validate integration patterns before design phase.

### Research Tasks

#### R1: OpenAI Agents SDK Integration Pattern

**Question**: How does OpenAI Agents SDK integrate with custom MCP tools in a stateless FastAPI application?

**Research Areas**:
- Agent initialization and configuration
- Tool registration with MCP server
- Conversation history format for agent context
- Error handling when tools fail
- Token limit management for conversation history

**Deliverable**: Code pattern for agent initialization, tool registration, and request handling

#### R2: Official MCP SDK for Python

**Question**: What is the correct pattern for implementing MCP tools using the Official MCP SDK?

**Research Areas**:
- MCP server initialization
- Tool definition schema (parameters, returns, descriptions)
- Tool execution lifecycle
- Error propagation from tools to agent
- Async support in MCP SDK

**Deliverable**: MCP tool template with proper schema definition and error handling

#### R3: Stateless Conversation Management

**Question**: How to efficiently fetch and truncate conversation history for AI context while maintaining stateless architecture?

**Research Areas**:
- Optimal query pattern for last N messages
- Message ordering (oldest first vs newest first for AI)
- Token counting strategy (approximate vs exact)
- Truncation algorithm (keep recent + system messages)
- Performance optimization (database indexes, query limits)

**Deliverable**: Repository method for fetching conversation history with truncation logic

#### R4: Better Auth JWT Verification (Phase 2 Pattern)

**Question**: How to reuse Phase 2's JWT verification pattern for Phase 3 backend?

**Research Areas**:
- JWKS endpoint URL from Phase 2 frontend
- JWT verification code from Phase 2 backend (`app/core/auth.py`)
- Shared secret configuration
- FastAPI dependency injection pattern
- Error handling for expired/invalid tokens

**Deliverable**: Reusable JWT verification dependency for Phase 3

#### R5: Database Schema Migration Strategy

**Question**: How to add Conversation and Message tables without breaking Phase 2 schema?

**Research Areas**:
- Alembic migration for new tables
- Foreign key to existing users table (Better Auth)
- Index strategy for performance (user_id, conversation_id, created_at)
- Relationship to existing tasks table (none - MCP tools access via repository)
- Migration rollback strategy

**Deliverable**: Alembic migration script with proper indexes and constraints

### Research Output

**File**: `specs/001-chatbot-backend/research.md`

**Format**:
```markdown
# Research Findings: AI Chatbot Backend

## R1: OpenAI Agents SDK Integration Pattern

**Decision**: [Chosen approach]
**Rationale**: [Why this approach]
**Alternatives Considered**: [Other options evaluated]
**Code Example**: [Minimal working example]

[Repeat for R2-R5]
```

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all unknowns resolved

### D1: Data Model Design

**File**: `specs/001-chatbot-backend/data-model.md`

**Entities**:

#### Conversation
- **Purpose**: Represents a chat session between user and AI assistant
- **Attributes**:
  - `id` (UUID, primary key)
  - `user_id` (String, foreign key to users.id, indexed)
  - `created_at` (DateTime, indexed)
  - `updated_at` (DateTime)
- **Relationships**:
  - Belongs to User (Better Auth)
  - Has many Messages
- **Validation Rules**:
  - user_id must exist in users table
  - created_at defaults to current timestamp
- **Indexes**:
  - Primary: `id`
  - Composite: `(user_id, created_at DESC)` for efficient user conversation listing

#### Message
- **Purpose**: Represents a single message in a conversation (user or assistant)
- **Attributes**:
  - `id` (UUID, primary key)
  - `conversation_id` (UUID, foreign key to conversations.id, indexed)
  - `user_id` (String, foreign key to users.id, indexed)
  - `role` (Enum: 'user' | 'assistant')
  - `content` (Text, required)
  - `tool_calls` (JSONB, optional) - Array of tool invocations
  - `created_at` (DateTime, indexed)
- **Relationships**:
  - Belongs to Conversation
  - Belongs to User
- **Validation Rules**:
  - conversation_id must exist
  - user_id must match conversation.user_id
  - role must be 'user' or 'assistant'
  - content cannot be empty
  - tool_calls must be valid JSON array if present
- **Indexes**:
  - Primary: `id`
  - Composite: `(conversation_id, created_at ASC)` for efficient message ordering
  - Composite: `(user_id, created_at DESC)` for user message history

#### Task (Existing - Phase 2)
- **Purpose**: Todo items (no changes to schema)
- **Access Pattern**: MCP tools access via Phase 2 task repository
- **Multi-tenancy**: Enforced by Phase 2 repository (user_id filtering)

### D2: API Contracts

**File**: `specs/001-chatbot-backend/contracts/chat-api.yaml`

**OpenAPI Specification**:

```yaml
openapi: 3.0.0
info:
  title: AI Chatbot API
  version: 1.0.0
  description: Natural language task management via AI chatbot

paths:
  /api/{user_id}/chat:
    post:
      summary: Send message to AI chatbot
      description: |
        Stateless endpoint that processes user message with AI agent,
        executes MCP tools, and returns assistant response.
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
          description: Authenticated user ID (must match JWT subject)
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                conversation_id:
                  type: integer
                  description: Existing conversation ID (creates new if omitted)
                  example: 123
                message:
                  type: string
                  description: User's natural language message
                  example: "Add a task to buy groceries"
                  minLength: 1
                  maxLength: 2000
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                required:
                  - conversation_id
                  - response
                  - tool_calls
                properties:
                  conversation_id:
                    type: integer
                    description: Conversation ID (new or existing)
                    example: 123
                  response:
                    type: string
                    description: AI assistant's response
                    example: "✓ Task added: Buy groceries"
                  tool_calls:
                    type: array
                    description: List of MCP tools invoked
                    items:
                      type: object
                      properties:
                        tool:
                          type: string
                          example: "add_task"
                        parameters:
                          type: object
                          example: {"title": "Buy groceries"}
                        result:
                          type: object
                          example: {"task_id": 5, "status": "created"}
        '400':
          description: Bad request (invalid message format)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized (invalid or missing JWT)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '403':
          description: Forbidden (user_id mismatch with JWT)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '500':
          description: Server error (OpenAI API failure, database error)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Better Auth JWT token

  schemas:
    Error:
      type: object
      required:
        - status
        - code
        - message
      properties:
        status:
          type: string
          enum: [error]
        code:
          type: string
          example: "INVALID_REQUEST"
        message:
          type: string
          example: "Message cannot be empty"
        details:
          type: object
          description: Additional error context
```

### D3: MCP Tool Specifications

**File**: `specs/001-chatbot-backend/contracts/mcp-tools.yaml`

**Tool Definitions** (5 tools matching phase-3.md requirements):

```yaml
tools:
  - name: add_task
    description: Create a new task for the user
    parameters:
      type: object
      required: [user_id, title]
      properties:
        user_id:
          type: string
          description: Authenticated user ID
        title:
          type: string
          description: Task title
          minLength: 1
          maxLength: 200
        description:
          type: string
          description: Optional task description
          maxLength: 1000
    returns:
      type: object
      properties:
        task_id:
          type: integer
        status:
          type: string
          enum: [created]
        title:
          type: string

  - name: list_tasks
    description: Retrieve user's tasks with optional status filter
    parameters:
      type: object
      required: [user_id]
      properties:
        user_id:
          type: string
        status:
          type: string
          enum: [all, pending, completed]
          default: all
    returns:
      type: array
      items:
        type: object
        properties:
          id:
            type: integer
          title:
            type: string
          description:
            type: string
          completed:
            type: boolean
          created_at:
            type: string
            format: date-time

  - name: complete_task
    description: Mark a task as complete
    parameters:
      type: object
      required: [user_id, task_id]
      properties:
        user_id:
          type: string
        task_id:
          type: integer
    returns:
      type: object
      properties:
        task_id:
          type: integer
        status:
          type: string
          enum: [completed]
        title:
          type: string

  - name: delete_task
    description: Remove a task from the list
    parameters:
      type: object
      required: [user_id, task_id]
      properties:
        user_id:
          type: string
        task_id:
          type: integer
    returns:
      type: object
      properties:
        task_id:
          type: integer
        status:
          type: string
          enum: [deleted]
        title:
          type: string

  - name: update_task
    description: Modify task title or description
    parameters:
      type: object
      required: [user_id, task_id]
      properties:
        user_id:
          type: string
        task_id:
          type: integer
        title:
          type: string
          minLength: 1
          maxLength: 200
        description:
          type: string
          maxLength: 1000
    returns:
      type: object
      properties:
        task_id:
          type: integer
        status:
          type: string
          enum: [updated]
        title:
          type: string
```

### D4: Quickstart Guide

**File**: `specs/001-chatbot-backend/quickstart.md`

**Content**: Developer setup instructions, environment variables, database migration, running locally, testing the chat endpoint.

### D5: Agent Context Update

**Action**: Run `.specify/scripts/bash/update-agent-context.sh claude`

**Purpose**: Update `CLAUDE.md` with Phase 3 technologies:
- OpenAI Agents SDK
- Official MCP SDK
- Stateless architecture pattern
- Conversation/Message models

---

## Next Steps

1. **Execute Phase 0**: Generate `research.md` by researching OpenAI Agents SDK, MCP SDK, and stateless patterns
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Run `/sp.tasks`**: Generate implementation tasks from this plan
4. **Run `/sp.implement`**: Execute tasks to build the chatbot backend

**Command**: `/sp.tasks` (after Phase 0 and Phase 1 complete)
