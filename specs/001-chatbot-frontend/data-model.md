# Data Model: AI Chatbot Frontend

**Feature**: 001-chatbot-frontend
**Date**: 2026-02-21
**Status**: Complete

## Overview

This document defines the frontend data structures for the AI chatbot task management application. The frontend is stateless - all persistent data is managed by the backend. These models represent the shape of data as it flows through the frontend application.

---

## 1. Authentication & Session

### User

Represents an authenticated user (from Phase 2).

```typescript
interface User {
  id: string;              // Unique user identifier (from Phase 2 Better Auth)
  email: string;           // User's email address
  name: string;            // User's display name
  image?: string;          // Optional profile image URL
  emailVerified: boolean;  // Email verification status
  createdAt: Date;         // Account creation timestamp
}
```

**Source**: Phase 2 Better Auth session data
**Usage**: Displayed in header, used for API calls (user.id)

---

### Session

Represents an active authentication session (from Phase 2).

```typescript
interface Session {
  user: User;              // User information
  session: {
    id: string;            // Session identifier
    userId: string;        // Reference to user.id
    expiresAt: Date;       // Session expiration timestamp
    token: string;         // JWT token (if needed for API calls)
  };
}
```

**Source**: Phase 2 Better Auth session (read from cookies)
**Usage**: Auth state management, protected route access

**Note**: Phase 3 reads existing Phase 2 session - does not create or modify sessions.

---

## 2. Chat & Messaging

### Message

Represents a single message in the chat conversation.

```typescript
type MessageRole = 'user' | 'assistant';

interface Message {
  id: string;              // Unique message identifier
  role: MessageRole;       // Who sent the message
  content: string;         // Message text content
  timestamp: Date;         // When message was sent
  toolCalls?: ToolCall[];  // MCP tools invoked (assistant messages only)
  status?: 'sending' | 'sent' | 'error';  // Message status (optimistic updates)
}
```

**Source**:
- User messages: Created locally, sent to backend
- Assistant messages: Received from backend via ChatKit

**Usage**: Displayed in chat interface

---

### ToolCall

Represents an MCP tool invocation by the AI agent.

```typescript
interface ToolCall {
  tool: string;            // Tool name (e.g., "add_task", "list_tasks")
  parameters: Record<string, any>;  // Tool input parameters
  result: any;             // Tool execution result
}
```

**Source**: Backend response (tool_calls array)
**Usage**: Displayed as metadata in chat (optional, subtle UI indicator)

---

### Conversation

Represents a chat conversation session.

```typescript
interface Conversation {
  id: string;              // Conversation identifier (UUID from backend)
  userId: string;          // Owner user ID
  messages: Message[];     // Array of messages in conversation
  createdAt: Date;         // Conversation start timestamp
  updatedAt: Date;         // Last message timestamp
}
```

**Source**: Backend (conversation_id in API responses)
**Usage**: Conversation state management, message history

---

### ChatRequest

Request payload for sending messages to backend.

```typescript
interface ChatRequest {
  message: string;         // User's message text
  conversation_id?: string; // Optional: existing conversation ID
}
```

**Destination**: `POST /api/{user_id}/chat`

---

### ChatResponse

Response from backend chat endpoint.

```typescript
interface ChatResponse {
  conversation_id: string;  // Conversation identifier
  response: string;         // AI assistant's response text
  tool_calls: ToolCall[];   // MCP tools invoked during processing
}
```

**Source**: Backend `POST /api/{user_id}/chat` response

---

## 3. Task Management (for Analytics)

### Task

Represents a task item (used for analytics display only).

```typescript
type TaskStatus = 'pending' | 'completed' | 'deleted';

interface Task {
  id: string;              // Task identifier (UUID)
  userId: string;          // Owner user ID
  title: string;           // Task title
  description?: string;    // Optional task description
  status: TaskStatus;      // Task status
  createdAt: Date;         // Task creation timestamp
  updatedAt: Date;         // Last update timestamp
}
```

**Source**: Backend (fetched for analytics dashboard)
**Usage**: Analytics charts, task statistics

**Note**: Tasks are NOT managed directly in frontend. Users create/update tasks through natural language chat. This model is only for displaying analytics.

---

### TaskStatusData

Data structure for status distribution chart.

```typescript
interface TaskStatusData {
  name: string;            // Status label (e.g., "Completed", "Pending")
  value: number;           // Count of tasks with this status
  color: string;           // Chart color for this status
}
```

**Source**: Transformed from Task[] array
**Usage**: Recharts PieChart data

**Example**:
```typescript
const statusData: TaskStatusData[] = [
  { name: 'Completed', value: 45, color: '#10b981' },
  { name: 'Pending', value: 23, color: '#f59e0b' },
  { name: 'Deleted', value: 4, color: '#ef4444' },
];
```

---

### TaskTrendData

Data structure for completion trend chart.

```typescript
interface TaskTrendData {
  date: string;            // Date label (e.g., "Jan", "2024-01-15")
  completed: number;       // Tasks completed on this date
  created: number;         // Tasks created on this date
}
```

**Source**: Transformed from Task[] array (grouped by date)
**Usage**: Recharts LineChart data

**Example**:
```typescript
const trendData: TaskTrendData[] = [
  { date: 'Jan', completed: 45, created: 52 },
  { date: 'Feb', completed: 52, created: 48 },
  { date: 'Mar', completed: 61, created: 55 },
];
```

---

## 4. UI State

### ChatState

Local state for chat interface.

```typescript
interface ChatState {
  conversationId: string | null;  // Current conversation ID
  messages: Message[];            // Message history
  isLoading: boolean;             // Waiting for AI response
  error: string | null;           // Error message if any
  inputValue: string;             // Current input text
}
```

**Source**: React state (useState, useReducer)
**Usage**: Chat interface component state

---

### AnalyticsState

Local state for analytics dashboard.

```typescript
interface AnalyticsState {
  tasks: Task[];           // All tasks for analytics
  isLoading: boolean;      // Fetching data
  error: string | null;    // Error message if any
  dateRange: {
    start: Date;
    end: Date;
  };                       // Date range filter
}
```

**Source**: React state + API fetch
**Usage**: Analytics dashboard component state

---

## 6. API Error Responses

### ErrorResponse

Standard error response from backend.

```typescript
interface ErrorResponse {
  status: 'error';
  code: string;            // Error code (e.g., "UNAUTHORIZED", "VALIDATION_ERROR")
  message: string;         // User-friendly error message
  details?: Record<string, any>;  // Optional error details
}
```

**Source**: Backend error responses
**Usage**: Error handling, user feedback

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Phase 2      │───▶│ Read Session │───▶│   Session    │ │
│  │ Session      │    │ from Cookies │    │   (User)     │ │
│  │ (Cookies)    │    │              │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                 │            │
│                                                 ▼            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Chat UI      │───▶│  ChatKit     │───▶│ Conversation │ │
│  │ (OpenAI)     │    │  Component   │    │  + Messages  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                              │
│         │                    ▼                              │
│         │            ┌──────────────┐                       │
│         └───────────▶│ API Client   │                       │
│                      │ (fetch)      │                       │
│                      └──────────────┘                       │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Backend API      │
                    │ (FastAPI)        │
                    │                  │
                    │ POST /api/{id}/  │
                    │      chat        │
                    └──────────────────┘
```

**Note**: Phase 2 handles authentication. Phase 3 only reads existing session cookies.

---

## Type Definitions Location

All TypeScript types should be centralized in `/src/types/`:

```
/src/types/
├── auth.ts          # User, Session (from Phase 2)
├── chat.ts          # Message, Conversation, ChatRequest, ChatResponse
├── task.ts          # Task, TaskStatusData, TaskTrendData
├── api.ts           # ErrorResponse, API client types
└── index.ts         # Re-export all types
```

**Note**: No form data types needed - Phase 2 handles authentication forms.

---

## Validation Strategy

**Client-Side Validation** (UX):
- Zod schemas for chat message validation
- Inline error messages
- Prevent invalid submissions

**Backend Validation** (Security):
- Backend validates all inputs
- Frontend validation is for UX only
- Never trust client-side validation alone

**No Authentication Validation Needed**: Phase 2 handles all auth validation.

---

## State Management Summary

| Data Type | Storage | Persistence | Source |
|-----------|---------|-------------|--------|
| User Session | Phase 2 cookies (read-only) | 7 days | Phase 2 Better Auth |
| Chat Messages | ChatKit internal state | Session | Backend API |
| Conversation ID | React state | Session | Backend API |
| Task Data (Analytics) | React state | None (fetch on demand) | Backend API |

**Note**: Phase 3 does not manage authentication state - only reads existing Phase 2 session.

---

## Notes

1. **Stateless Frontend**: All persistent data lives on backend. Frontend only holds temporary UI state.
2. **No Direct Task CRUD**: Users manage tasks through natural language chat, not forms.
3. **Analytics Read-Only**: Task data fetched only for analytics display, not for editing.
4. **Type Safety**: All data structures have TypeScript types with strict mode enabled.
5. **Validation**: Zod schemas for runtime validation of user input and API responses.
