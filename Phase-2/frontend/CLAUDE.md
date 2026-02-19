# CLAUDE.md — Frontend Agent Guide

## 1. Local Context
This is a **Next.js 15+** application utilizing the **App Router**. It serves as the client-side interface for the Phase-II Todo App. The frontend focuses on high performance, accessibility, and a seamless "App-like" user experience.

## 2. Technical Stack
- **Framework:** Next.js 15 (App Router, Server & Client Components).
- **Styling:** Tailwind CSS + Shadcn/UI primitives.
- **Auth:** Better Auth Client SDK (JWT handling).
- **Icons:** Lucide-React.
- **State & Fetching:** React Hooks + SWR/React Query for client-side caching.

## 3. Core Architectural Rules
1. **Component Separation:**
   - `components/ui`: Atomic Shadcn components (Button, Input, etc.).
   - `components/features`: Feature-specific logic (TaskCard, TaskList).
2. **Data Fetching:**
   - Use **Server Components** for initial page loads (SEO/Speed).
   - Use **Client Components** for real-time CRUD interactions and state updates.
3. **Form Handling:** Use `react-hook-form` with `zod` for schema validation.

## 4. Operational Commands (npm/pnpm)
- **Install Deps:** `npm install`
- **Dev Server:** `npm run dev` (Runs on http://localhost:3000)
- **Production Build:** `npm run build`
- **Linting:** `npm run lint`

## 5. Coding Standards & UI Patterns
- **Optimistic UI:** When a task is updated or deleted, update the local UI immediately before the API response returns. Roll back on error.
- **TypeScript Strictness:** No `any` types. Define interfaces for all API responses in `src/types`.
- **Naming Convention:** PascalCase for components, camelCase for functions and variables.
- **Error UI:** Use **Toast notifications** (via Sonner) for all background API failures.



## 6. Security Protocol
- **Route Protection:** Use `middleware.ts` to redirect unauthenticated users from `/dashboard` to `/login`.
- **Token Management:** Ensure the `Authorization: Bearer <token>` header is sent with every backend request.
- **Safe Rendering:** Handle loading states and skeletons to prevent Layout Shift (CLS).

## 7. Global References
Refer to these files in the root `/specs` folder before coding:
- **UI System:** `specs/ui/components.md`
- **Pages & Routes:** `specs/ui/pages.md`
- **API Contract:** `specs/api/rest-endpoints.md`
- **Auth Flow:** `specs/features/authentication.md`