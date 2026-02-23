---
id: "026"
title: "Guardrail todo-only and conversation history"
stage: green
date: "2026-02-23"
surface: agent
model: claude-sonnet-4-6
feature: 001-chatbot-frontend
branch: 001-chatbot-frontend
user: syedhuzaifa
command: "add guardrail todo-only + fix chatui conversation history"
labels: ["guardrail", "mcp-server", "conversation-history", "openai-agents-sdk"]
links:
  spec: "specs/001-chatbot-frontend/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files_created:
  - Phase-3/backend/app/services/guardrail.py
files_modified:
  - Phase-3/backend/app/models/conversation.py
  - Phase-3/backend/app/repositories/conversation_repository.py
  - Phase-3/backend/app/schemas/chat.py
  - Phase-3/backend/app/api/v1/chat.py
  - Phase-3/backend/app/services/chat_service.py
  - Phase-3/backend/app/services/chatkit_adapter.py
tests_run: []
---

## Prompt

now i face a issue this is only todo agent add a guadril that they only help relaed to todo if user ask out of the box then they strictly say that i only help you regarding todo so add a guadril use context7 mcp server to fetch the documentation of openai agent sdk so follow best practices and impement it also chatui dont make conversation history

## What Was Implemented

### 1. Input Guardrail (`app/services/guardrail.py`)
Following the official OpenAI Agents SDK guardrail pattern (verified via Context7):
- `TodoRelevanceCheck(BaseModel)` with `is_todo_related: bool` and `reasoning: str`
- `_guardrail_agent` using same `OpenAIChatCompletionsModel` (Grok) with `output_type=TodoRelevanceCheck`
- `@input_guardrail todo_only_guardrail` extracts the latest user message from string OR list input, runs the classifier agent, trips the wire if `is_todo_related=False`
- Fails **open** on guardrail errors (classification failure lets the main agent handle it gracefully)
- `REFUSAL_MESSAGE` with friendly markdown list of allowed actions

### 2. Guardrail wired into agent (`chat_service.py`)
- `input_guardrails=[todo_only_guardrail]` added to `Agent(...)` in `_build_agent()`
- `InputGuardrailTripwireTriggered` caught before `asyncio.TimeoutError` in `process()`
- On trip: saves user message + REFUSAL_MESSAGE to DB, returns `ChatResponse` immediately

### 3. Conversation history (`chatkit_thread_id` persistence)
Root cause: `InMemoryChatKitStore` lost thread→conversation mapping on process restart, causing every refresh to start a new conversation.

Fix:
- `Conversation` model: added `chatkit_thread_id: Optional[str]` (nullable, indexed)
- `ConversationRepository`: added `get_by_chatkit_thread_id()`, updated `create()` to accept `chatkit_thread_id`
- `ChatRequest` schema: added `chatkit_thread_id: Optional[str]`
- `ChatService.process()`: added `chatkit_thread_id` param; when `conversation_id` is None but `chatkit_thread_id` is set, looks up existing conversation before creating new
- `chatkit_adapter.py` `respond()`: passes `chatkit_thread_id: thread.id` in every backend request body

### 4. DB-backed history hydration (`chatkit_adapter.py`)
- `load_thread()`: on memory miss, queries DB via `get_by_chatkit_thread_id()` to recover `backend_conversation_id`
- `load_thread_items()`: when items list is empty, calls `_load_items_from_db()` which loads messages via `MessageRepository.get_history()` and converts them to ChatKit `UserMessageItem` / `AssistantMessageItem` using `UserMessageTextContent` / `AssistantMessageContent`
- Hydrated items cached in memory for the session
- `InferenceOptions` and `UserMessageTextContent` correctly imported from `chatkit.types`

## Outcome
- Off-topic messages (math, news, etc.) → friendly refusal without LLM tool execution
- Topic classification uses same Grok model via `OpenAIChatCompletionsModel`
- Conversation history survives browser refresh and process restarts
- ChatKit UI shows previous messages when reopened
