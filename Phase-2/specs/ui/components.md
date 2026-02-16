# UI Components Specification  
**Hackathon II – Phase II: Full-Stack Web Application**

## 1. Purpose

This document defines the reusable UI components and their responsibilities for the Todo web application in Phase II.  

All components live inside the **Next.js frontend** (`Phase-2/frontend/`) and are built using:
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS (utility-first styling)
- shadcn/ui components (recommended base – buttons, cards, inputs, dialogs, toasts, etc.)
- Lucide React icons (or Heroicons)

**Core Rules**
- Use **Server Components** by default (fetch data, render static parts)
- Use **Client Components** only when interactivity is required ("use client" directive)
- No inline styles → Tailwind classes only
- Responsive by default (mobile-first)
- Dark mode support (via `class` strategy in `tailwind.config.js`)
- Accessibility: semantic HTML, ARIA labels where needed, keyboard navigation
- Error states, loading skeletons, and toast notifications for UX polish
- All task-related components live inside the **protected dashboard**

## 2. Folder Structure Recommendation
frontend/
├── components/
│   ├── common/               # Shared across public & protected
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Textarea.tsx
│   │   ├── Toast.tsx         # or use shadcn toast
│   │   └── Skeleton.tsx
│   ├── public/               # Landing page only
│   │   ├── HeroSection.tsx
│   │   └── CTAButton.tsx
│   ├── auth/
│   │   ├── AuthForm.tsx      # Shared signup/signin form logic
│   │   ├── SignUpForm.tsx
│   │   └── SignInForm.tsx
│   └── dashboard/
│       ├── TaskList.tsx
│       ├── TaskItem.tsx
│       ├── TaskForm.tsx
│       ├── FilterControls.tsx
│       ├── SortControls.tsx
│       ├── SearchBar.tsx
│       ├── AnalyticsCards.tsx
│       ├── CompletionChart.tsx
│       └── EmptyState.tsx
└── CLAUDE.md                 # frontend-specific guidelines

## 3. Component Catalog

### 3.1 Common Components (Reusable Everywhere)

- **Button**  
  Variants: primary, secondary, outline, ghost, destructive, link  
  Sizes: sm, md (default), lg  
  States: loading (with spinner), disabled  
  Usage: Submit buttons, logout, delete confirm, etc.

- **Card**  
  Used for task items, analytics widgets  
  Variants: default, hoverable  
  Children: header, content, footer

- **Input** / **Textarea**  
  With label, error message, placeholder  
  Validation states (error border + message)

- **Toast**  
  Success, error, info, warning variants  
  Auto-dismiss after 5s  
  Used for: "Task created", "Invalid credentials", "Logged out"

- **Skeleton**  
  Loading placeholders for lists, cards, charts

### 3.2 Public / Landing Components

- **HeroSection**  
  - Large heading: "Organize Your Life with Todo"
  - Subheading: brief value proposition
  - Two prominent CTAs: "Sign Up" → /signup, "Sign In" → /signin
  - Responsive hero image or gradient background

- **CTAButton**  
  Large, eye-catching buttons linking to auth pages

### 3.3 Authentication Components

- **AuthForm** (base component)  
  - Handles both signup & signin (variant prop)
  - Fields: email, password, name (signup only)
  - Submit button + loading state
  - Error display below fields
  - Link to switch between signup/signin

- **SignUpForm** / **SignInForm**  
  - Wrap AuthForm with correct variant & redirect logic

### 3.4 Dashboard Components (Core of the App)

- **TaskList**  
  - Renders array of tasks from API
  - Shows TaskItem for each
  - Empty state → <EmptyState />
  - Loading → skeletons
  - Supports drag-and-drop reordering (optional Phase II stretch)

- **TaskItem**  
  - Card-like display
  - Checkbox/toggle for complete (optimistic update)
  - Title (strikethrough if completed)
  - Description (truncated, expand on click)
  - Edit icon → opens edit modal or inline edit
  - Delete icon → confirmation dialog
  - Created/updated relative time (e.g., "2 hours ago")

- **TaskForm** (Add & Edit)  
  - Modal or inline form
  - Fields: title (required), description (textarea)
  - Submit → optimistic add/update → refresh list
  - Cancel button
  - Validation: title required

- **FilterControls**  
  - Dropdown: All / Pending / Completed
  - Updates URL query params or local state → refetch

- **SortControls**  
  - Dropdown or buttons: Newest first, Oldest first, A–Z, Z–A

- **SearchBar**  
  - Debounced input (300–500ms)
  - Clear button
  - Placeholder: "Search tasks..."

- **AnalyticsCards**  
  - Grid of 3–4 cards:
    - Total Tasks
    - Pending Tasks
    - Completed Tasks
    - Completion Rate (%)
  - Each card: big number + label + subtle icon

- **CompletionChart**  
  - Simple pie or bar chart (Recharts / Chart.js)
  - Shows completed vs pending
  - Colors: green for completed, gray/orange for pending
  - Responsive size

- **EmptyState**  
  - Centered message: "No tasks yet. Add your first one!"
  - Big + icon button to open TaskForm

## 4. Design System & Styling Guidelines

- Primary color: indigo/blue (e.g., bg-indigo-600)
- Accent: green for complete/success
- Neutral: gray scale
- Typography: Inter or default system font
- Spacing: Consistent 4px scale (p-4, gap-4, etc.)
- Shadows: subtle (shadow-md on cards)
- Borders: rounded-md, border-border
- Dark mode: auto via `class` strategy

## 5. Accessibility Requirements

- Semantic HTML (button, input, label)
- ARIA labels on icons/buttons without text
- Focus states visible (ring-2 ring-indigo-500)
- Keyboard navigation (tab through forms, list items)
- Screen reader friendly (no hidden content issues)

## 6. Interaction Patterns

- Optimistic updates for create/update/toggle
- Rollback on error + error toast
- Confirmation dialog for delete
- Loading skeletons during fetches
- Toast notifications for all success/error states

## Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/database/schema.md - Database schema and relationships
6. @specs/ui/pages.md - Next.js pages and routing
7. @specs/overview.md - Overview about the project

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

**This file is the authoritative spec for all UI components in Phase II.**  
All component code generation must reference this document.
