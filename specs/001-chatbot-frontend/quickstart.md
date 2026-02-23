# Quickstart Guide: AI Chatbot Frontend

**Feature**: 001-chatbot-frontend
**Last Updated**: 2026-02-21

## Overview

This guide will help you set up and run the AI chatbot frontend locally. The frontend is a Next.js 15 application with OpenAI ChatKit for the chat interface, **Phase 2 Better Auth session integration** (no authentication UI needed), and Recharts for analytics.

**Important**: This frontend assumes users are already authenticated via Phase 2. It reads existing session cookies from Phase 2 Better Auth.

---

## Prerequisites

### Required Software

- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **Package Manager**: npm, yarn, or pnpm
- **Git**: For cloning the repository
- **Code Editor**: VS Code recommended

### Backend Dependency

The frontend requires both the backend API and Phase 2 authentication to be running:
- **Phase 3 Backend** (001-chatbot-backend) should be accessible at `http://localhost:8001` (or configured URL)
- **Phase 2 Better Auth** must be running (shared Neon database)
- **Phase 2 session cookies** must be accessible (same domain recommended)
- Backend must expose the chat endpoint: `POST /api/{user_id}/chat`

**Critical**: Phase 2 and Phase 3 should be on the same domain for session cookie sharing.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Hackathon-2/Phase-3/frontend
```

### 2. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

**Key Dependencies**:
- `next@15` - Next.js framework
- `react@19` - React library
- `@openai/chatkit-react` - OpenAI ChatKit component
- `recharts` - Chart library
- `tailwindcss` - CSS framework
- `zod` - Schema validation
- `lucide-react` - Icon library

**Note**: No Better Auth client libraries needed - Phase 3 reads existing Phase 2 session cookies.

---

## Configuration

### 1. Environment Variables

Create a `.env.local` file in the frontend root directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001

# OpenAI ChatKit (obtain from OpenAI dashboard)
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key-from-openai

# Production (uncomment for deployment)
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Important**:
- No Better Auth environment variables needed - Phase 3 reads existing Phase 2 session cookies
- `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` requires domain registration (see below)
- Ensure Phase 2 and Phase 3 are on the same domain for cookie sharing

### 2. Verify Phase 2 Authentication

Ensure Phase 2 Better Auth is running and accessible:

```bash
# Test Phase 2 authentication (adjust URL to your Phase 2 setup)
curl http://localhost:3000/api/auth/session

# Should return session data if authenticated
```

**Note**: Users must be authenticated in Phase 2 before accessing Phase 3 chatbot.

### 3. OpenAI ChatKit Domain Allowlist Setup

**Required for ChatKit to work**:

1. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. For local development, add: `localhost:3000`
4. For production, add your deployed domain: `yourdomain.com`
5. Copy the `domainKey` provided by OpenAI
6. Add it to `.env.local` as `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`

**Note**: Without domain registration, ChatKit will not function.

### 3. Verify Backend Connection

Ensure the backend is running and accessible:

```bash
# Test backend health endpoint
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy"}
```

---

## Running the Application

### Development Mode

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

The application will start at: **http://localhost:3000**

### Production Build

```bash
# Build the application
npm run build

# Start production server
npm run start
```

### Linting and Type Checking

```bash
# Run ESLint
npm run lint

# Type check with TypeScript
npx tsc --noEmit
```

---

## Project Structure

```
Phase-3/frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router
│   │   ├── chat/              # Chat interface (protected)
│   │   ├── analytics/         # Analytics dashboard (protected)
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   └── globals.css        # Global styles
│   │
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── chat/             # Chat components
│   │   ├── analytics/        # Chart components
│   │   └── layout/           # Layout components
│   │
│   ├── lib/                   # Utility libraries
│   │   ├── api/              # API client
│   │   ├── auth/             # Phase 2 session integration
│   │   ├── hooks/            # Custom React hooks
│   │   └── utils/            # Helper functions
│   │
│   ├── types/                 # TypeScript types
│   └── config/                # Configuration
│
├── public/                    # Static assets
├── tests/                     # Tests
├── .env.local                 # Environment variables (gitignored)
├── .env.example              # Environment template
├── next.config.js            # Next.js config
├── tailwind.config.ts        # Tailwind config
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencies
```

**Note**: No authentication pages (sign-in/sign-up) - Phase 2 handles all authentication.

---

## First-Time Setup Checklist

- [ ] Node.js 18+ installed
- [ ] Repository cloned
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` created with all required variables
- [ ] Phase 2 Better Auth running and accessible
- [ ] OpenAI domain allowlist configured
- [ ] `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` added to `.env.local`
- [ ] Backend API running at `http://localhost:8001`
- [ ] Backend health check passes
- [ ] Development server started (`npm run dev`)
- [ ] Application accessible at `http://localhost:3000`

---

## Testing the Application

### 1. Verify Phase 2 Authentication

**Prerequisites**: You must be authenticated in Phase 2 first.

1. Navigate to Phase 2 application (e.g., http://localhost:3000)
2. Sign in with your Phase 2 credentials
3. Verify session cookie exists (browser DevTools → Application → Cookies → `better-auth.session_token`)

### 2. Access Chat Interface

Navigate to: http://localhost:3000/chat (or your Phase 3 frontend URL)

**Expected**:
- If authenticated in Phase 2: Chat interface loads
- If not authenticated: Redirected to Phase 2 sign-in page
- Dark theme applied
- ChatKit interface visible

### 3. Test Chat Functionality

In the chat interface:

1. Type: "Add a task to buy groceries"
2. Press Enter

**Expected**:
- Message sent to backend
- AI responds with confirmation
- Task created via MCP tool

**Test Commands**:
- "Show me all my tasks"
- "Mark task 1 as complete"
- "Delete task 2"
- "Update task 1 to 'Buy groceries and fruits'"

### 4. Analytics Dashboard

1. Navigate to Analytics (click "Analytics" in navigation)

**Expected**:
- Status distribution chart (donut chart)
- Completion trend chart (line chart)
- Charts display task data

### 5. Session Management

**Note**: Sign-out is handled by Phase 2. To sign out:

1. Navigate to Phase 2 application
2. Click "Sign Out" button in Phase 2

**Expected**:
- Session cleared by Phase 2
- Cannot access Phase 3 protected routes (chat, analytics)
- Redirected to Phase 2 sign-in when attempting to access protected routes

---

## Common Issues and Solutions

### Issue: "Cannot connect to backend"

**Symptoms**: API calls fail, chat doesn't work

**Solutions**:
1. Verify backend is running: `curl http://localhost:8001/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure no CORS issues (backend should allow frontend origin)

### Issue: "ChatKit domain not allowed"

**Symptoms**: ChatKit fails to load, console error about domain

**Solutions**:
1. Register domain in OpenAI dashboard
2. Add `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` to `.env.local`
3. Restart development server

### Issue: "Session not found" or "Unauthorized"

**Symptoms**: Redirected to sign-in, cannot access chat/analytics

**Solutions**:
1. Verify you are authenticated in Phase 2 first
2. Check Phase 2 session cookie exists: `better-auth.session_token`
3. Ensure Phase 2 and Phase 3 are on the same domain (for cookie sharing)
4. Verify cookies are enabled in browser
5. Clear browser cookies and sign in again via Phase 2

### Issue: "User ID mismatch" error

**Symptoms**: 403 Forbidden when accessing chat

**Solutions**:
1. Verify JWT token is valid (check Phase 2 session)
2. Ensure backend is correctly extracting user_id from JWT
3. Check backend logs for JWT verification errors

### Issue: TypeScript errors

**Symptoms**: Type errors in IDE or build

**Solutions**:
1. Run `npm install` to ensure all types are installed
2. Check `tsconfig.json` has `strict: true`
3. Verify all imports have proper types

### Issue: Tailwind styles not applying

**Symptoms**: Components look unstyled

**Solutions**:
1. Verify `tailwind.config.ts` is configured correctly
2. Check `globals.css` imports Tailwind directives
3. Restart development server

---

## Development Workflow

### 1. Create a New Component

```bash
# Create component file
touch src/components/MyComponent.tsx
```

```tsx
// src/components/MyComponent.tsx
'use client'; // If using client-side features

export function MyComponent() {
  return (
    <div className="p-4 bg-gray-900 rounded-lg">
      <h2 className="text-xl font-bold text-gray-100">My Component</h2>
    </div>
  );
}
```

### 2. Add a New Route

```bash
# Create route directory
mkdir -p src/app/my-route

# Create page
touch src/app/my-route/page.tsx
```

```tsx
// src/app/my-route/page.tsx
export default function MyRoutePage() {
  return (
    <main className="min-h-screen bg-gray-950 p-8">
      <h1 className="text-3xl font-bold text-gray-100">My Route</h1>
    </main>
  );
}
```

### 3. Add API Client Function

```typescript
// src/lib/api/client.ts
export async function fetchData<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
```

### 4. Run Tests

```bash
# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Test coverage
npm run test:coverage
```

---

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`
4. Deploy

**Important**:
- Register your production domain in OpenAI's domain allowlist before deploying
- Ensure Phase 2 and Phase 3 are deployed on the same domain for cookie sharing
- No authentication environment variables needed - Phase 3 reads Phase 2 session cookies

### Other Platforms

The application can be deployed to any platform that supports Next.js:
- Netlify
- AWS Amplify
- DigitalOcean App Platform
- Self-hosted with Docker

---

## Environment-Specific Configuration

### Development

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key-from-openai
```

**Note**: Phase 2 session cookies automatically accessible on same domain.

### Staging

```bash
NEXT_PUBLIC_API_URL=https://api-staging.yourdomain.com
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-staging-domain-key
```

### Production

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-production-domain-key
```

**Critical**: Ensure Phase 2 and Phase 3 are on the same domain in all environments for session cookie sharing.

---

## Performance Optimization

### 1. Enable Next.js Optimizations

Already configured in `next.config.js`:
- Image optimization
- Font optimization
- Code splitting
- Tree shaking

### 2. Lazy Load Heavy Components

```tsx
import dynamic from 'next/dynamic';

const AnalyticsChart = dynamic(() => import('@/components/AnalyticsChart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false, // Disable SSR for client-only components
});
```

### 3. Memoize Expensive Computations

```tsx
import { useMemo } from 'react';

const chartData = useMemo(() =>
  transformTasksToChartData(tasks),
  [tasks]
);
```

---

## Security Best Practices

1. **Never commit `.env.local`** - It's gitignored by default
2. **Validate all user input** - Use Zod schemas
3. **Keep dependencies updated** - Run `npm audit` regularly
4. **Use HTTPS in production** - Required for secure cookies
5. **Same domain requirement** - Phase 2 and Phase 3 must be on same domain for cookie sharing
6. **Trust Phase 2 authentication** - Phase 3 relies on Phase 2 for all auth security

---

## Getting Help

### Documentation

- [Next.js 15 Docs](https://nextjs.org/docs)
- [Better Auth Docs](https://www.better-auth.com/)
- [OpenAI ChatKit Docs](https://github.com/openai/chatkit-js)
- [Recharts Docs](https://recharts.org/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Troubleshooting

1. Check browser console for errors
2. Check terminal for server errors
3. Verify environment variables are set correctly
4. Ensure backend is running and accessible
5. Clear browser cache and cookies

### Support

- GitHub Issues: [Repository Issues](https://github.com/your-repo/issues)
- Project Documentation: `specs/001-chatbot-frontend/`

---

## Next Steps

After completing the quickstart:

1. **Explore the codebase**: Familiarize yourself with the project structure
2. **Read the specification**: `specs/001-chatbot-frontend/spec.md`
3. **Review the plan**: `specs/001-chatbot-frontend/plan.md`
4. **Check the data model**: `specs/001-chatbot-frontend/data-model.md`
5. **Start implementing**: Follow the tasks in `specs/001-chatbot-frontend/tasks.md` (once generated)

---

## Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking

# Testing
npm run test             # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Generate coverage report
npm run test:e2e         # Run E2E tests

# Utilities
npm run clean            # Clean build artifacts
npm run format           # Format code with Prettier
```

---

**Ready to start?** Run `npm run dev` and navigate to http://localhost:3000! 🚀
