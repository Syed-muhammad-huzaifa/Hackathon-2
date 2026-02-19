# UI & Components Specification - Phase II

## 1. Overview
The frontend is built using **Next.js 15 (App Router)** and **TypeScript**. We follow a "Component-Based Architecture" where the UI is broken down into small, reusable, and testable pieces. All components are styled using **Tailwind CSS** and primitive components from **Shadcn/UI**.

## 2. Design System
- **Framework:** Next.js 15
- **Styling:** Tailwind CSS
- **Component Library:** Shadcn/UI (Radix UI primitives)
- **Icons:** Lucide-React
- **State Management:** React Context (for Auth) + SWR/React Query (for Data Fetching)

## 3. Core Component Library

### 3.1 Shared Layout Components
- **Navbar:** Displays the application logo, "Add Task" quick-action, and the User Profile/Logout dropdown.
- **Footer:** Simple persistent bar with versioning and project links.
- **ProtectedRoute:** A wrapper component that checks the **Better Auth** session and redirects unauthenticated users to `/login`.

### 3.2 Task-Specific Components
- **TaskCard:** Individual display for a task.
    - Props: `title`, `description`, `is_completed`, `onToggle`, `onDelete`.
    - Features: Strike-through text when completed; "Edit" and "Delete" icon buttons.
- **TaskList:** The container that maps through the tasks array. 
    - Handles **Empty States** ("No tasks found") and **Loading States** (Skeleton cards).
- **TaskForm:** A modal or inline form to create/edit tasks.
    - Fields: `Title` (Input), `Description` (Textarea).
    - Validation: Title cannot be empty.

## 4. Page Structure
| Page | Route | Description |
| :--- | :--- | :--- |
| **Landing** | `/` | Introduction to the app with "Get Started" buttons. |
| **Login** | `/login` | Email/Password form powered by Better Auth. |
| **Signup** | `/signup` | New user registration form. |
| **Dashboard** | `/dashboard` | The main "Task View" containing the TaskList and TaskForm. |

## 5. Interaction Patterns (Optimistic UI)
To provide an industry-level user experience, we implement **Optimistic Updates**:
1. User clicks the "Complete" checkbox.
2. The UI immediately reflects the change (checked state + strike-through).
3. The **Frontend Service** sends a `PATCH` request to the backend.
4. If the request fails, the UI rolls back to the previous state and shows a **Toast** error message.

## 6. Implementation Instructions for Agent

### 6.1 State Management
- Use `useActionState` or `useFormStatus` (Next.js 15 features) for handling form submissions.
- Implement a `useTasks` custom hook to encapsulate fetching logic and revalidation.

### 6.2 Styling Rules
- Use `cn()` utility for conditional class merging.
- Maintain **Dark Mode** support by using Tailwind `dark:` variants.
- Ensure all interactive elements have `:hover` and `:focus-visible` states for accessibility.