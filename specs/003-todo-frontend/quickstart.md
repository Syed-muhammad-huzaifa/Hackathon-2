# Quickstart Guide: Todo Frontend Application

**Feature**: 003-todo-frontend | **Date**: 2026-02-16
**Purpose**: Setup instructions for local development

## Prerequisites

- **Node.js**: 18.x or higher
- **npm**: 9.x or higher (or yarn/pnpm)
- **Backend API**: Phase-2 backend running on `http://localhost:8000`
- **Better Auth**: Configured on backend with JWT plugin enabled
- **Git**: For version control

## Initial Setup

### 1. Create Next.js Project

```bash
# Navigate to Phase-2 directory
cd Phase-2

# Create Next.js 15 app with TypeScript and Tailwind
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# Navigate to frontend directory
cd frontend
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install better-auth zod react-hook-form @hookform/resolvers/zod

# UI components (shadcn/ui)
npx shadcn-ui@latest init

# Charts
npm install recharts

# Animations
npm install framer-motion

# Icons
npm install lucide-react

# Dev dependencies
npm install -D @types/node @types/react @types/react-dom
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
npm install -D eslint-config-next
```

### 3. Configure Environment Variables

Create `.env.local` file:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth URL (same as backend)
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

Create `.env.example` file (for documentation):

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth URL
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### 4. Configure TypeScript

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 5. Configure ESLint

Update `.eslintrc.json`:

```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 6. Configure Tailwind CSS

Update `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.95)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### 7. Configure Dark Theme with CSS Variables

Update `app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Dark theme colors */
    --background: 10 10 10; /* #0a0a0a */
    --foreground: 250 250 250; /* #fafafa */

    --card: 17 17 17; /* #111111 */
    --card-foreground: 250 250 250;

    --primary: 139 92 246; /* #8B5CF6 purple */
    --primary-foreground: 255 255 255;

    --secondary: 59 130 246; /* #3B82F6 blue */
    --secondary-foreground: 255 255 255;

    --muted: 38 38 38; /* #262626 */
    --muted-foreground: 163 163 163; /* #a3a3a3 */

    --accent: 6 182 212; /* #06B6D4 cyan */
    --accent-foreground: 255 255 255;

    --destructive: 239 68 68; /* #EF4444 red */
    --destructive-foreground: 255 255 255;

    --border: 38 38 38; /* #262626 */
    --input: 38 38 38;
    --ring: 139 92 246; /* #8B5CF6 */

    --radius: 0.75rem; /* 12px */
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground font-sans antialiased;
  }

  /* Glassmorphism utility */
  .glass {
    @apply bg-white/5 backdrop-blur-xl border border-white/10;
  }

  /* Gradient text utility */
  .gradient-text {
    @apply bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent;
  }
}
```

### 8. Configure Premium Fonts

Update `app/layout.tsx`:

```typescript
import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Todo App - Premium Task Management",
  description: "A modern, premium todo application with dark theme",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark`}>
      <body>{children}</body>
    </html>
  );
}
```

### 9. Install shadcn/ui Components

```bash
# Install base components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add form
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add badge
```

### 10. Copy Contract Files

```bash
# Create lib directory structure
mkdir -p lib/schemas

# Copy contract files from specs
cp ../specs/003-todo-frontend/contracts/auth.schema.ts lib/schemas/auth.ts
cp ../specs/003-todo-frontend/contracts/task.schema.ts lib/schemas/task.ts
cp ../specs/003-todo-frontend/contracts/api-client.ts lib/api/client.ts
```

### 11. Configure Better Auth

Create `lib/auth/client.ts`:

```typescript
import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
})
```

### 12. Create Middleware for Route Protection

Create `middleware.ts` in root:

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check for auth cookie (set by Better Auth)
  const authCookie = request.cookies.get('better-auth.session_token')

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!authCookie) {
      return NextResponse.redirect(new URL('/sign-in', request.url))
    }
  }

  // Redirect authenticated users away from auth pages
  if (request.nextUrl.pathname.startsWith('/sign-in') ||
      request.nextUrl.pathname.startsWith('/sign-up')) {
    if (authCookie) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/sign-in', '/sign-up'],
}
```

## Development Workflow

### Start Development Server

```bash
npm run dev
```

Application will be available at `http://localhost:3000`

### Run Tests

```bash
# Component tests
npm run test

# E2E tests
npm run test:e2e

# Type checking
npm run type-check
```

### Build for Production

```bash
npm run build
npm run start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth route group
│   │   ├── sign-up/
│   │   └── sign-in/
│   ├── (dashboard)/       # Protected route group
│   │   └── dashboard/
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── auth/             # Auth forms
│   ├── tasks/            # Task components
│   ├── analytics/        # Chart components
│   └── layout/           # Layout components
├── lib/                  # Utilities
│   ├── api/             # API client
│   ├── auth/            # Better Auth setup
│   ├── schemas/         # Zod schemas
│   └── utils.ts
├── types/               # TypeScript types
├── public/              # Static assets
├── tests/               # Test files
├── middleware.ts        # Route protection
├── .env.local          # Environment variables
└── package.json
```

## Verification Checklist

After setup, verify:

- [ ] `npm run dev` starts without errors
- [ ] Navigate to `http://localhost:3000` shows landing page
- [ ] TypeScript compilation succeeds (`npm run type-check`)
- [ ] ESLint passes (`npm run lint`)
- [ ] Backend API is accessible at `http://localhost:8000/health`
- [ ] Better Auth is configured on backend
- [ ] Environment variables are set in `.env.local`

## Common Issues

### Issue: "Module not found" errors

**Solution**: Run `npm install` to ensure all dependencies are installed

### Issue: Backend API not accessible

**Solution**:
1. Start the backend server: `cd Phase-2/backend && .venv/bin/uvicorn app.main:app --reload --port 8000`
2. Verify backend is running: `curl http://localhost:8000/health`

### Issue: Better Auth errors

**Solution**: Ensure backend has Better Auth configured with JWT plugin enabled

### Issue: TypeScript errors in contract files

**Solution**: Run `npm install zod` to ensure Zod is installed

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement features in priority order (P1 → P2 → P3)
3. Write tests for each component
4. Run E2E tests to verify user flows

## Additional Resources

- [Next.js 15 Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://better-auth.com)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org)
