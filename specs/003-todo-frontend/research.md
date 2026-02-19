# Research: Todo Frontend Application

**Feature**: 003-todo-frontend | **Date**: 2026-02-16
**Purpose**: Document technology decisions, patterns, and best practices for implementation

## Research Questions

### 1. Better Auth Integration with Next.js 15 App Router

**Question**: How should Better Auth be integrated with Next.js 15 App Router for optimal security and UX?

**Research Findings**:
- Better Auth provides a TypeScript-first authentication library with built-in Next.js support
- Next.js 15 App Router uses Server Components by default, which can directly access cookies
- Better Auth JWT plugin generates tokens that can be stored in httpOnly cookies
- Middleware can protect routes at the edge before rendering

**Decision**: Use Better Auth with Next.js middleware for route protection

**Rationale**:
- Middleware runs at the edge before page rendering, providing fast auth checks
- httpOnly cookies prevent XSS attacks (tokens not accessible via JavaScript)
- Server Components can read cookies directly without client-side JavaScript
- Better Auth's Next.js adapter provides seamless integration

**Implementation Pattern**:
```typescript
// middleware.ts
import { betterAuth } from "better-auth/client"
export async function middleware(request: NextRequest) {
  const session = await betterAuth.getSession(request)
  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/sign-in', request.url))
  }
}
```

**Alternatives Considered**:
- Client-side auth checks: Rejected due to flash of unauthenticated content and security concerns
- localStorage for tokens: Rejected due to XSS vulnerability

---

### 2. API Client Architecture

**Question**: Should we use native fetch, a library like axios, or build a custom typed client?

**Research Findings**:
- Next.js 15 extends native fetch with caching and revalidation
- TypeScript can provide full type safety with Zod schemas
- Custom client allows automatic token injection and error handling
- Modern fetch supports all needed features (headers, JSON, error handling)

**Decision**: Build a custom typed API client using native fetch + Zod

**Rationale**:
- Native fetch is built into Next.js with enhanced features (no extra dependency)
- Zod schemas provide runtime validation + TypeScript types
- Custom client centralizes auth token injection and error handling
- Leverages Next.js fetch caching for performance

**Implementation Pattern**:
```typescript
// lib/api/client.ts
import { z } from "zod"

export async function apiClient<T>(
  endpoint: string,
  schema: z.ZodSchema<T>,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include', // Send cookies
  })

  if (!response.ok) {
    throw new APIError(response.status, await response.json())
  }

  const data = await response.json()
  return schema.parse(data) // Runtime validation
}
```

**Alternatives Considered**:
- axios: Rejected due to unnecessary dependency and lack of Next.js fetch integration
- SWR/React Query: Considered for data fetching but deferred to implementation phase (can layer on top)

---

### 3. Chart Library Selection

**Question**: Should we use Recharts or Chart.js for analytics visualizations?

**Research Findings**:
- **Recharts**: React-native, composable API, built with React components, TypeScript support
- **Chart.js**: Canvas-based, imperative API, requires react-chartjs-2 wrapper, larger ecosystem
- Performance: Both handle <1000 data points well (our use case: max ~100 tasks)
- Bundle size: Recharts ~100KB, Chart.js ~200KB (with wrapper)

**Decision**: Use Recharts

**Rationale**:
- Native React components fit Next.js component model better
- Declarative API is more intuitive for React developers
- Smaller bundle size (important for performance goals)
- Built-in TypeScript support without wrappers
- Composable API allows easy customization

**Implementation Pattern**:
```typescript
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

export function StatusChart({ tasks }: { tasks: Task[] }) {
  const data = [
    { name: 'Pending', value: tasks.filter(t => t.status === 'pending').length },
    { name: 'In Progress', value: tasks.filter(t => t.status === 'in-progress').length },
    { name: 'Completed', value: tasks.filter(t => t.status === 'completed').length },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" />
      </PieChart>
    </ResponsiveContainer>
  )
}
```

**Alternatives Considered**:
- Chart.js: Rejected due to larger bundle size and imperative API
- Victory: Rejected due to less active maintenance and larger bundle

---

### 4. State Management Approach

**Question**: Do we need a state management library (Redux, Zustand) or can we use React Server Components + hooks?

**Research Findings**:
- Next.js 15 App Router defaults to Server Components (no client-side state)
- Server Components can fetch data directly and pass to Client Components
- Client Components can use React hooks (useState, useReducer) for local state
- Most data is fetched per-route, not shared globally
- Task list updates can use optimistic UI with React hooks

**Decision**: Use Server Components for data fetching + React hooks for client state (no global state library)

**Rationale**:
- Server Components eliminate need for client-side data fetching in most cases
- Task CRUD operations are scoped to single routes (no cross-route state sharing)
- React hooks sufficient for form state and optimistic updates
- Simpler architecture without additional dependencies
- Can add SWR later if caching/revalidation needs arise

**Implementation Pattern**:
```typescript
// app/dashboard/page.tsx (Server Component)
export default async function DashboardPage() {
  const tasks = await fetchTasks() // Server-side fetch
  return <TaskList initialTasks={tasks} /> // Pass to Client Component
}

// components/tasks/task-list.tsx (Client Component)
'use client'
export function TaskList({ initialTasks }: { initialTasks: Task[] }) {
  const [tasks, setTasks] = useState(initialTasks)
  // Optimistic updates with local state
}
```

**Alternatives Considered**:
- Redux: Rejected due to unnecessary complexity for this use case
- Zustand: Rejected due to lack of cross-route state sharing needs
- SWR/React Query: Deferred - can add later if caching needs emerge

---

### 5. Testing Strategy for Next.js 15 App Router

**Question**: What testing tools and patterns work best with Next.js 15 App Router?

**Research Findings**:
- **Vitest**: Fast, Vite-based, better TypeScript support than Jest
- **React Testing Library**: Standard for component testing, works with Server Components
- **Playwright**: Official recommendation for E2E testing Next.js apps
- Server Components require special testing considerations (async rendering)

**Decision**: Vitest + React Testing Library for components, Playwright for E2E

**Rationale**:
- Vitest is faster and has better ESM support than Jest
- React Testing Library enforces testing user behavior (not implementation)
- Playwright provides cross-browser E2E testing with excellent Next.js support
- Three-tier testing: Unit (business logic) → Component (UI) → E2E (user flows)

**Implementation Pattern**:
```typescript
// tests/components/task-card.test.tsx
import { render, screen } from '@testing-library/react'
import { TaskCard } from '@/components/tasks/task-card'

test('displays task title and status', () => {
  render(<TaskCard task={{ title: 'Test', status: 'pending' }} />)
  expect(screen.getByText('Test')).toBeInTheDocument()
  expect(screen.getByText('pending')).toBeInTheDocument()
})

// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('user can sign up and access dashboard', async ({ page }) => {
  await page.goto('/sign-up')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')
})
```

**Alternatives Considered**:
- Jest: Rejected due to slower performance and ESM issues
- Cypress: Rejected in favor of Playwright (better Next.js integration, faster)

---

### 6. Form Validation Strategy

**Question**: Should we use a form library (React Hook Form, Formik) or native HTML + React state?

**Research Findings**:
- React Hook Form: Uncontrolled inputs, minimal re-renders, built-in validation
- Formik: Controlled inputs, more re-renders, larger bundle
- Native HTML validation: Simple but limited error messaging
- Zod integration: React Hook Form has official Zod resolver

**Decision**: Use React Hook Form + Zod for form validation

**Rationale**:
- Minimal re-renders improve performance (important for mobile)
- Built-in validation with Zod schemas (reuse API schemas)
- Excellent TypeScript support
- Small bundle size (~9KB)
- Handles complex validation rules from spec (email format, password length)

**Implementation Pattern**:
```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { signUpSchema } from '@/lib/schemas/auth'

export function SignUpForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(signUpSchema)
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
    </form>
  )
}
```

**Alternatives Considered**:
- Formik: Rejected due to larger bundle and more re-renders
- Native validation: Rejected due to limited error messaging and UX

---

### 7. Premium Typography Selection

**Question**: Which premium font family should we use for a modern, professional look?

**Research Findings**:
- **Inter**: Variable font, excellent readability, widely used in modern apps, 400KB
- **Geist**: Vercel's font, optimized for Next.js, modern aesthetic, 350KB
- **SF Pro**: Apple's system font, premium feel, licensing restrictions
- **Manrope**: Geometric sans-serif, unique character, 300KB
- Next.js font optimization: Automatic subsetting, preloading, zero layout shift

**Decision**: Use Inter as primary font with JetBrains Mono for monospace

**Rationale**:
- Inter is battle-tested in production apps (GitHub, Stripe, Linear)
- Variable font allows flexible weight adjustments (300-700)
- Excellent readability at all sizes (mobile to desktop)
- Next.js font optimization eliminates FOUT/FOIT
- JetBrains Mono provides professional monospace for code/data
- Combined bundle size optimized through subsetting

**Implementation Pattern**:
```typescript
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
})

export default function RootLayout({ children }) {
  return (
    <html className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  )
}
```

**Alternatives Considered**:
- Geist: Rejected due to less widespread adoption (newer font)
- SF Pro: Rejected due to licensing complexity
- System fonts: Rejected due to lack of premium feel

---

### 8. Animation Library Selection

**Question**: Should we use Framer Motion, React Spring, or CSS animations for smooth interactions?

**Research Findings**:
- **Framer Motion**: Declarative API, gesture support, layout animations, 60KB
- **React Spring**: Physics-based animations, complex API, 40KB
- **CSS Animations**: Lightweight, limited control, no gesture support
- **GSAP**: Powerful but large bundle (100KB+), imperative API

**Decision**: Use Framer Motion for complex animations + Tailwind for simple transitions

**Rationale**:
- Framer Motion's declarative API fits React component model
- Built-in gesture support (drag, hover, tap) for micro-interactions
- Layout animations handle position changes smoothly
- Variants system enables coordinated animations
- Tailwind handles simple hover/focus transitions (no extra JS)
- 60KB bundle acceptable for premium UX

**Implementation Pattern**:
```typescript
import { motion } from 'framer-motion'

export function TaskCard({ task }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="card"
    >
      {task.title}
    </motion.div>
  )
}
```

**Alternatives Considered**:
- React Spring: Rejected due to steeper learning curve and physics-based approach not needed
- CSS only: Rejected due to lack of gesture support and complex orchestration
- GSAP: Rejected due to large bundle size and imperative API

---

### 9. Icon Library Selection

**Question**: Which icon library provides the best balance of quality, consistency, and bundle size?

**Research Findings**:
- **Lucide Icons**: Modern, consistent, tree-shakeable, React components, 2KB per icon
- **Heroicons**: Tailwind Labs official, two styles (outline/solid), React components, 2KB per icon
- **React Icons**: Aggregates multiple sets, inconsistent styles, larger bundle
- **Custom SVGs**: Maximum control, requires design resources

**Decision**: Use Lucide Icons

**Rationale**:
- Modern, clean design that matches premium aesthetic
- Fully tree-shakeable (only import icons you use)
- React components with TypeScript support
- Consistent stroke width and sizing
- Active maintenance and growing library
- Smaller bundle than React Icons (only pay for what you use)

**Implementation Pattern**:
```typescript
import { Check, X, Plus, Trash2, Edit } from 'lucide-react'

export function TaskActions() {
  return (
    <div className="flex gap-2">
      <button><Check className="w-5 h-5" /></button>
      <button><Edit className="w-5 h-5" /></button>
      <button><Trash2 className="w-5 h-5" /></button>
    </div>
  )
}
```

**Alternatives Considered**:
- Heroicons: Rejected due to smaller icon library (Lucide has more options)
- React Icons: Rejected due to bundle size concerns
- Custom SVGs: Rejected due to time constraints and design resources needed

---

### 10. Dark Theme Implementation Strategy

**Question**: How should we implement the dark theme to ensure consistency and maintainability?

**Research Findings**:
- **Tailwind Dark Mode**: Class-based or media query-based, CSS variables for colors
- **CSS Variables**: Centralized color management, easy theme switching
- **Inline Styles**: Not recommended, hard to maintain
- **shadcn/ui**: Built-in dark mode support with CSS variables

**Decision**: Use Tailwind CSS with CSS variables for dark theme colors

**Rationale**:
- CSS variables enable centralized color management
- Tailwind's dark mode utilities work seamlessly
- shadcn/ui components already support dark mode
- Easy to adjust colors globally without touching components
- Future light mode addition is straightforward (just swap variables)

**Implementation Pattern**:
```css
/* globals.css */
@layer base {
  :root {
    --background: 10 10 10; /* #0a0a0a */
    --foreground: 250 250 250; /* #fafafa */
    --primary: 139 92 246; /* #8B5CF6 purple */
    --primary-foreground: 255 255 255;
    --card: 17 17 17; /* #111111 */
    --card-foreground: 250 250 250;
    /* ... more variables */
  }
}
```

```typescript
// Component usage
<div className="bg-background text-foreground">
  <div className="bg-card rounded-lg p-6">
    <button className="bg-primary text-primary-foreground">
      Click me
    </button>
  </div>
</div>
```

**Alternatives Considered**:
- Media query dark mode: Rejected because we want dark as default (not system preference)
- Inline styles: Rejected due to maintainability issues
- Theme provider library: Rejected due to unnecessary complexity (Tailwind + CSS vars sufficient)

---

## Technology Stack Summary

| Category | Technology | Rationale |
|----------|-----------|-----------|
| Framework | Next.js 15 (App Router) | Server Components, built-in optimizations, TypeScript support |
| Language | TypeScript (strict mode) | Type safety, better DX, catches errors at compile time |
| Styling | Tailwind CSS | Utility-first, mobile-first, small bundle, fast development |
| UI Components | shadcn/ui | Accessible, customizable, copy-paste (no dependency), Tailwind-based, dark mode support |
| Authentication | Better Auth (JWT plugin) | TypeScript-first, Next.js integration, httpOnly cookies |
| API Client | Native fetch + Zod | No extra dependency, type-safe, runtime validation |
| Charts | Recharts | React-native, smaller bundle, declarative API |
| Forms | React Hook Form + Zod | Performance, type-safe, minimal re-renders |
| State | Server Components + React hooks | Simple, no global state needed, leverages Next.js strengths |
| Testing (Component) | Vitest + React Testing Library | Fast, ESM support, user-centric testing |
| Testing (E2E) | Playwright | Cross-browser, Next.js integration, reliable |
| Validation | Zod | Runtime + compile-time types, composable schemas |
| Typography | Inter + JetBrains Mono | Premium fonts, variable weights, Next.js optimization |
| Animations | Framer Motion + Tailwind | Declarative API, gesture support, smooth 60fps animations |
| Icons | Lucide Icons | Modern, tree-shakeable, consistent design, React components |
| Theme | Dark mode (CSS variables) | Centralized color management, Tailwind integration |

---

## Best Practices & Patterns

### 1. Server Components First
- Default to Server Components for data fetching
- Use Client Components only for interactivity (forms, buttons, charts)
- Mark Client Components with `'use client'` directive

### 2. Type Safety
- All API responses validated with Zod schemas
- No `any` types (ESLint rule enforced)
- Strict TypeScript configuration

### 3. Error Handling
- API errors caught and displayed with toast notifications
- Form validation errors shown inline
- Network errors trigger retry mechanism

### 4. Performance
- Code splitting with dynamic imports for charts
- Image optimization with Next.js Image component
- Lazy loading for below-the-fold content
- Font optimization with next/font (zero layout shift)
- Animation performance: Use CSS transforms (translate, scale) over position changes

### 5. Accessibility
- Semantic HTML (`<nav>`, `<main>`, `<button>`)
- ARIA labels on interactive elements
- Keyboard navigation (Tab, Enter, Escape)
- Focus indicators visible
- High contrast colors (WCAG AA minimum)

### 6. Security
- httpOnly cookies for JWT storage
- CSRF protection with SameSite cookies
- Input validation on client and server
- HTTPS enforced in production

### 7. Premium UI/UX Patterns
- **Glassmorphism**: Use backdrop-blur with rgba transparency for cards
- **Smooth Animations**: 60fps target, use Framer Motion for complex animations
- **Micro-interactions**: Button ripples, hover effects, loading skeletons
- **Consistent Spacing**: Use Tailwind spacing scale (4px increments)
- **Color Consistency**: Use CSS variables for all colors (easy theme adjustments)
- **Mobile-First**: Design for mobile, enhance for desktop
- **Touch Targets**: Minimum 44x44px on mobile devices
- **Loading States**: Skeleton screens instead of spinners for better perceived performance
- **Empty States**: Friendly messages with illustrations or animations
- **Success Feedback**: Celebrate user actions with animations (confetti, checkmarks)

---

## Open Questions Resolved

All technical decisions have been made. No open questions remain for implementation phase.

---

## Next Steps

1. **Phase 1**: Create data-model.md (frontend state shape, API contracts)
2. **Phase 1**: Generate contracts/ (TypeScript interfaces, Zod schemas)
3. **Phase 1**: Create quickstart.md (setup instructions)
4. **Phase 1**: Update agent context with new technologies
5. **Phase 2**: Generate tasks.md with `/sp.tasks` command
