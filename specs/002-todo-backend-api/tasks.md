# Tasks: Backend API for Task Management

**Input**: Design documents from `/specs/002-todo-backend-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this implementation plan as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

All paths are relative to `Phase-2/backend/` directory:
- Application code: `app/`
- Tests: `tests/`
- Configuration: root level (pyproject.toml, .env.example)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Phase-2/backend directory structure per plan.md (app/, app/api/, app/api/v1/, app/services/, app/repositories/, app/models/, app/core/, tests/)
- [X] T002 Initialize Python project with uv in Phase-2/backend/ (uv init, set requires-python = ">=3.12")
- [X] T003 [P] Add production dependencies via uv (fastapi, sqlmodel, pyjwt, psycopg[binary], uvicorn[standard], python-dotenv)
- [X] T004 [P] Add development dependencies via uv (pytest, pytest-asyncio, httpx, ruff)
- [X] T005 [P] Create .env.example in Phase-2/backend/ with DATABASE_URL, BETTER_AUTH_SECRET, APP_ENV, DEBUG, LOG_LEVEL, ALLOWED_ORIGINS, HOST, PORT
- [X] T006 [P] Create .gitignore in Phase-2/backend/ (exclude .env, __pycache__, *.pyc, .pytest_cache, .ruff_cache)
- [X] T007 [P] Create README.md in Phase-2/backend/ with setup instructions referencing quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create app/__init__.py (empty file for package initialization)
- [X] T009 Create app/core/__init__.py (empty file for package initialization)
- [X] T010 [P] Implement configuration management in app/core/config.py (Settings class with DATABASE_URL, BETTER_AUTH_SECRET, environment variables using pydantic-settings)
- [X] T011 [P] Implement database connection and async session management in app/core/database.py (create_async_engine, async_session_maker, engine configuration per research.md)
- [X] T012 [P] Implement JWT verification utilities in app/core/auth.py (verify_jwt function using pyjwt, HTTPBearer security, validate token signature/expiry per research.md)
- [X] T013 Create app/models/__init__.py (empty file for package initialization)
- [X] T014 Implement Task model and Pydantic schemas in app/models/task.py (Task SQLModel with all fields from data-model.md, TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse, TaskSingleResponse, ErrorResponse schemas with validation)
- [X] T015 Create app/main.py with FastAPI application initialization (FastAPI instance, lifespan context manager for SQLModel.metadata.create_all, CORS middleware configuration, include routers)
- [X] T016 Create app/api/__init__.py (empty file for package initialization)
- [X] T017 Create app/api/v1/__init__.py (empty file for package initialization)
- [X] T018 Implement dependency injection functions in app/api/dependencies.py (get_db_session, get_task_repository, get_task_service per research.md pattern)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can retrieve their complete task list with multi-tenant data isolation

**Independent Test**: Authenticate as User A, create tasks via database, call GET /api/{user_id}/tasks, verify only User A's tasks are returned

### Implementation for User Story 1

- [X] T019 Create app/repositories/__init__.py (empty file for package initialization)
- [X] T020 [US1] Implement TaskRepository.find_by_user_id method in app/repositories/task_repository.py (async method, SELECT with WHERE user_id filter, return list of Task, exclude deleted tasks)
- [X] T021 Create app/services/__init__.py (empty file for package initialization)
- [X] T022 [US1] Implement TaskService.list_tasks method in app/services/task_service.py (async method, call repository.find_by_user_id, return list of tasks, handle empty list case)
- [X] T023 [US1] Implement GET /api/{user_id}/tasks endpoint in app/api/v1/tasks.py (async route handler, verify user_id matches JWT, call service.list_tasks, return TaskListResponse with status/data/meta)
- [X] T024 [US1] Add user_id path parameter validation in app/api/v1/tasks.py (verify current_user["user_id"] == path user_id, raise HTTPException 403 if mismatch)
- [X] T025 [US1] Register tasks router in app/main.py (app.include_router with prefix and tags)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can view their tasks

---

## Phase 4: User Story 2 - Create New Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks that are automatically associated with their user account

**Independent Test**: Authenticate as User A, POST to /api/{user_id}/tasks with task data, verify task is created and associated with User A

### Implementation for User Story 2

- [X] T026 [P] [US2] Implement TaskRepository.create method in app/repositories/task_repository.py (async method, create Task instance with user_id, add to session, commit, refresh, return Task)
- [X] T027 [US2] Implement TaskService.create_task method in app/services/task_service.py (async method, validate input data, set user_id from authenticated user, call repository.create, return created task)
- [X] T028 [US2] Implement POST /api/{user_id}/tasks endpoint in app/api/v1/tasks.py (async route handler, verify user_id matches JWT, parse TaskCreateRequest, call service.create_task, return TaskSingleResponse with 201 status)
- [X] T029 [US2] Add input validation error handling in app/api/v1/tasks.py (catch Pydantic ValidationError, return 400 with clear error message per FR-008)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can create and view tasks (MVP complete!)

---

## Phase 5: User Story 3 - Update Existing Tasks (Priority: P2)

**Goal**: Users can modify their existing tasks with ownership verification

**Independent Test**: Authenticate as User A, create a task, PATCH to /api/{user_id}/tasks/{task_id} with updates, verify changes persisted and User B cannot update User A's task

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement TaskRepository.find_by_id method in app/repositories/task_repository.py (async method, SELECT with WHERE id AND user_id filter, return Task or None)
- [X] T031 [P] [US3] Implement TaskRepository.update method in app/repositories/task_repository.py (async method, find task by id and user_id, apply updates via setattr, update updated_at timestamp, commit, refresh, return Task or None)
- [X] T032 [US3] Implement TaskService.update_task method in app/services/task_service.py (async method, call repository.find_by_id, raise HTTPException 404 if not found, validate business rules - cannot update deleted tasks per FR-013, call repository.update, return updated task)
- [X] T033 [US3] Implement PATCH /api/{user_id}/tasks/{task_id} endpoint in app/api/v1/tasks.py (async route handler, verify user_id matches JWT, parse TaskUpdateRequest, call service.update_task, return TaskSingleResponse)
- [X] T034 [US3] Implement GET /api/{user_id}/tasks/{task_id} endpoint in app/api/v1/tasks.py (async route handler, verify user_id matches JWT, call service.get_task, return TaskSingleResponse or 404)
- [X] T035 [US3] Implement TaskService.get_task method in app/services/task_service.py (async method, call repository.find_by_id, raise HTTPException 404 if not found, return task)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P3)

**Goal**: Users can remove tasks they no longer need with soft delete

**Independent Test**: Authenticate as User A, create a task, DELETE to /api/{user_id}/tasks/{task_id}, verify task status set to 'deleted' and no longer appears in list

### Implementation for User Story 4

- [X] T036 [P] [US4] Implement TaskRepository.soft_delete method in app/repositories/task_repository.py (async method, find task by id and user_id, set status='deleted', update updated_at, commit, return True or False)
- [X] T037 [US4] Implement TaskService.delete_task method in app/services/task_service.py (async method, call repository.find_by_id, raise HTTPException 404 if not found, call repository.soft_delete, return success)
- [X] T038 [US4] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in app/api/v1/tasks.py (async route handler, verify user_id matches JWT, call service.delete_task, return success response with 200 status)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T039 [P] Add comprehensive docstrings to all modules (app/models/task.py, app/repositories/task_repository.py, app/services/task_service.py, app/api/v1/tasks.py)
- [X] T040 [P] Configure CORS middleware in app/main.py (allow origins from ALLOWED_ORIGINS env var, allow credentials, allow methods, allow headers)
- [X] T041 [P] Add request logging middleware in app/api/middleware.py (log request method, path, user_id, response status, duration)
- [X] T042 [P] Add health check endpoint in app/api/v1/health.py (GET /health returns status and database connectivity check)
- [X] T043 Verify all async functions use proper error handling (HTTPException with appropriate status codes per FR-009)
- [X] T044 Verify all repository methods include user_id filtering (audit all queries for multi-tenancy compliance per SC-002)
- [X] T045 [P] Run ruff format and ruff check on all Python files (ensure code quality and consistency)
- [X] T046 Verify API documentation is accessible at /docs (FastAPI auto-generated Swagger UI per FR-011)
- [X] T047 Manual testing following quickstart.md validation steps (verify all endpoints work with JWT authentication)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (but logically follows US1 for MVP)
  - User Story 3 (P2): Can start after Foundational - No dependencies on other stories
  - User Story 4 (P3): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Can be implemented and tested alone
- **User Story 2 (P1)**: Independent - Can be implemented and tested alone (forms MVP with US1)
- **User Story 3 (P2)**: Independent - Can be implemented and tested alone
- **User Story 4 (P3)**: Independent - Can be implemented and tested alone

### Within Each User Story

- Repository methods before service methods
- Service methods before route endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006, T007)
- All Foundational tasks marked [P] can run in parallel within Phase 2 (T010, T011, T012)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Repository methods within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational infrastructure tasks together:
Task: "Implement configuration management in app/core/config.py"
Task: "Implement database connection in app/core/database.py"
Task: "Implement JWT verification in app/core/auth.py"
```

## Parallel Example: User Story 3

```bash
# Launch repository methods together:
Task: "Implement TaskRepository.find_by_id in app/repositories/task_repository.py"
Task: "Implement TaskRepository.update in app/repositories/task_repository.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T018) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T019-T025) - View tasks
4. Complete Phase 4: User Story 2 (T026-T029) - Create tasks
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (read-only MVP)
3. Add User Story 2 → Test independently → Deploy/Demo (full MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo (update capability)
5. Add User Story 4 → Test independently → Deploy/Demo (delete capability)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (T019-T025)
   - Developer B: User Story 2 (T026-T029)
   - Developer C: User Story 3 (T030-T035)
   - Developer D: User Story 4 (T036-T038)
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 47
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 11 tasks (BLOCKING)
- Phase 3 (US1 - View Tasks): 7 tasks
- Phase 4 (US2 - Create Tasks): 4 tasks
- Phase 5 (US3 - Update Tasks): 6 tasks
- Phase 6 (US4 - Delete Tasks): 3 tasks
- Phase 7 (Polish): 9 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-4 (29 tasks) deliver a functional task management API with view and create capabilities

**Independent Test Criteria**:
- US1: Can view tasks filtered by user_id
- US2: Can create tasks associated with user_id
- US3: Can update own tasks, cannot update others' tasks
- US4: Can delete own tasks (soft delete), cannot delete others' tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All async functions must use `async def` and `await`
- All repository queries MUST include user_id filtering
- All routes MUST verify user_id matches authenticated user
- Follow Phase-2/backend/CLAUDE.md conventions (app/ directory, HTTPException in services, co-located models/schemas)
