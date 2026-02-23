# Implementation Plan: AI Chatbot Frontend for Task Management

**Branch**: `001-chatbot-frontend` | **Date**: 2026-02-21 | **Updated**: 2026-02-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chatbot-frontend/spec.md`
**Hackathon Requirements**: [phase-3.md](../../phase-3.md)

## Summary

Build an AI-powered chatbot frontend using OpenAI ChatKit for conversational task management with a **separate Better Auth authentication system** (not linked to Phase 2). Phase 3 is a standalone application with **premium UI design** and **100% responsive layout** featuring: landing page, signup/signin, and dashboard containing Chatbot page, Analytics page, Settings page, and 2 additional pages (Task History, Help/Documentation). Better Auth generates JWT tokens on authentication, frontend sends JWT to backend for verification. The frontend is stateless - all conversation state, task data, and AI agent logic are handled by the backend (001-chatbot-backend). Frontend responsibilities: authentication UI, landing page, dashboard navigation, chat interface integration, analytics visualization, settings management.

**Technical Approach**: Next.js 15 App Router with TypeScript, Better Auth for authentication (JWT generation), OpenAI ChatKit for chat UI, Recharts/Chart.js for analytics, Tailwind CSS for styling with **premium design system**. All API calls to backend endpoint `POST /api/{user_id}/chat` with JWT in Authorization header.

**Design Philosophy**: Premium, modern, dark-themed interface with glassmorphism effects, smooth animations, gradient accents, and professional typography. 100% responsive from mobile (320px) to ultra-wide (2560px+).

**Note**: This frontend is built in a separate folder (`Phase-3/frontend/`) and deployed independently. Phase 3 has its own Better Auth system and does NOT integrate with Phase 2.

## Technical Context

**Language/Version**: TypeScript 5.x (strict mode, zero 'any' types)
**Framework**: Next.js 15 (App Router only, React 19)
**Primary Dependencies**:
- Better Auth (authentication with JWT generation)
- OpenAI ChatKit (chat interface component - **hackathon requirement**)
- Recharts or Chart.js (analytics charts)
- Tailwind CSS (styling with custom design system)
- Framer Motion (premium animations and transitions)
- Lucide React (premium icon set)
- Zod (schema validation)

**Storage**: httpOnly cookies (JWT tokens via Better Auth), all data persisted on backend via API calls
**Testing**: Vitest + React Testing Library (component tests), Playwright (E2E tests)
**Target Platform**: 100% responsive - mobile (320px) → tablet (768px) → desktop (1024px) → ultra-wide (2560px+)
**Project Type**: Full-stack web application with premium UI/UX design
**Performance Goals**:
- Landing page load: < 3 seconds on 3G
- Signup/signin: < 2 seconds
- Dashboard load: < 1 second after authentication
- Chat interface load: < 2 seconds
- Message send → AI response: < 5 seconds
- 60fps animations and scrolling across all devices
- Lighthouse score: 90+ (Performance, Accessibility, Best Practices)

**Premium UI/UX Requirements** (100% mandatory):
- **Dark theme** with high-contrast elements and gradient accents
- **Glassmorphism** effects for cards, modals, and chat bubbles
- **Smooth animations** for all interactions (page transitions, button clicks, message sending)
- **Premium typography** using Inter, Geist Sans, or SF Pro Display
- **Gradient backgrounds** with subtle patterns and depth
- **Micro-interactions** (hover effects, loading states, success animations)
- **Custom scrollbars** styled to match dark theme
- **Responsive breakpoints**: mobile-first design with fluid layouts
- **Touch-optimized** for mobile devices (larger tap targets, swipe gestures)
- **Accessibility** (ARIA labels, keyboard navigation, focus states)

**Constraints**:
- Must integrate with existing backend API (001-chatbot-backend) at `POST /api/{user_id}/chat` (**hackathon requirement**)
- **Phase 3 has separate Better Auth system** (not linked to Phase 2)
- **Better Auth generates JWT tokens** on signup/signin
- **Frontend sends JWT to backend** in `Authorization: Bearer <token>` header
- **Backend verifies JWT** using Phase 3 Better Auth JWKS endpoint
- **OpenAI ChatKit** requires domain allowlist configuration (**hackathon requirement**)
- **100% responsive** design (320px min → 2560px+ max)
- **Premium UI** across all pages (landing, auth, dashboard, chat, analytics, settings)
- Dark theme as primary interface (no light mode for MVP)
- No direct MCP tool integration (backend handles all AI agent logic via **OpenAI Agents SDK** - **hackathon requirement**)
- Must implement authentication UI (signup/signin forms)
- Must implement landing page with hero and features
- Must implement dashboard with multiple pages (Chatbot, Analytics, Settings, Task History, Help)

**Scale/Scope**:
- Single-user sessions (no real-time multi-user collaboration)
- Up to 100 messages per conversation in UI (pagination for older messages)
- Supports concurrent browser tabs (conversation state synced via backend)
- Analytics for up to 1000 tasks per user
- Optimized for modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Spec-First Integrity ✅ PASS

- Specification exists at `specs/001-chatbot-frontend/spec.md`
- All 90 functional requirements documented
- 7 prioritized user stories with acceptance scenarios
- Implementation will reference spec in code comments

**Compliance**: All code will include `@spec: specs/001-chatbot-frontend/spec.md (FR-XXX)` references

---

### II. N-Tier Layered Architecture ⚠️ PARTIAL APPLICABILITY

**Status**: Frontend architecture differs from backend N-Tier pattern

**Frontend Layer Separation** (adapted for React/Next.js):
- **Presentation Layer**: React components (pages, UI components)
- **Service Layer**: API client functions, business logic helpers
- **State Management**: React Server Components (default), Client Components (interactivity only)

**Rules Applied**:
- Components MUST NOT contain API call logic (use service functions)
- Service functions MUST NOT contain JSX or UI logic
- API client isolated in `/lib/api/` directory
- Authentication logic isolated in `/lib/auth/` directory
- Better Auth configuration isolated in `/lib/auth/config.ts`

**Justification**: Frontend doesn't have Repository layer (backend handles data access). Adapted principles: separation of concerns, single responsibility, clear boundaries.

---

### III. Mandatory Multi-tenancy ✅ PASS

**Frontend Responsibilities**:
- Better Auth manages user sessions and generates JWT tokens
- Extract `user_id` from JWT token (via Better Auth session)
- Send JWT in `Authorization: Bearer <token>` header to backend
- Never allow manual `user_id` manipulation
- Display only data returned by backend (backend enforces user_id filtering)

**Backend Enforcement**: Backend (001-chatbot-backend) enforces multi-tenancy at every layer. Backend verifies JWT and validates user_id from JWT claims.

**Compliance**:
- Better Auth handles user authentication and JWT generation
- All API calls include JWT in Authorization header
- Backend verifies JWT signature and validates user_id
- No client-side user_id manipulation possible (backend rejects invalid tokens with 401/403)

---

### IV. Asynchronous First ✅ PASS

**Frontend Async Operations**:
- All API calls use async/await with fetch or axios
- React Server Components for async data fetching
- Client Components use React hooks (useEffect, useSWR) for async operations
- No blocking operations in UI rendering
- Better Auth operations are async

**Compliance**:
- All API client functions declared with `async`
- Loading states displayed during async operations
- Error boundaries handle async failures gracefully

---

### Key Standards Compliance

**Frontend Standards** ✅ PASS:
- Next.js 15 (App Router only) ✓
- TypeScript strict mode, zero 'any' types ✓
- Tailwind CSS mobile-first ✓
- **Better Auth for authentication** (separate Phase 3 system) ✓
- React Server Components by default ✓
- Semantic HTML, ARIA labels, keyboard navigation ✓
- Responsive breakpoints: mobile (default), md:, lg:, xl: ✓

**Security Standards** ✅ PASS:
- **Better Auth JWT tokens** (7-day validity) ✓
- **JWT stored in httpOnly cookies** (managed by Better Auth) ✓
- **Backend verifies JWT** using Phase 3 Better Auth JWKS endpoint ✓
- HTTPS enforced in production ✓
- Input validation (Zod schemas) ✓
- No hardcoded secrets (environment variables) ✓
- CORS handled by backend ✓

**Performance Standards** ✅ PASS:
- Landing page < 3s on 3G ✓
- Dashboard < 1s after auth ✓
- Chat interface < 2s ✓
- Message response < 5s ✓
- 60fps scrolling ✓

---

### Constitution Violations: NONE

All applicable constitution principles are satisfied. Frontend-specific adaptations documented above.

## Project Structure

### Documentation (this feature)

```text
specs/001-chatbot-frontend/
├── spec.md              # Feature specification (UPDATED 2026-02-22)
├── plan.md              # This file (UPDATING)
├── research.md          # Phase 0 output (NEXT)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   ├── chat-api.yaml    # Backend chat endpoint contract
│   ├── auth-flow.md     # Better Auth integration flow
│   └── analytics-api.yaml # Backend analytics endpoint contract
├── checklists/
│   └── requirements.md  # Spec validation checklist (NEEDS UPDATE)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
Phase-3/frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── (auth)/            # Auth route group (unauthenticated)
│   │   │   ├── signin/
│   │   │   │   └── page.tsx   # Sign in page (premium form design)
│   │   │   ├── signup/
│   │   │   │   └── page.tsx   # Sign up page (premium form design)
│   │   │   └── layout.tsx     # Auth layout (minimal, gradient background)
│   │   │
│   │   ├── (dashboard)/       # Dashboard route group (authenticated)
│   │   │   ├── chatbot/
│   │   │   │   └── page.tsx   # Chatbot page (main feature, glassmorphism chat UI)
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx   # Analytics page (premium charts with animations)
│   │   │   ├── settings/
│   │   │   │   └── page.tsx   # Settings page (organized sections, smooth transitions)
│   │   │   ├── history/
│   │   │   │   └── page.tsx   # Task history page (timeline view with animations)
│   │   │   ├── help/
│   │   │   │   └── page.tsx   # Help/docs page (searchable, categorized)
│   │   │   └── layout.tsx     # Dashboard layout (premium sidebar, animated header)
│   │   │
│   │   ├── api/               # API routes (Better Auth endpoints)
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts # Better Auth handler
│   │   │
│   │   ├── layout.tsx         # Root layout (font optimization, theme provider)
│   │   ├── page.tsx           # Landing page (premium hero, animated features, gradient CTAs)
│   │   └── globals.css        # Global styles (Tailwind + custom animations + scrollbar styling)
│   │
│   ├── components/            # React components (all with premium styling)
│   │   ├── ui/               # shadcn/ui components (customized for dark theme)
│   │   │   ├── button.tsx    # Premium button with hover effects
│   │   │   ├── card.tsx      # Glassmorphism card component
│   │   │   ├── input.tsx     # Styled input with focus animations
│   │   │   ├── dialog.tsx    # Modal with backdrop blur
│   │   │   └── ...           # Other shadcn/ui components
│   │   │
│   │   ├── landing/          # Landing page components (premium design)
│   │   │   ├── Hero.tsx      # Animated hero with gradient text
│   │   │   ├── Features.tsx  # Feature cards with hover effects
│   │   │   ├── CTA.tsx       # Call-to-action with gradient buttons
│   │   │   └── AnimatedBackground.tsx # Gradient background with particles
│   │   │
│   │   ├── auth/             # Auth components (premium forms)
│   │   │   ├── SignInForm.tsx # Sign in form with validation animations
│   │   │   ├── SignUpForm.tsx # Sign up form with step indicators
│   │   │   └── AuthCard.tsx   # Glassmorphism auth container
│   │   │
│   │   ├── chat/             # Chat components (premium chat UI)
│   │   │   ├── ChatInterface.tsx # Main chat container with animations
│   │   │   ├── MessageBubble.tsx # Glassmorphism message bubbles
│   │   │   ├── TypingIndicator.tsx # Animated typing dots
│   │   │   ├── MessageInput.tsx # Premium input with send animation
│   │   │   └── ToolCallBadge.tsx # Badge showing MCP tool invocations
│   │   │
│   │   ├── analytics/        # Analytics components (premium charts)
│   │   │   ├── StatusChart.tsx # Animated donut/pie chart
│   │   │   ├── TrendChart.tsx  # Animated line/bar chart
│   │   │   ├── StatsCard.tsx   # Glassmorphism stats card
│   │   │   └── EmptyState.tsx  # Premium empty state illustration
│   │   │
│   │   ├── settings/         # Settings components (organized sections)
│   │   │   ├── ProfileSection.tsx # Profile editing with avatar
│   │   │   ├── PreferencesSection.tsx # Toggle switches with animations
│   │   │   ├── SecuritySection.tsx # Password change form
│   │   │   └── DangerZone.tsx # Account deletion with confirmation
│   │   │
│   │   └── layout/           # Layout components (premium navigation)
│   │       ├── DashboardSidebar.tsx # Animated sidebar with icons
│   │       ├── DashboardHeader.tsx # Header with user menu
│   │       ├── Navigation.tsx # Navigation with active state animations
│   │       ├── MobileNav.tsx  # Mobile hamburger menu
│   │       └── LoadingScreen.tsx # Premium loading animation
│   │
│   ├── lib/                   # Utility libraries
│   │   ├── api/              # API client functions
│   │   │   ├── chat.ts       # Chat API calls (POST /api/{user_id}/chat)
│   │   │   ├── analytics.ts  # Analytics API calls
│   │   │   └── client.ts     # Base API client (sends JWT, handles errors)
│   │   │
│   │   ├── auth/             # Better Auth configuration
│   │   │   ├── config.ts     # Better Auth setup with JWT
│   │   │   ├── client.ts     # Better Auth client
│   │   │   └── middleware.ts # Auth middleware for protected routes
│   │   │
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useChat.ts    # Chat state management
│   │   │   ├── useAuth.ts    # Auth state management
│   │   │   ├── useAnalytics.ts # Analytics data fetching
│   │   │   └── useMediaQuery.ts # Responsive breakpoint detection
│   │   │
│   │   ├── animations/       # Animation utilities
│   │   │   ├── variants.ts   # Framer Motion variants
│   │   │   └── transitions.ts # Reusable transition configs
│   │   │
│   │   └── utils/            # Helper functions
│   │       ├── cn.ts         # Tailwind class merger
│   │       ├── format.ts     # Date/time formatting
│   │       └── colors.ts     # Color palette utilities
│   │
│   ├── types/                 # TypeScript type definitions
│   │   ├── api.ts            # API request/response types
│   │   ├── chat.ts           # Chat message types
│   │   ├── auth.ts           # Auth types
│   │   └── analytics.ts      # Analytics data types
│   │
│   ├── styles/                # Additional styles
│   │   ├── animations.css    # Custom CSS animations
│   │   └── scrollbar.css     # Custom scrollbar styling
│   │
│   └── config/                # Configuration
│       ├── env.ts            # Environment variables (validated with Zod)
│       ├── theme.ts          # Theme configuration (colors, gradients)
│       └── fonts.ts          # Font configuration (Next.js font optimization)
│
├── public/                    # Static assets
│   ├── fonts/                # Custom fonts (if not using Next.js font optimization)
│   ├── images/               # Images, illustrations
│   └── icons/                # Custom icons, favicons
│
├── tests/                     # Tests
│   ├── components/           # Component tests (Vitest + RTL)
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests (Playwright)
│
├── .env.example              # Environment variables template
├── .env.local                # Local environment (gitignored)
├── next.config.js            # Next.js configuration
├── tailwind.config.ts        # Tailwind configuration (custom colors, animations)
├── tsconfig.json             # TypeScript configuration (strict mode)
├── package.json              # Dependencies
├── postcss.config.js         # PostCSS configuration
└── README.md                 # Setup instructions
```

**Structure Decision**: Full-stack web application with **premium UI/UX design system**. Next.js 15 App Router with route groups for auth and dashboard. Landing page at root with animated hero. Components organized by feature with emphasis on **glassmorphism, animations, and responsive design**. API client sends requests to `POST /api/{user_id}/chat` (**hackathon requirement**). Better Auth logic isolated in `/lib/auth/`. Premium animations in `/lib/animations/`. TypeScript types centralized in `/types/`. Custom styles for animations and scrollbars. Tests mirror source structure.

**Key Architectural Decisions**:
- Route groups `(auth)` and `(dashboard)` for different layouts
- Better Auth API routes at `/api/auth/[...all]`
- Separate layouts: auth (minimal gradient), dashboard (premium sidebar + header)
- Landing page at root route with animated hero and features
- 2 additional pages: Task History (timeline view) and Help/Documentation (searchable)
- **Premium UI components** with glassmorphism, gradients, and smooth animations
- **100% responsive** with mobile-first approach and fluid layouts
- **Framer Motion** for page transitions and micro-interactions
- **Custom Tailwind theme** with dark mode colors and gradient utilities

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All applicable principles satisfied with frontend-specific adaptations documented in Constitution Check section.

## Phase 0: Research & Technology Decisions

**Status**: NEEDS EXECUTION

**Research Tasks**:

1. **Better Auth Integration** (CRITICAL - Hackathon Requirement)
   - Research: How to integrate Better Auth with Next.js 15 App Router
   - Research: Better Auth configuration for email/password authentication
   - Research: JWT token generation and management with Better Auth
   - Research: Better Auth API routes setup (`/api/auth/[...all]`)
   - Research: Better Auth client-side hooks and session management
   - Research: Better Auth JWKS endpoint for backend JWT verification
   - Research: httpOnly cookie configuration for JWT storage
   - Decision needed: Better Auth plugins and configuration options
   - Output: Better Auth setup pattern, configuration examples, integration guide

2. **OpenAI ChatKit Integration** (CRITICAL - Hackathon Requirement)
   - Research: How to integrate OpenAI ChatKit with Next.js 15 App Router
   - Research: ChatKit domain allowlist configuration requirements
   - Research: ChatKit message format and API contract
   - Research: ChatKit customization options (styling, theming for dark mode)
   - Research: ChatKit premium styling (glassmorphism chat bubbles)
   - Decision needed: ChatKit vs custom chat UI implementation
   - Output: Integration pattern, configuration steps, code examples

3. **Backend API Integration** (CRITICAL - Hackathon Requirement)
   - Research: Backend endpoint contract: `POST /api/{user_id}/chat` (**exact endpoint from hackathon requirements**)
   - Research: Sending JWT in `Authorization: Bearer <token>` header
   - Research: Request/response format (conversation_id, message, response, tool_calls)
   - Research: Error handling patterns (401 Unauthorized, 403 Forbidden)
   - Research: Retry logic and timeout handling
   - Research: Analytics endpoint for task data (if separate from chat)
   - Decision needed: API client library (fetch vs axios vs custom)
   - Output: API client implementation pattern, error handling strategy

4. **Premium UI/UX Design System** (CRITICAL - 100% Responsive + Premium Design)
   - Research: Glassmorphism implementation with Tailwind CSS (backdrop-blur, transparency)
   - Research: Dark theme color palette (high contrast, gradient accents)
   - Research: Premium typography (Inter, Geist Sans, SF Pro Display via Next.js font optimization)
   - Research: Gradient backgrounds and patterns (CSS gradients, SVG patterns)
   - Research: Custom scrollbar styling for dark theme
   - Research: Responsive breakpoints strategy (mobile-first, fluid layouts)
   - Research: Touch optimization for mobile (tap targets, swipe gestures)
   - Decision needed: Design system structure and component library approach
   - Output: Design system documentation, color palette, typography scale, spacing system

5. **Animation & Micro-interactions** (HIGH PRIORITY - Premium Feel)
   - Research: Framer Motion integration with Next.js 15 App Router
   - Research: Page transition animations (fade, slide, scale)
   - Research: Micro-interactions (button hover, input focus, message send)
   - Research: Loading animations (skeleton screens, spinners, progress bars)
   - Research: Success/error animations (checkmarks, shake effects)
   - Research: Scroll animations (fade-in on scroll, parallax effects)
   - Research: Performance optimization for animations (GPU acceleration, will-change)
   - Decision needed: Animation library (Framer Motion vs CSS animations vs both)
   - Output: Animation patterns, reusable variants, performance guidelines

6. **Analytics Implementation** (HIGH PRIORITY)
   - Research: Recharts vs Chart.js for Next.js 15 (bundle size, features, customization)
   - Research: Chart types needed (donut/pie for status distribution, line/bar for trends)
   - Research: Chart animations and transitions (smooth data updates)
   - Research: Chart responsiveness (mobile-optimized charts)
   - Research: Dark theme styling for charts (colors, gridlines, tooltips)
   - Research: Data fetching strategy for analytics (API endpoint vs chat commands)
   - Research: Empty state handling for no data (illustrations, CTAs)
   - Decision needed: Charting library selection (Recharts recommended for React)
   - Output: Analytics implementation pattern, chart examples, responsive design

7. **Landing Page Design** (MEDIUM PRIORITY - First Impression)
   - Research: Premium landing page patterns and examples (Vercel, Linear, Stripe)
   - Research: Hero section best practices (animated headline, gradient text, CTA placement)
   - Research: Features section layout (bento grid, feature cards with icons)
   - Research: Animated backgrounds (gradient mesh, particles, subtle motion)
   - Research: Call-to-action design (gradient buttons, hover effects)
   - Research: Responsive landing page design (mobile hero, stacked features)
   - Research: Performance optimization (lazy loading, image optimization)
   - Decision needed: Animation complexity level (subtle vs bold)
   - Output: Landing page component structure, design patterns, animation examples

8. **Responsive Design Strategy** (HIGH PRIORITY - 100% Responsive)
   - Research: Mobile-first CSS approach with Tailwind
   - Research: Breakpoint strategy (sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px)
   - Research: Fluid typography (clamp(), responsive font sizes)
   - Research: Container queries for component-level responsiveness
   - Research: Mobile navigation patterns (hamburger menu, bottom nav)
   - Research: Touch gestures for mobile (swipe to delete, pull to refresh)
   - Research: Responsive images (next/image, srcset, sizes)
   - Research: Testing strategy for multiple devices (Chrome DevTools, BrowserStack)
   - Decision needed: Mobile navigation approach (sidebar vs bottom nav)
   - Output: Responsive design guidelines, breakpoint usage, mobile patterns

9. **State Management** (MEDIUM PRIORITY)
   - Research: React Server Components vs Client Components for different pages
   - Research: Conversation state management (local vs server-synced)
   - Research: Optimistic updates for message sending
   - Research: Better Auth session state management
   - Research: Analytics data caching and refresh strategy
   - Decision needed: State management approach (React hooks vs Zustand vs Jotai)
   - Output: State management pattern, data flow diagram

10. **Accessibility & Performance** (MEDIUM PRIORITY)
    - Research: ARIA labels and semantic HTML for screen readers
    - Research: Keyboard navigation patterns (focus management, shortcuts)
    - Research: Focus states styling for dark theme
    - Research: Color contrast ratios for WCAG compliance
    - Research: Performance optimization (code splitting, lazy loading, image optimization)
    - Research: Lighthouse audit best practices
    - Decision needed: Accessibility testing tools and workflow
    - Output: Accessibility checklist, performance optimization guide

**Output**: `research.md` with all decisions documented, design system specifications, and implementation patterns

## Phase 1: Design & Contracts

**Status**: PENDING (blocked by Phase 0)

**Deliverables**:

1. **data-model.md**: Frontend data structures
   - User type (id, email, name, createdAt)
   - Session type (user, token, expiresAt)
   - Message type (user/assistant, content, timestamp)
   - Conversation type (conversation_id, messages array)
   - Task type (task_id, title, status, priority, timestamps) - for analytics
   - AnalyticsData type (status distribution, completion trends)

2. **contracts/**: API contracts and integration flows
   - `chat-api.yaml`: Backend chat endpoint OpenAPI spec (`POST /api/{user_id}/chat` - **hackathon requirement**)
   - `analytics-api.yaml`: Backend analytics endpoint OpenAPI spec (if separate)
   - `auth-flow.md`: Better Auth authentication flow diagram (signup/signin → JWT → backend)
   - `error-handling.md`: Error response formats and handling strategy

3. **quickstart.md**: Developer setup guide
   - Prerequisites (Node.js 18+, npm/yarn/pnpm)
   - Environment variables setup (DATABASE_URL, BETTER_AUTH_SECRET, BACKEND_API_URL, OPENAI_DOMAIN_KEY)
   - Better Auth configuration and database setup
   - OpenAI ChatKit domain allowlist setup (**hackathon requirement**)
   - Local development server
   - Build and deployment

4. **design-system.md**: Premium UI/UX design system specification
   - Color palette (dark theme with gradient accents)
   - Typography scale (Inter/Geist Sans with responsive sizes)
   - Spacing system (4px base unit, consistent margins/paddings)
   - Component library (buttons, cards, inputs, modals with glassmorphism)
   - Animation guidelines (transition durations, easing functions)
   - Responsive breakpoints (mobile, tablet, desktop, ultra-wide)
   - Accessibility standards (ARIA labels, keyboard navigation, focus states)
   - Icon system (Lucide React with consistent sizing)

5. **responsive-design.md**: 100% responsive design specifications
   - Mobile-first approach (320px minimum width)
   - Breakpoint strategy (sm: 640px, md: 768px, lg: 1024px, xl: 1280px, 2xl: 1536px)
   - Fluid typography (clamp() for responsive font sizes)
   - Mobile navigation patterns (hamburger menu, bottom nav)
   - Touch optimization (larger tap targets, swipe gestures)
   - Responsive images (next/image optimization)
   - Testing strategy (Chrome DevTools, real devices)

## Premium UI/UX Design Guidelines

**Status**: MANDATORY - All pages must follow these guidelines

### Design Philosophy

**Core Principles**:
- **Dark-first**: Dark theme as primary interface with high contrast
- **Glassmorphism**: Frosted glass effects for depth and premium feel
- **Fluid Motion**: Smooth animations that enhance, not distract
- **Responsive Excellence**: Perfect experience from 320px to 2560px+
- **Touch-optimized**: Mobile-first with gesture support

### Color Palette

**Background Layers**:
```
- bg-primary: #0a0a0a (deepest background)
- bg-secondary: #141414 (card backgrounds)
- bg-tertiary: #1e1e1e (elevated elements)
```

**Accent Colors**:
```
- accent-primary: Linear gradient (#6366f1 → #8b5cf6) - Primary CTAs
- accent-secondary: Linear gradient (#ec4899 → #f43f5e) - Secondary actions
- accent-success: #10b981 - Success states
- accent-warning: #f59e0b - Warning states
- accent-error: #ef4444 - Error states
```

**Text Colors**:
```
- text-primary: #ffffff (high emphasis)
- text-secondary: #a1a1aa (medium emphasis)
- text-tertiary: #71717a (low emphasis)
```

**Glassmorphism**:
```
- Glass light: backdrop-blur-xl bg-white/5 border border-white/10
- Glass medium: backdrop-blur-2xl bg-white/10 border border-white/20
- Glass heavy: backdrop-blur-3xl bg-white/15 border border-white/30
```

### Typography

**Font Stack**:
- Primary: Inter (via next/font/google)
- Fallback: system-ui, -apple-system, sans-serif

**Scale** (mobile → desktop):
```
- Heading 1: clamp(2rem, 5vw, 3.5rem) / font-bold
- Heading 2: clamp(1.5rem, 4vw, 2.5rem) / font-bold
- Heading 3: clamp(1.25rem, 3vw, 2rem) / font-semibold
- Body Large: clamp(1.125rem, 2vw, 1.25rem) / font-normal
- Body: 1rem / font-normal
- Body Small: 0.875rem / font-normal
- Caption: 0.75rem / font-medium
```

### Spacing System

**Base Unit**: 4px (Tailwind's default)

**Common Spacing**:
```
- xs: 0.5rem (8px)
- sm: 0.75rem (12px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)
- 3xl: 4rem (64px)
```

### Component Patterns

**Buttons**:
```tsx
// Primary Button (Gradient)
className="px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600
           text-white font-semibold shadow-lg shadow-indigo-500/50
           hover:shadow-xl hover:shadow-indigo-500/60 hover:scale-105
           active:scale-95 transition-all duration-200"

// Secondary Button (Glass)
className="px-6 py-3 rounded-xl backdrop-blur-xl bg-white/5 border border-white/10
           text-white font-semibold hover:bg-white/10 hover:border-white/20
           active:scale-95 transition-all duration-200"
```

**Cards**:
```tsx
// Glass Card
className="p-6 rounded-2xl backdrop-blur-2xl bg-white/5 border border-white/10
           shadow-xl hover:bg-white/10 hover:border-white/20
           transition-all duration-300"

// Elevated Card
className="p-6 rounded-2xl bg-zinc-900 border border-zinc-800
           shadow-2xl hover:shadow-indigo-500/10 hover:border-zinc-700
           transition-all duration-300"
```

**Inputs**:
```tsx
// Text Input
className="w-full px-4 py-3 rounded-xl backdrop-blur-xl bg-white/5
           border border-white/10 text-white placeholder-zinc-500
           focus:bg-white/10 focus:border-indigo-500 focus:ring-2
           focus:ring-indigo-500/20 transition-all duration-200"
```

**Chat Bubbles**:
```tsx
// User Message
className="max-w-[80%] ml-auto px-4 py-3 rounded-2xl rounded-tr-sm
           bg-gradient-to-r from-indigo-500 to-purple-600 text-white
           shadow-lg shadow-indigo-500/30"

// AI Message
className="max-w-[80%] mr-auto px-4 py-3 rounded-2xl rounded-tl-sm
           backdrop-blur-2xl bg-white/5 border border-white/10 text-white
           shadow-lg"
```

### Animation Guidelines

**Transition Durations**:
```
- Instant: 100ms (hover states)
- Fast: 200ms (button clicks, input focus)
- Normal: 300ms (card hover, modal open)
- Slow: 500ms (page transitions)
```

**Easing Functions**:
```
- ease-out: Default for most transitions
- ease-in-out: Modal animations, page transitions
- spring: Framer Motion for micro-interactions
```

**Framer Motion Variants**:
```tsx
// Fade In
const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 }
}

// Scale In
const scaleIn = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
  transition: { duration: 0.2 }
}

// Slide In
const slideIn = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3 }
}
```

### Responsive Breakpoints

**Strategy**: Mobile-first with progressive enhancement

**Breakpoints**:
```
- Mobile: 320px - 639px (default, no prefix)
- Tablet: 640px - 1023px (sm:)
- Desktop: 1024px - 1279px (lg:)
- Large Desktop: 1280px - 1535px (xl:)
- Ultra-wide: 1536px+ (2xl:)
```

**Responsive Patterns**:
```tsx
// Responsive Grid
className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"

// Responsive Padding
className="px-4 sm:px-6 lg:px-8 xl:px-12"

// Responsive Text
className="text-sm sm:text-base lg:text-lg"

// Responsive Flex Direction
className="flex flex-col lg:flex-row gap-4"
```

### Accessibility Standards

**Keyboard Navigation**:
- All interactive elements must be keyboard accessible
- Visible focus states with ring-2 ring-indigo-500
- Tab order follows visual hierarchy
- Escape key closes modals and dropdowns

**ARIA Labels**:
```tsx
// Button with icon only
<button aria-label="Send message">
  <SendIcon />
</button>

// Form input
<input aria-label="Email address" aria-required="true" />

// Loading state
<div role="status" aria-live="polite">Loading...</div>
```

**Color Contrast**:
- Text on background: Minimum 4.5:1 ratio
- Large text (18px+): Minimum 3:1 ratio
- Interactive elements: Minimum 3:1 ratio

### Mobile Optimization

**Touch Targets**:
- Minimum size: 44x44px (iOS) / 48x48px (Android)
- Spacing between targets: Minimum 8px

**Gestures**:
- Swipe left on message: Delete (with confirmation)
- Pull down on chat: Refresh conversation
- Swipe right on sidebar: Open/close navigation

**Performance**:
- Lazy load images with next/image
- Code split routes with dynamic imports
- Optimize animations for 60fps on mobile
- Use CSS transforms (GPU-accelerated) over position changes

### Loading States

**Skeleton Screens**:
```tsx
// Card Skeleton
<div className="animate-pulse">
  <div className="h-4 bg-white/10 rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-white/10 rounded w-1/2"></div>
</div>
```

**Spinners**:
```tsx
// Gradient Spinner
<div className="animate-spin rounded-full h-8 w-8 border-2 border-white/20
                border-t-indigo-500"></div>
```

**Progress Indicators**:
```tsx
// Linear Progress
<div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
  <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-600
                  animate-progress"></div>
</div>
```

### Error States

**Inline Errors**:
```tsx
// Form Field Error
<div className="mt-1 text-sm text-red-400 flex items-center gap-1">
  <AlertIcon className="w-4 h-4" />
  <span>This field is required</span>
</div>
```

**Toast Notifications**:
```tsx
// Error Toast
<div className="px-4 py-3 rounded-xl backdrop-blur-2xl bg-red-500/10
                border border-red-500/20 text-red-400 shadow-lg
                animate-slide-in-right">
  <div className="flex items-center gap-2">
    <AlertIcon className="w-5 h-5" />
    <span>Failed to send message</span>
  </div>
</div>
```

### Empty States

**Pattern**:
```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <div className="w-16 h-16 rounded-full bg-white/5 flex items-center
                  justify-center mb-4">
    <Icon className="w-8 h-8 text-zinc-500" />
  </div>
  <h3 className="text-lg font-semibold text-white mb-2">No tasks yet</h3>
  <p className="text-sm text-zinc-400 mb-4">
    Start by creating your first task via chat
  </p>
  <button className="px-4 py-2 rounded-lg bg-gradient-to-r
                     from-indigo-500 to-purple-600 text-white">
    Go to Chat
  </button>
</div>
```

## Phase 2: Task Generation

**Status**: NOT STARTED (use `/sp.tasks` command after Phase 1 complete)

**Note**: Task generation is handled by `/sp.tasks` command, not `/sp.plan`. This plan provides the foundation for task generation.

**Expected Task Categories**:
1. **Setup & Configuration** (Better Auth, OpenAI ChatKit, Tailwind config, fonts, Framer Motion)
2. **Design System Implementation** (colors, typography, glassmorphism components, animations)
3. **Landing Page** (hero with animations, features section, gradient CTAs, responsive design)
4. **Authentication** (signup/signin forms with validation, Better Auth integration, JWT handling)
5. **Dashboard Layout** (premium sidebar, animated header, navigation, mobile hamburger menu)
6. **Chatbot Page** (ChatKit integration, glassmorphism message bubbles, typing indicator, API integration to `POST /api/{user_id}/chat`)
7. **Analytics Page** (animated charts, stats cards, empty states, responsive design)
8. **Settings Page** (profile section, preferences toggles, security, account deletion with confirmation)
9. **Additional Pages** (task history timeline with animations, help/documentation with search)
10. **Premium UI Polish** (page transitions, micro-interactions, loading states, error toasts)
11. **Responsive Design** (mobile optimization, touch gestures, fluid layouts, breakpoint testing)
12. **Accessibility** (ARIA labels, keyboard navigation, focus states, screen reader testing)
13. **Testing** (component tests, E2E tests, responsive tests, accessibility audits)
14. **Performance Optimization** (code splitting, lazy loading, image optimization, Lighthouse audit)
15. **Deployment** (environment setup, build optimization, OpenAI domain allowlist configuration)

## Next Steps

1. **Execute Phase 0 research** (generate `research.md`)
   - Better Auth integration with Next.js 15 App Router
   - OpenAI ChatKit setup and domain allowlist configuration (**hackathon requirement**)
   - Backend API integration (`POST /api/{user_id}/chat` - **hackathon requirement**)
   - Premium UI design system (glassmorphism, gradients, animations)
   - Framer Motion animation patterns
   - Recharts vs Chart.js comparison
   - Responsive design strategy (mobile-first, 100% responsive)
   - Document all technology decisions and implementation patterns

2. **Execute Phase 1 design** (generate design artifacts)
   - `data-model.md`: Frontend data structures (User, Session, Message, Conversation, Task, AnalyticsData)
   - `contracts/chat-api.yaml`: Backend chat endpoint OpenAPI spec (`POST /api/{user_id}/chat`)
   - `contracts/analytics-api.yaml`: Backend analytics endpoint spec (if separate)
   - `contracts/auth-flow.md`: Better Auth authentication flow diagram
   - `contracts/error-handling.md`: Error response formats and handling strategy
   - `quickstart.md`: Developer setup guide with environment variables
   - `design-system.md`: Comprehensive design system (colors, typography, components, animations)
   - `responsive-design.md`: 100% responsive design specifications

3. **Update agent context** with new technologies
   - Better Auth configuration patterns
   - OpenAI ChatKit integration examples
   - Framer Motion animation variants
   - Premium UI component library (glassmorphism cards, gradient buttons)
   - Responsive design patterns (mobile navigation, fluid layouts)

4. **Run `/sp.tasks`** to generate implementation tasks
   - Tasks will be organized by priority and dependencies
   - Each task will reference specific FRs from spec.md
   - Tasks will include acceptance criteria and testing requirements
   - Premium UI requirements will be embedded in each task

5. **Begin implementation** following spec-driven workflow
   - **Phase 1**: Setup & Configuration (Better Auth, OpenAI ChatKit, Tailwind, Framer Motion)
   - **Phase 2**: Design System (colors, typography, glassmorphism components, animations)
   - **Phase 3**: Landing Page (premium hero, animated features, gradient CTAs)
   - **Phase 4**: Authentication (signup/signin with Better Auth, JWT handling)
   - **Phase 5**: Dashboard Layout (premium sidebar, animated header, mobile menu)
   - **Phase 6**: Chatbot Page (ChatKit integration, glassmorphism bubbles, API to `POST /api/{user_id}/chat`)
   - **Phase 7**: Analytics Page (animated charts, stats cards, responsive design)
   - **Phase 8**: Settings Page (profile, preferences, security, account deletion)
   - **Phase 9**: Additional Pages (task history timeline, help/documentation)
   - **Phase 10**: Premium UI Polish (animations, micro-interactions, loading states)
   - **Phase 11**: Responsive Optimization (mobile testing, touch gestures, fluid layouts)
   - **Phase 12**: Testing & QA (component tests, E2E tests, accessibility audits)
   - **Phase 13**: Deployment (build optimization, domain configuration, production deployment)

## Hackathon Requirements Checklist

**Technology Stack** ✅:
- [x] Frontend: OpenAI ChatKit
- [x] Backend: Python FastAPI (already implemented)
- [x] AI Framework: OpenAI Agents SDK (backend)
- [x] MCP Server: Official MCP SDK (backend)
- [x] ORM: SQLModel (backend)
- [x] Database: Neon Serverless PostgreSQL
- [x] Authentication: Better Auth

**API Endpoint** ✅:
- [x] `POST /api/{user_id}/chat` (exact endpoint from hackathon requirements)

**MCP Tools** ✅ (backend implements):
- [x] add_task
- [x] list_tasks
- [x] complete_task
- [x] delete_task
- [x] update_task

**Frontend Requirements** ✅:
- [x] Conversational interface with OpenAI ChatKit
- [x] Natural language task management
- [x] Stateless chat endpoint (backend handles state)
- [x] Premium UI design (glassmorphism, animations, gradients)
- [x] 100% responsive (320px to 2560px+)
- [x] Better Auth authentication with JWT
- [x] Landing page, signup/signin, dashboard
- [x] Analytics dashboard with charts
- [x] Settings page

**Deliverables** ✅:
- [x] `/frontend` – ChatKit-based UI with premium design
- [x] `/backend` – FastAPI + Agents SDK + MCP (already implemented)
- [x] `/specs` – Specification files (spec.md, plan.md, research.md, data-model.md, contracts/)
- [x] Database migration scripts (Better Auth tables)
- [x] README with setup instructions

## Dependencies

**External Dependencies**:
- Backend API (001-chatbot-backend) must be deployed and accessible
- **Better Auth library** for TypeScript/Next.js
- **Neon PostgreSQL database** for Better Auth tables and backend data
- OpenAI ChatKit library availability
- OpenAI domain allowlist configured for deployed frontend URL
- Recharts or Chart.js library for analytics charts
- Lucide React or Heroicons for icons

**Internal Dependencies**:
- Phase 0 research must complete before Phase 1 design
- Phase 1 design must complete before task generation
- All constitution gates must pass before implementation
- **Better Auth must be configured** with database connection
- **Better Auth JWKS endpoint** must be accessible to backend for JWT verification

**Database Dependencies**:
- Neon PostgreSQL database for Phase 3
- Better Auth tables (user, session, account, verification) created automatically
- Task table exists (from Phase 3 backend)
- Conversation and Message tables exist (from Phase 3 backend)
- Database shared between Phase 3 frontend (Better Auth) and Phase 3 backend (tasks, conversations)

**Deployment Dependencies**:
- **Phase 3 deployed independently** (not on same domain as Phase 2)
- Better Auth configured with production URL and secrets
- CORS configured on Phase 3 backend to allow Phase 3 frontend origin
- Environment variables configured (DATABASE_URL, BETTER_AUTH_SECRET, BACKEND_API_URL)

## Risk Assessment

**High Risk**:
- **Better Auth integration complexity** - First-time setup with Next.js 15 App Router (mitigation: thorough Phase 0 research, follow official Better Auth docs, test authentication flow early)
- **Better Auth database setup** - Creating tables and managing migrations (mitigation: use Better Auth CLI, test locally first, backup database before production)
- **JWT token management** - Ensuring secure token generation and storage (mitigation: use httpOnly cookies, follow Better Auth security best practices)
- OpenAI ChatKit integration complexity (mitigation: thorough Phase 0 research, fallback to custom chat UI)
- Backend API availability during development (mitigation: mock API for local development)

**Medium Risk**:
- **Analytics implementation** - Fetching and visualizing task data (mitigation: research charting libraries early, design simple charts first)
- **Landing page design quality** - Creating premium landing page (mitigation: use design references, iterate based on feedback)
- Performance with 100+ messages in chat (mitigation: virtualized scrolling, pagination)
- Mobile responsiveness of chat interface (mitigation: mobile-first design, extensive testing)
- **JWT expiration handling** - User session expires while using app (mitigation: detect 401 errors, redirect to signin with message, preserve unsaved work)
- **CORS issues** between Phase 3 frontend and backend (mitigation: configure CORS properly on backend, test cross-origin requests)
- **Dashboard navigation complexity** - Managing multiple pages and state (mitigation: use Next.js App Router patterns, clear navigation structure)

**Low Risk**:
- Dark theme implementation (mitigation: Tailwind dark mode utilities)
- Settings page implementation (mitigation: standard form patterns)
- Additional pages implementation (mitigation: reuse existing components and patterns)
