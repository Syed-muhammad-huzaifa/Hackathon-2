




























# Tasks: AI Chatbot Frontend for Task Management

**Input**: Design documents from `/specs/001-chatbot-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All paths relative to `Phase-3/frontend/` directory.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Next.js 15 project with TypeScript in Phase-3/frontend/ directory
- [ ] T002 [P] Install core dependencies: Better Auth, OpenAI ChatKit, Recharts, Tailwind CSS, Framer Motion, Lucide React, Zod
- [ ] T003 [P] Configure TypeScript with strict mode in tsconfig.json
- [ ] T004 [P] Configure Tailwind CSS with dark theme colors and custom utilities in tailwind.config.ts
- [ ] T005 [P] Configure Next.js with font optimization and environment variables in next.config.js
- [ ] T006 [P] Create environment variables template in .env.example (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_CHATKIT_DOMAIN_KEY)
- [ ] T007 [P] Setup ESLint and Prettier for code quality
- [ ] T008 Create project directory structure per plan.md (src/app, src/components, src/lib, src/types, src/styles, src/config)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Design System & Styling

- [ ] T009 [P] Create global styles with dark theme and custom scrollbar in src/app/globals.css
- [ ] T010 [P] Configure Inter font with Next.js font optimization in src/config/fonts.ts
- [ ] T011 [P] Create theme configuration with color palette and gradients in src/config/theme.ts
- [ ] T012 [P] Create animation variants for Framer Motion in src/lib/animations/variants.ts
- [ ] T013 [P] Create transition configurations in src/lib/animations/transitions.ts

### Base UI Components (shadcn/ui)

- [ ] T014 [P] Create Button component with premium styling in src/components/ui/button.tsx
- [ ] T015 [P] Create Card component with glassmorphism in src/components/ui/card.tsx
- [ ] T016 [P] Create Input component with focus animations in src/components/ui/input.tsx
- [ ] T017 [P] Create Dialog component with backdrop blur in src/components/ui/dialog.tsx
- [ ] T018 [P] Create Toast component for notifications in src/components/ui/toast.tsx

### TypeScript Types

- [ ] T019 [P] Create auth types (User, Session) in src/types/auth.ts
- [ ] T020 [P] Create chat types (Message, Conversation, ChatRequest, ChatResponse, ToolCall) in src/types/chat.ts
- [ ] T021 [P] Create task types (Task, TaskStatusData, TaskTrendData) in src/types/task.ts
- [ ] T022 [P] Create API types (ErrorResponse) in src/types/api.ts
- [ ] T023 Create type index file re-exporting all types in src/types/index.ts

### Utility Functions

- [ ] T024 [P] Create Tailwind class merger utility in src/lib/utils/cn.ts
- [ ] T025 [P] Create date/time formatting utilities in src/lib/utils/format.ts
- [ ] T026 [P] Create color palette utilities in src/lib/utils/colors.ts
- [ ] T027 [P] Create environment variable validation with Zod in src/config/env.ts

### Better Auth Integration (Phase 2 Session Reading)

- [ ] T028 Create session reading functions (getJWTToken, isAuthenticated) in src/lib/auth/session.ts
- [ ] T029 Create auth middleware for protected routes in middleware.ts
- [ ] T030 Create useAuth hook for client-side auth state in src/lib/hooks/useAuth.ts
- [ ] T031 Create API route to check authentication status in src/app/api/auth/check/route.ts

### API Client

- [ ] T032 Create base API client with JWT header injection in src/lib/api/client.ts
- [ ] T033 Create chat API functions (sendMessage) in src/lib/api/chat.ts
- [ ] T034 Create analytics API functions (getTasks) in src/lib/api/analytics.ts

### Root Layout

- [ ] T035 Create root layout with font and theme provider in src/app/layout.tsx
- [ ] T036 Create error boundary component in src/components/ErrorBoundary.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authentication System (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, sign in, and access protected dashboard routes using Better Auth JWT tokens

**Independent Test**: Visit landing page, click signup, create account, verify redirect to dashboard, sign out, sign back in

### Implementation for User Story 1

- [ ] T037 [P] [US1] Create AuthCard component with glassmorphism styling in src/components/auth/AuthCard.tsx
- [ ] T038 [P] [US1] Create SignUpForm component with validation in src/components/auth/SignUpForm.tsx
- [ ] T039 [P] [US1] Create SignInForm component with validation in src/components/auth/SignInForm.tsx
- [ ] T040 [US1] Create auth layout with minimal gradient background in src/app/(auth)/layout.tsx
- [ ] T041 [US1] Create signup page in src/app/(auth)/signup/page.tsx
- [ ] T042 [US1] Create signin page in src/app/(auth)/signin/page.tsx
- [ ] T043 [US1] Implement sign-out functionality in dashboard header
- [ ] T044 [US1] Add error handling for authentication failures (invalid credentials, email exists)
- [ ] T045 [US1] Add loading states for signup/signin forms
- [ ] T046 [US1] Test authentication flow: signup → dashboard → signout → signin

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Landing Page & Navigation (Priority: P2)

**Goal**: Premium landing page with hero, features, CTAs, and dashboard navigation

**Independent Test**: Visit landing page, verify premium design, click CTAs, navigate between dashboard pages

### Landing Page Components

- [ ] T047 [P] [US2] Create Hero component with animated gradient text in src/components/landing/Hero.tsx
- [ ] T048 [P] [US2] Create Features component with feature cards in src/components/landing/Features.tsx
- [ ] T049 [P] [US2] Create CTA component with gradient buttons in src/components/landing/CTA.tsx
- [ ] T050 [P] [US2] Create AnimatedBackground component in src/components/landing/AnimatedBackground.tsx

### Dashboard Layout Components

- [ ] T051 [P] [US2] Create DashboardSidebar component with navigation links in src/components/layout/DashboardSidebar.tsx
- [ ] T052 [P] [US2] Create DashboardHeader component with user menu in src/components/layout/DashboardHeader.tsx
- [ ] T053 [P] [US2] Create Navigation component with active state in src/components/layout/Navigation.tsx
- [ ] T054 [P] [US2] Create MobileNav component with hamburger menu in src/components/layout/MobileNav.tsx
- [ ] T055 [P] [US2] Create LoadingScreen component with premium animation in src/components/layout/LoadingScreen.tsx

### Page Implementation

- [ ] T056 [US2] Create landing page with hero, features, and CTAs in src/app/page.tsx
- [ ] T057 [US2] Create dashboard layout with sidebar and header in src/app/(dashboard)/layout.tsx
- [ ] T058 [US2] Add responsive breakpoints for mobile, tablet, desktop
- [ ] T059 [US2] Add page transition animations with Framer Motion
- [ ] T060 [US2] Test navigation flow: landing → signup → dashboard → all pages

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Conversational Task Management (Priority: P3)

**Goal**: Users can manage tasks through natural language chat interface using OpenAI ChatKit

**Independent Test**: Sign in, navigate to chatbot page, send natural language commands, verify AI responses and task operations

### Chat Components

- [ ] T061 [P] [US3] Create ChatInterface component with OpenAI ChatKit integration in src/components/chat/ChatInterface.tsx
- [ ] T062 [P] [US3] Create MessageBubble component with glassmorphism in src/components/chat/MessageBubble.tsx
- [ ] T063 [P] [US3] Create TypingIndicator component with animation in src/components/chat/TypingIndicator.tsx
- [ ] T064 [P] [US3] Create MessageInput component with send animation in src/components/chat/MessageInput.tsx
- [ ] T065 [P] [US3] Create ToolCallBadge component for MCP tool display in src/components/chat/ToolCallBadge.tsx

### Chat State Management

- [ ] T066 [US3] Create useChat hook for conversation state management in src/lib/hooks/useChat.ts
- [ ] T067 [US3] Implement conversation persistence (send conversation_id with requests)
- [ ] T068 [US3] Implement optimistic updates for message sending
- [ ] T069 [US3] Add error handling for API failures with retry logic

### OpenAI ChatKit Setup

- [ ] T070 [US3] Configure OpenAI ChatKit with domain key and theme in ChatInterface component
- [ ] T071 [US3] Create ChatKit session API route in src/app/api/chatkit/session/route.ts
- [ ] T072 [US3] Create ChatKit refresh API route in src/app/api/chatkit/refresh/route.ts
- [ ] T073 [US3] Customize ChatKit theme for dark mode and glassmorphism

### Page Implementation

- [ ] T074 [US3] Create chatbot page with ChatInterface in src/app/(dashboard)/chatbot/page.tsx
- [ ] T075 [US3] Add auto-scroll to latest message functionality
- [ ] T076 [US3] Add "New Conversation" button to start fresh chat
- [ ] T077 [US3] Add message timestamps display
- [ ] T078 [US3] Test natural language commands: add task, list tasks, complete task, delete task, update task

**Checkpoint**: All core chat functionality should now be working independently

---

## Phase 6: User Story 4 - Task Analytics and Insights Dashboard (Priority: P4)

**Goal**: Users can view visual charts showing task statistics and trends

**Independent Test**: Create tasks via chat, navigate to analytics, verify charts display accurate data

### Analytics Components

- [ ] T079 [P] [US4] Create StatusChart component with Recharts donut chart in src/components/analytics/StatusChart.tsx
- [ ] T080 [P] [US4] Create TrendChart component with Recharts line chart in src/components/analytics/TrendChart.tsx
- [ ] T081 [P] [US4] Create StatsCard component with glassmorphism in src/components/analytics/StatsCard.tsx
- [ ] T082 [P] [US4] Create EmptyState component for no data in src/components/analytics/EmptyState.tsx

### Analytics State Management

- [ ] T083 [US4] Create useAnalytics hook for data fetching in src/lib/hooks/useAnalytics.ts
- [ ] T084 [US4] Implement data transformation functions (tasks → chart data)
- [ ] T085 [US4] Add loading states for chart rendering
- [ ] T086 [US4] Add error handling for data fetch failures

### Page Implementation

- [ ] T087 [US4] Create analytics page with charts and stats in src/app/(dashboard)/analytics/page.tsx
- [ ] T088 [US4] Add responsive chart sizing for mobile/tablet/desktop
- [ ] T089 [US4] Add chart animations and transitions
- [ ] T090 [US4] Test analytics: create tasks → navigate to analytics → verify charts update

**Checkpoint**: Analytics dashboard should display accurate task data independently

---

## Phase 7: User Story 5 - Settings Page (Priority: P5)

**Goal**: Users can manage account preferences and profile information

**Independent Test**: Navigate to settings, verify profile display, update name, change password

### Settings Components

- [ ] T091 [P] [US5] Create ProfileSection component in src/components/settings/ProfileSection.tsx
- [ ] T092 [P] [US5] Create PreferencesSection component with toggles in src/components/settings/PreferencesSection.tsx
- [ ] T093 [P] [US5] Create SecuritySection component with password change in src/components/settings/SecuritySection.tsx
- [ ] T094 [P] [US5] Create DangerZone component with account deletion in src/components/settings/DangerZone.tsx

### Settings API

- [ ] T095 [US5] Create settings API functions (updateProfile, changePassword, deleteAccount) in src/lib/api/settings.ts
- [ ] T096 [US5] Add validation for settings changes with Zod schemas
- [ ] T097 [US5] Add confirmation dialogs for destructive actions

### Page Implementation

- [ ] T098 [US5] Create settings page with all sections in src/app/(dashboard)/settings/page.tsx
- [ ] T099 [US5] Add loading states for settings updates
- [ ] T100 [US5] Add success/error toast notifications
- [ ] T101 [US5] Test settings: update profile → change password → verify changes

**Checkpoint**: Settings page should allow profile management independently

---

## Phase 8: User Story 6 - Additional Dashboard Pages (Priority: P6)

**Goal**: Provide 2 additional pages for extended functionality (Task History and Help/Documentation)

**Independent Test**: Navigate to additional pages, verify content and consistent design

### Task History Page

- [ ] T102 [P] [US6] Create TaskHistoryItem component with timeline styling in src/components/history/TaskHistoryItem.tsx
- [ ] T103 [P] [US6] Create TaskTimeline component in src/components/history/TaskTimeline.tsx
- [ ] T104 [US6] Create task history page in src/app/(dashboard)/history/page.tsx
- [ ] T105 [US6] Add filtering by date range and status
- [ ] T106 [US6] Add animations for timeline items

### Help/Documentation Page

- [ ] T107 [P] [US6] Create HelpSection component in src/components/help/HelpSection.tsx
- [ ] T108 [P] [US6] Create SearchBar component for help search in src/components/help/SearchBar.tsx
- [ ] T109 [US6] Create help page with categorized documentation in src/app/(dashboard)/help/page.tsx
- [ ] T110 [US6] Add search functionality for help topics
- [ ] T111 [US6] Add FAQ section with expandable items

### Testing

- [ ] T112 [US6] Test task history: create/complete tasks → view history → verify timeline
- [ ] T113 [US6] Test help page: search topics → verify results → navigate categories

**Checkpoint**: Additional pages should provide value and maintain design consistency

---

## Phase 9: User Story 7 - Chat Interface Enhancements (Priority: P7)

**Goal**: Polish chat UX with typing indicators, timestamps, error handling, and conversation management

**Independent Test**: Send messages, verify typing indicator, test error scenarios, clear conversation

### Chat Enhancements

- [ ] T114 [US7] Add typing indicator animation when AI is processing
- [ ] T115 [US7] Add message timestamps with relative time formatting
- [ ] T116 [US7] Add error messages with retry buttons for failed requests
- [ ] T117 [US7] Add "Clear Conversation" functionality with confirmation
- [ ] T118 [US7] Add Enter to send, Shift+Enter for new line
- [ ] T119 [US7] Add formatted task list display in chat bubbles
- [ ] T120 [US7] Add helpful error guidance for ambiguous commands
- [ ] T121 [US7] Add loading skeleton for conversation history
- [ ] T122 [US7] Test all enhancements: typing indicator, timestamps, errors, conversation clearing

**Checkpoint**: Chat interface should provide polished, production-ready UX

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Responsive Design Optimization

- [ ] T123 [P] Test and optimize mobile layout (320px - 639px)
- [ ] T124 [P] Test and optimize tablet layout (640px - 1023px)
- [ ] T125 [P] Test and optimize desktop layout (1024px+)
- [ ] T126 [P] Add touch gestures for mobile (swipe navigation)
- [ ] T127 [P] Optimize tap targets for mobile (minimum 44x44px)

### Performance Optimization

- [ ] T128 [P] Implement code splitting for analytics and settings pages
- [ ] T129 [P] Add lazy loading for images and heavy components
- [ ] T130 [P] Optimize bundle size (analyze with next/bundle-analyzer)
- [ ] T131 [P] Add loading states for all async operations
- [ ] T132 [P] Optimize Recharts rendering performance

### Accessibility

- [ ] T133 [P] Add ARIA labels to all interactive elements
- [ ] T134 [P] Implement keyboard navigation for all features
- [ ] T135 [P] Add visible focus states with ring-2 ring-indigo-500
- [ ] T136 [P] Test color contrast ratios (minimum 4.5:1)
- [ ] T137 [P] Add screen reader support for chat messages

### Error Handling & Edge Cases

- [ ] T138 Handle session expiration gracefully (redirect to signin with message)
- [ ] T139 Handle network errors with retry logic and user feedback
- [ ] T140 Handle malformed backend responses with error boundaries
- [ ] T141 Handle concurrent chat sessions (warn or sync state)
- [ ] T142 Handle very long messages (over 1000 characters)

### Documentation & Deployment

- [ ] T143 Create README.md with setup instructions
- [ ] T144 Create quickstart.md validation script
- [ ] T145 Document environment variables in .env.example
- [ ] T146 Create deployment guide for Vercel/Netlify
- [ ] T147 Configure OpenAI ChatKit domain allowlist for production

### Testing & QA

- [ ] T148 [P] Write component tests for critical components (Vitest + RTL)
- [ ] T149 [P] Write E2E tests for authentication flow (Playwright)
- [ ] T150 [P] Write E2E tests for chat flow (Playwright)
- [ ] T151 Run Lighthouse audit and optimize for 90+ score
- [ ] T152 Test cross-browser compatibility (Chrome, Firefox, Safari, Edge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6 → P7)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Requires US1 (authentication) and US2 (navigation) for full testing
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Requires US3 (chat) to create tasks for analytics
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Requires US1 (authentication) for profile management
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Requires US3 (chat) for task history data
- **User Story 7 (P7)**: Depends on US3 (chat) being complete - Enhances existing chat functionality

### Within Each User Story

- Components marked [P] can run in parallel (different files)
- Components before state management
- State management before page implementation
- Core implementation before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1, US2, US5 can start in parallel (independent stories)
- US3, US4, US6, US7 should wait for US1 and US2 to complete
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 3 (Chat)

```bash
# Launch all chat components together:
Task: "Create ChatInterface component in src/components/chat/ChatInterface.tsx"
Task: "Create MessageBubble component in src/components/chat/MessageBubble.tsx"
Task: "Create TypingIndicator component in src/components/chat/TypingIndicator.tsx"
Task: "Create MessageInput component in src/components/chat/MessageInput.tsx"
Task: "Create ToolCallBadge component in src/components/chat/ToolCallBadge.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Landing & Navigation)
5. Complete Phase 5: User Story 3 (Chat)
6. **STOP and VALIDATE**: Test all three stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Auth working!)
3. Add User Story 2 → Test independently → Deploy/Demo (Landing + Nav working!)
4. Add User Story 3 → Test independently → Deploy/Demo (MVP complete - chat working!)
5. Add User Story 4 → Test independently → Deploy/Demo (Analytics added!)
6. Add User Story 5 → Test independently → Deploy/Demo (Settings added!)
7. Add User Story 6 → Test independently → Deploy/Demo (Additional pages added!)
8. Add User Story 7 → Test independently → Deploy/Demo (Chat polished!)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Landing & Navigation)
   - Developer C: User Story 5 (Settings)
3. After US1 and US2 complete:
   - Developer A: User Story 3 (Chat)
   - Developer B: User Story 4 (Analytics)
4. After US3 completes:
   - Developer C: User Story 6 (Additional Pages)
   - Developer A: User Story 7 (Chat Enhancements)
5. All developers: Phase 10 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Premium UI requirements (glassmorphism, animations, gradients) embedded in each task
- OpenAI ChatKit integration is mandatory per hackathon requirements
- Backend API endpoint `POST /api/{user_id}/chat` is fixed per hackathon requirements
- Better Auth reads Phase 2 session cookies (no separate auth implementation needed)
- All paths relative to `Phase-3/frontend/` directory
- Dark theme is primary (no light mode for MVP)
- 100% responsive design required (320px to 2560px+)
