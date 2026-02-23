# Tasks: AI Chatbot Backend with MCP Server

**Input**: Design documents from `/specs/001-chatbot-backend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Project root: `Phase-3/backend/` (uv project)
- Application code: `Phase-3/backend/app/`
- N-Tier structure: `app/api/v1/`, `app/services/`, `app/repositories/`, `app/mcp/tools/`, `app/models/`, `app/core/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize uv project named "backend" in Phase-3/ directory
- [X] T002 Install core dependencies: fastapi, sqlmodel, psycopg[binary], psycopg[pool], pyjwt, httpx, uvicorn, openai
- [X] T003 [P] Install dev dependencies: pytest, pytest-asyncio, httpx, ruff, mypy
- [X] T004 [P] Create project directory structure: app/api/v1/, app/services/, app/repositories/, app/mcp/tools/, app/models/, app/core/, app/schemas/
- [X] T005 [P] Create .env.example file with required environment variables (DATABASE_URL, BETTER_AUTH_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, ALLOWED_ORIGINS, HOST, PORT, APP_ENV, DEBUG, LOG_LEVEL)
- [X] T006 [P] Create .gitignore file for Python project (exclude .env, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create Settings class in Phase-3/backend/app/core/config.py with Pydantic BaseSettings for environment variables
- [X] T008 [P] Create async database engine and session factory in Phase-3/backend/app/core/database.py using SQLModel and asyncpg
- [X] T009 [P] Create JWT verification functions in Phase-3/backend/app/core/auth.py (verify_token, get_current_user_id) following Phase 2 pattern
- [X] T010 [P] Create Conversation SQLModel in Phase-3/backend/app/models/conversation.py with id (UUID), user_id, created_at, updated_at, indexes
- [X] T011 [P] Create Message SQLModel in Phase-3/backend/app/models/message.py with id (UUID), conversation_id, user_id, role (enum), content, tool_calls (JSON), created_at, indexes
- [X] T012 [P] Create Pydantic schemas in Phase-3/backend/app/schemas/chat.py (ChatRequest, ChatResponse, ToolCall)
- [X] T013 [P] Create Pydantic schemas in Phase-3/backend/app/schemas/mcp.py for MCP tool parameters and results (AddTaskParams, AddTaskResult, ListTasksParams, etc.)
- [X] T014 Create FastAPI app instance in Phase-3/backend/app/main.py with CORS middleware, startup event for table creation, and router includes
- [X] T015 [P] Create health check endpoints in Phase-3/backend/app/api/v1/health.py (GET /health/live, GET /health/ready)
- [X] T016 Create ConversationRepository in Phase-3/backend/app/repositories/conversation_repository.py with create, get_by_id, get_by_user methods
- [X] T017 Create MessageRepository in Phase-3/backend/app/repositories/message_repository.py with create, get_history methods (fetch last 20 messages)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage tasks through natural language conversation. AI agent interprets intent, calls appropriate MCP tool, and returns friendly confirmation.

**Independent Test**: Send POST request to `/api/{user_id}/chat` with message "Add task to buy groceries" and verify response confirms task creation and task appears in database.

### Implementation for User Story 1

- [X] T018 [P] [US1] Implement add_task MCP tool in Phase-3/backend/app/mcp/tools/add_task.py using @mcp.tool() decorator and Phase 2 task repository
- [X] T019 [P] [US1] Implement list_tasks MCP tool in Phase-3/backend/app/mcp/tools/list_tasks.py with status filter (all, pending, completed)
- [X] T020 [P] [US1] Implement complete_task MCP tool in Phase-3/backend/app/mcp/tools/complete_task.py with task_id parameter
- [X] T021 [P] [US1] Implement delete_task MCP tool in Phase-3/backend/app/mcp/tools/delete_task.py with task_id parameter
- [X] T022 [P] [US1] Implement update_task MCP tool in Phase-3/backend/app/mcp/tools/update_task.py with optional title and description
- [X] T023 [US1] Initialize MCP server in Phase-3/backend/app/mcp/server.py and register all 5 tools (depends on T018-T022)
- [X] T024 [US1] Implement ChatService in Phase-3/backend/app/services/chat_service.py with OpenAI Agent integration, MCP tool execution, and conversation management (depends on T023)
- [X] T025 [US1] Implement POST /api/{user_id}/chat endpoint in Phase-3/backend/app/api/v1/chat.py with JWT verification, request validation, ChatService call, and response formatting (depends on T024)
- [ ] T026 [US1] Add error handling for tool execution failures in ChatService (TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR)
- [ ] T027 [US1] Add request validation in chat endpoint (message required, 1-2000 chars, conversation_id optional integer)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can manage tasks via natural language

---

## Phase 4: User Story 2 - Stateless Conversation Continuity (Priority: P2)

**Goal**: Enable conversation continuity across server restarts by fetching conversation history from database on each request.

**Independent Test**: Create a conversation, restart FastAPI server, send another message with same conversation_id, verify AI has context from previous messages.

### Implementation for User Story 2

- [ ] T028 [US2] Add conversation history fetching logic to ChatService.process() method in Phase-3/backend/app/services/chat_service.py (fetch last 20 messages via MessageRepository)
- [ ] T029 [US2] Add conversation creation logic to ChatService when conversation_id is not provided (create new Conversation via ConversationRepository)
- [ ] T030 [US2] Add conversation ownership validation in ChatService (verify conversation.user_id matches authenticated user_id before processing)
- [ ] T031 [US2] Add message persistence logic to ChatService (save user message and assistant response with tool_calls to database via MessageRepository)
- [ ] T032 [US2] Add conversation history truncation logic to ChatService (keep last 20 messages for OpenAI token limits, oldest first for chronological context)
- [ ] T033 [US2] Update chat endpoint to handle conversation_id parameter and return conversation_id in response

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - conversations persist across server restarts

---

## Phase 5: User Story 3 - Intelligent Error Handling (Priority: P3)

**Goal**: Provide user-friendly error messages when AI agent encounters errors instead of technical error codes.

**Independent Test**: Trigger various error conditions (invalid task_id, OpenAI API timeout, database error) and verify system returns appropriate user-friendly messages.

### Implementation for User Story 3

- [ ] T034 [P] [US3] Add OpenAI API error handling in ChatService (timeout, rate limit, invalid API key) with user-friendly messages
- [ ] T035 [P] [US3] Add database error handling in repositories (connection failure, query timeout) with generic error messages
- [ ] T036 [US3] Add MCP tool error propagation in ChatService (catch tool exceptions, format as user-friendly responses)
- [ ] T037 [US3] Add HTTP exception handlers in Phase-3/backend/app/main.py for 400, 401, 403, 500 errors with consistent error response format
- [ ] T038 [US3] Add conversation not found error handling in ChatService (return 404 when conversation_id doesn't exist or belongs to another user)
- [ ] T039 [US3] Add ambiguous command handling in AI agent system prompt (guide agent to ask for clarification when task_id is missing)

**Checkpoint**: All user stories should now be independently functional with graceful error handling

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T040 [P] Add logging configuration in Phase-3/backend/app/core/config.py (structured logging with log level from env)
- [ ] T041 [P] Add logging statements in ChatService for debugging (conversation start, tool calls, errors)
- [ ] T042 [P] Add logging statements in MCP tools for audit trail (tool invocation, parameters, results)
- [ ] T043 [P] Create README.md in Phase-3/backend/ with setup instructions, environment variables, running locally
- [ ] T044 [P] Create Dockerfile in Phase-3/backend/ for containerized deployment
- [ ] T045 [P] Add type hints validation by running mypy on app/ directory
- [ ] T046 [P] Add code formatting by running ruff format on app/ directory
- [ ] T047 [P] Add linting by running ruff check on app/ directory
- [ ] T048 Verify quickstart.md instructions by following setup steps from scratch
- [ ] T049 Manual testing: Send various natural language messages and verify correct tool calls and responses
- [ ] T050 Manual testing: Verify conversation continuity after server restart

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 but independently testable

### Within Each User Story

**User Story 1 (Natural Language Task Management)**:
1. MCP tools (T018-T022) can run in parallel - different files
2. MCP server initialization (T023) depends on all tools
3. ChatService (T024) depends on MCP server
4. Chat endpoint (T025) depends on ChatService
5. Error handling and validation (T026-T027) can run after endpoint

**User Story 2 (Stateless Conversation Continuity)**:
1. All tasks (T028-T033) modify ChatService and chat endpoint sequentially
2. Each task builds on previous conversation management logic

**User Story 3 (Intelligent Error Handling)**:
1. OpenAI and database error handling (T034-T035) can run in parallel - different layers
2. Tool error propagation (T036) depends on understanding tool errors
3. HTTP exception handlers (T037) can run in parallel with other error handling
4. Specific error cases (T038-T039) can run after core error handling

### Parallel Opportunities

- **Phase 1 Setup**: T003, T004, T005, T006 can run in parallel
- **Phase 2 Foundational**: T008, T009, T010, T011, T012, T013, T015 can run in parallel (different files)
- **User Story 1**: T018, T019, T020, T021, T022 (all MCP tools) can run in parallel
- **User Story 3**: T034, T035, T037 can run in parallel (different layers)
- **Phase 6 Polish**: T040, T041, T042, T043, T044, T045, T046, T047 can run in parallel

---

## Parallel Example: User Story 1 MCP Tools

```bash
# Launch all MCP tools together (different files, no dependencies):
Task T018: "Implement add_task MCP tool in Phase-3/backend/app/mcp/tools/add_task.py"
Task T019: "Implement list_tasks MCP tool in Phase-3/backend/app/mcp/tools/list_tasks.py"
Task T020: "Implement complete_task MCP tool in Phase-3/backend/app/mcp/tools/complete_task.py"
Task T021: "Implement delete_task MCP tool in Phase-3/backend/app/mcp/tools/delete_task.py"
Task T022: "Implement update_task MCP tool in Phase-3/backend/app/mcp/tools/update_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T017) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T018-T027)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send "Add task to buy groceries" → verify task created
   - Send "Show me all my tasks" → verify tasks listed
   - Send "Mark task 3 as complete" → verify task completed
   - Send "Delete task 5" → verify task deleted
   - Send "Change task 1 to 'Call mom tonight'" → verify task updated
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Users can manage tasks via natural language
3. Add User Story 2 → Test independently → Deploy/Demo
   - Conversations persist across server restarts
4. Add User Story 3 → Test independently → Deploy/Demo
   - Graceful error handling with user-friendly messages
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T017)
2. Once Foundational is done:
   - Developer A: User Story 1 (T018-T027)
   - Developer B: User Story 2 (T028-T033) - can start in parallel
   - Developer C: User Story 3 (T034-T039) - can start in parallel
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use uv for all dependency management (uv add, uv run)
- Tables created automatically via SQLModel on FastAPI startup (no Alembic migrations)
- MCP tools MUST call Phase 2 task repository (not direct SQL)
- All database operations MUST be async (await session.exec())
- JWT verification MUST match Phase 2 pattern (JWKS verification)
- Conversation history MUST be truncated to last 20 messages for token limits
