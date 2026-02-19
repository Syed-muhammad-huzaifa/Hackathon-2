# Pages & Routing Specification - Phase II

## 1. Overview
The frontend utilizes the **Next.js 15 App Router**. Routing is organized to separate public marketing pages from protected application logic. All data-driven pages utilize **Server Components** by default for initial fetches, with **Client Components** nested for interactivity.

## 2. Route Map

| Path | Access | Component Type | Purpose |
| :--- | :--- | :--- | :--- |
| `/` | Public | Server | Landing page & Value proposition. |
| `/login` | Public | Client | User authentication (Better Auth). |
| `/signup` | Public | Client | New user registration. |
| `/dashboard`| Private| Server/Client | The main Todo application interface. |
| `/settings` | Private| Client | User profile and account management. |

## 3. Page Definitions

### 3.1 Landing Page (`/`)
- **Content:** Hero section, feature highlights (Cloud sync, Security, Speed).
- **Actions:** "Get Started" button (redirects to `/signup`) and "Login" link.

### 3.2 Authentication Pages (`/login` & `/signup`)
- **Logic:** Uses the `authClient` from Better Auth.
- **Redirection:** If a user is already authenticated, they are automatically redirected to `/dashboard`.
- **Validation:** Client-side form validation for email format and password strength.

### 3.3 Dashboard Page (`/dashboard`)
This is the core of the application.
- **Layout:** Includes the `Navbar` and a centered `TaskContainer`.
- **Data Fetching:** - Initial task load via a **Server Component** (using `fetch` with the JWT).
    - Real-time updates handled via a **Client Component** (using `SWR` or `React Query`) for a "live" feel.
- **Empty State:** High-visibility "Create your first task" button when the task count is zero.

## 4. Middleware & Protection
- **Global Middleware:** `middleware.ts` intercepts requests to `/dashboard` and `/settings`.
- **Session Check:** If no Better Auth session cookie is found, the user is redirected to `/login` with a `callbackUrl`.

## 5. Data Flow: Page to API

1. **Page Load:** The Page Component requests data from the **Backend Presentation Layer** (`/api/v1/tasks`).
2. **Authorization:** The page includes the `Bearer Token` in the request header.
3. **Hydration:** The Server Component passes initial data to Client Components (like `TaskList`) to prevent layout shifts.

## 6. Implementation Instructions for Agent

### 6.1 Directory Structure
```text
/frontend/src/app
├── (auth)
│   ├── login/page.tsx
│   └── signup/page.tsx
├── (protected)
│   ├── dashboard/page.tsx
│   └── settings/page.tsx
├── layout.tsx
└── page.tsx (Landing)