---
id: 0002
title: chatbot-backend-plan
stage: plan
date: 2026-02-21
surface: agent
model: claude-sonnet-4-6
feature: 001-chatbot-backend
branch: 001-chatbot-backend
user: syedhuzaifa
command: /sp.plan
labels: ["phase-3", "chatbot", "backend", "planning", "openai-agents", "mcp", "stateless"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-chatbot-backend/plan.md
  - specs/001-chatbot-backend/research.md
  - specs/001-chatbot-backend/data-model.md
  - specs/001-chatbot-backend/contracts/chat-api.yaml
  - specs/001-chatbot-backend/contracts/mcp-tools.yaml
  - specs/001-chatbot-backend/quickstart.md
  - CLAUDE.md (updated with Phase 3 technologies)
tests:
  - None (planning phase - tests will be created during implementation)
---

## Prompt

User requested: "now write a plan refrence file is @specs/001-chatbot-backend/spec.md and the main hackathon requiremnt file is @phase-3.md"

Context: User wants to create implementation plan for Phase 3 chatbot backend based on the specification. The plan should include technical context, constitution compliance check, research findings, design artifacts (data model, API contracts, MCP tools), and quickstart guide.

Key requirements from spec.md:
- Stateless FastAPI backend with OpenAI Agents SDK
- MCP server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Chat endpoint: POST /api/{user_id}/chat
- Database: Conversation and Message models (new), Task model (existing from Phase 2)
- JWT verification via Better Auth (same pattern as Phase 2)
- Multi-tenancy enforcement at all layers
- Async/await for all I/O operations

## Response snapshot

Created comprehensive implementation plan with Phase 0 (Research) and Phase 1 (Design) complete:

**Phase 0: Research (research.md)**
- R1: OpenAI Agents SDK integration pattern (per-request agent with conversation history)
- R2: Official MCP SDK for Python (@mcp.tool() decorator with Pydantic schemas)
- R3: Stateless conversation management (fetch last 20 messages from database)
- R4: Better Auth JWT verification (reuse Phase 2 pattern)
- R5: Database migration strategy (Alembic migration for new tables)

**Phase 1: Design Artifacts**
1. **data-model.md**: Entity definitions for Conversation, Message, Task (existing)
   - Conversation: id, user_id, created_at, updated_at
   - Message: id, conversation_id, user_id, role, content, tool_calls, created_at
   - Indexes for performance: (user_id, created_at), (conversation_id, created_at)

2. **contracts/chat-api.yaml**: OpenAPI 3.0 specification
   - POST /api/{user_id}/chat endpoint
   - Request: message (required), conversation_id (optional)
   - Response: conversation_id, response, tool_calls
   - Error codes: 400, 401, 403, 500

3. **contracts/mcp-tools.yaml**: MCP tool specifications
   - 5 tools with parameters, returns, examples, errors
   - Agent behavior guidelines
   - Multi-tenancy enforcement rules

4. **quickstart.md**: Developer setup guide
   - Environment setup, dependencies, database migration
   - Running locally, testing chat endpoint
   - Common issues and troubleshooting

**Constitution Check**: ✅ ALL PASS
- Spec-First Integrity: Complete spec exists
- N-Tier Architecture: Clear layer separation (api/services/repositories/mcp)
- Multi-tenancy: user_id filtering at all layers
- Asynchronous First: All I/O operations async

**Project Structure**: Phase-3/backend with N-Tier architecture
- app/api/v1/ (routes)
- app/services/ (business logic)
- app/repositories/ (data access)
- app/mcp/tools/ (MCP tool implementations)

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation. All technical unknowns resolved through research. Design artifacts provide clear contracts for implementation.
- 🧪 Tests: No tests yet (planning phase). Test strategy defined in plan: contract tests, integration tests, unit tests.
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, 2 contract files, quickstart.md) + updated CLAUDE.md
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks from this plan
- 🧠 Reflection: Planning phase complete with zero constitution violations. Stateless architecture clearly defined. MCP tools bridge Phase 2 tasks with Phase 3 chatbot. Research resolved all technical unknowns (OpenAI Agents SDK, MCP SDK, JWT verification pattern). Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 4 core principles + standards)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Proceed to /sp.tasks to generate implementation tasks
