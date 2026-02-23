# Feature Specification: AI Chatbot Backend with MCP Server

**Feature Branch**: `001-chatbot-backend`
**Created**: 2026-02-21
**Status**: Draft
**Input**: User description: "Phase 3 backend - AI chatbot with OpenAI Agents SDK, MCP server, and stateless chat endpoint"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Management (Priority: P1)

A user sends a natural language message to the chatbot (e.g., "Add a task to buy groceries") and receives an AI-generated response confirming the action was completed. The AI agent interprets the intent, calls the appropriate MCP tool, and returns a friendly confirmation.

**Why this priority**: This is the core value proposition - enabling users to manage tasks through conversation instead of forms and buttons. Without this, the chatbot has no purpose.

**Independent Test**: Can be fully tested by sending a POST request to `/api/{user_id}/chat` with a message like "Add task to call mom" and verifying the response confirms task creation and the task appears in the database.

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** user sends "Add a task to buy groceries", **Then** AI agent calls add_task tool and responds "✓ Task added: Buy groceries"
2. **Given** user is authenticated, **When** user sends "Show me all my tasks", **Then** AI agent calls list_tasks tool and responds with formatted list of user's tasks
3. **Given** user has task with id=3, **When** user sends "Mark task 3 as complete", **Then** AI agent calls complete_task tool and responds "✓ Task completed: [task title]"
4. **Given** user is authenticated, **When** user sends "Delete task 5", **Then** AI agent calls delete_task tool and responds "✓ Task deleted: [task title]"
5. **Given** user has task with id=1, **When** user sends "Change task 1 to 'Call mom tonight'", **Then** AI agent calls update_task tool and responds "✓ Task updated: Call mom tonight"

---

### User Story 2 - Stateless Conversation Continuity (Priority: P2)

A user starts a conversation, the server restarts, and the user continues the same conversation seamlessly. The system fetches conversation history from the database on each request, enabling horizontal scaling and resilience.

**Why this priority**: Stateless architecture is critical for production scalability and reliability. Without this, the system cannot handle server restarts or scale horizontally.

**Independent Test**: Can be tested by creating a conversation, restarting the FastAPI server, then sending another message with the same conversation_id and verifying the AI has context from previous messages.

**Acceptance Scenarios**:

1. **Given** user has existing conversation_id=123, **When** user sends new message with conversation_id=123, **Then** system fetches conversation history from database and AI responds with context from previous messages
2. **Given** server restarts, **When** user sends message with existing conversation_id, **Then** conversation continues without data loss
3. **Given** user sends message without conversation_id, **When** request is processed, **Then** system creates new conversation and returns new conversation_id

---

### User Story 3 - Intelligent Error Handling (Priority: P3)

When the AI agent encounters errors (task not found, OpenAI API failure, database error), it responds with helpful, user-friendly messages instead of crashing or returning technical error codes.

**Why this priority**: Good error handling improves user experience but is not critical for core functionality. Can be enhanced iteratively.

**Independent Test**: Can be tested by triggering various error conditions (invalid task_id, OpenAI API timeout, database connection failure) and verifying the system returns appropriate error messages.

**Acceptance Scenarios**:

1. **Given** user requests to delete task_id=999 that doesn't exist, **When** AI agent calls delete_task tool, **Then** tool returns error and AI responds "I couldn't find task 999. Would you like to see your current tasks?"
2. **Given** OpenAI API is unavailable, **When** user sends message, **Then** system returns "I'm having trouble connecting right now. Please try again in a moment."
3. **Given** user tries to access another user's conversation, **When** request is processed, **Then** system returns 403 Forbidden error

---

### Edge Cases

- **Large conversation history**: What happens when conversation has 100+ messages? System must truncate old messages to stay within OpenAI token limits while preserving recent context.
- **Concurrent requests**: How does system handle multiple users sending messages simultaneously? Database transactions ensure data consistency.
- **Token expiration mid-conversation**: What happens if JWT expires during active conversation? System returns 401 and frontend re-authenticates.
- **Ambiguous commands**: How does AI handle "delete task" without specifying which one? Agent should list tasks and ask user to specify task_id.
- **Tool execution failures**: What happens if MCP tool fails (database error, constraint violation)? Agent receives error message and responds with user-friendly explanation.
- **Invalid conversation_id**: What happens if user provides conversation_id that doesn't exist or belongs to another user? System returns error and creates new conversation.
- **OpenAI rate limits**: How does system handle rate limit errors? Return 429 status with retry-after header.
- **Very long messages**: What happens if user sends message exceeding token limits? Truncate message or return validation error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a stateless chat endpoint at `POST /api/{user_id}/chat` that accepts message and optional conversation_id
- **FR-002**: System MUST verify JWT token on every request and ensure user_id in URL matches JWT subject claim
- **FR-003**: System MUST integrate OpenAI Agents SDK to process natural language messages and determine appropriate tool calls
- **FR-004**: System MUST implement MCP server using Official MCP SDK with 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-005**: System MUST persist all user messages and assistant responses to database with conversation_id, role, content, and timestamp
- **FR-006**: System MUST fetch conversation history from database on each request to provide context to AI agent
- **FR-007**: System MUST create new conversation if conversation_id is not provided in request
- **FR-008**: System MUST validate that conversation_id belongs to authenticated user before processing request
- **FR-009**: MCP tools MUST access the Phase 3 tasks table in the Phase 3 separate Neon database
- **FR-010**: MCP tools MUST enforce row-level security ensuring users can only access their own tasks
- **FR-011**: System MUST return conversation_id, assistant response, and list of tool_calls in response
- **FR-012**: System MUST handle OpenAI API errors gracefully and return user-friendly error messages
- **FR-013**: System MUST handle database errors gracefully without exposing internal details to users
- **FR-014**: System MUST truncate conversation history to stay within OpenAI token limits (default: last 20 messages)
- **FR-015**: System MUST store tool call results in database for debugging and audit purposes
- **FR-016**: System MUST support CORS for frontend hosted on different domain
- **FR-017**: System MUST validate request payload (message required, conversation_id optional UUID)
- **FR-018**: System MUST return appropriate HTTP status codes (200 success, 400 bad request, 401 unauthorized, 403 forbidden, 500 server error)

### Key Entities

- **Conversation**: Represents a chat session between user and AI assistant. Attributes: id (primary key), user_id (foreign key to users table), created_at, updated_at. Relationships: belongs to User, has many Messages.

- **Message**: Represents a single message in a conversation. Attributes: id (primary key), conversation_id (foreign key), user_id (foreign key), role (enum: 'user' or 'assistant'), content (text), tool_calls (JSON array, optional), created_at. Relationships: belongs to Conversation and User.

- **Task**: Phase 3 entity in its own separate database. Attributes: id (UUID), user_id (str), title, description, status ('pending'|'in_progress'|'completed'|'deleted'), priority, created_at, updated_at. MCP tools create/read/update/delete rows in this table.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a natural language message and receive AI response with task operation completed in under 5 seconds (95th percentile)
- **SC-002**: System maintains conversation context across server restarts with zero data loss
- **SC-003**: System handles 100 concurrent chat requests without degradation in response time
- **SC-004**: AI agent correctly interprets user intent and calls appropriate MCP tool in 90% of test cases
- **SC-005**: System gracefully handles OpenAI API failures and returns user-friendly error messages in 100% of error scenarios
- **SC-006**: Conversation history is accurately persisted and retrieved from database in 100% of requests
- **SC-007**: Users can resume conversations after any time period with full context preserved
- **SC-008**: MCP tools enforce row-level security preventing users from accessing other users' tasks in 100% of cases

## Assumptions

- OpenAI API key is available and has sufficient quota for expected usage
- Phase 3 has its own separate Neon PostgreSQL database (not shared with Phase 2)
- Phase 3 has its own separate Better Auth instance running on the Phase 3 frontend
- Frontend will handle JWT token refresh when token expires
- Conversation history truncation at 20 messages provides sufficient context for most use cases
- OpenAI Agents SDK supports MCP tool integration (as per Official MCP SDK documentation)
- Database connection pooling is configured to handle concurrent requests
- CORS configuration allows requests from Phase 3 frontend domain

## Dependencies

- Phase 3 separate Neon PostgreSQL database (tasks, conversations, messages tables; Better Auth user/session tables)
- OpenAI API access and API key (Groq/OpenAI-compatible)
- Official MCP SDK for Python
- OpenAI Agents SDK for Python
- Better Auth JWKS endpoint for JWT verification (Phase 3 frontend)

## Out of Scope

- Frontend implementation (covered in separate frontend spec)
- User authentication endpoints (handled by Phase 3 Better Auth on the frontend)
- Task CRUD REST API endpoints (chat agent manages tasks exclusively via MCP tools)
- Real-time streaming responses (future enhancement)
- Multi-language support (English only for MVP)
- Voice input/output (future enhancement)
- File attachments in chat (future enhancement)
- Conversation search functionality (future enhancement)
- Analytics and usage tracking (future enhancement)
