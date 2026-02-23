# TaskAI - AI-Powered Task Manager

Conversational task management with natural language interface powered by OpenAI Agents SDK and Better Auth.

## Features

- 🤖 **AI Chatbot** - Manage tasks through natural language conversation
- 📊 **Analytics Dashboard** - Visual insights into task completion patterns
- 🔒 **Secure Authentication** - Better Auth with JWT tokens
- 💬 **Natural Language** - Create, update, complete, and delete tasks by chatting
- 📱 **Responsive Design** - Works on mobile, tablet, and desktop
- 🎨 **Premium UI** - Dark theme with glassmorphism effects

## Tech Stack

- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS
- **Authentication**: Better Auth (JWT tokens)
- **Chat UI**: OpenAI ChatKit
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Backend**: FastAPI + OpenAI Agents SDK + MCP Tools (separate repo)

## Prerequisites

- Node.js 18+
- PostgreSQL database (Neon recommended)
- Backend API running (Phase-3/backend)

## Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Configure environment variables**:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
DATABASE_URL=postgresql://user:password@host:5432/database
NEXT_PUBLIC_APP_URL=http://localhost:3001
NEXT_PUBLIC_API_URL=http://localhost:8001
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3001
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key
```

3. **Setup Better Auth database**:
```bash
npx @better-auth/cli generate
npx @better-auth/cli migrate
```

4. **Configure OpenAI ChatKit**:
- Visit https://platform.openai.com/settings/organization/security/domain-allowlist
- Add `localhost:3001` for development
- Copy the domain key to `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`

5. **Run development server**:
```bash
npm run dev
```

Open http://localhost:3001

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth pages (signin, signup)
│   ├── (dashboard)/       # Dashboard pages (chatbot, analytics, settings)
│   ├── api/               # API routes (Better Auth)
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # Base UI components
│   ├── auth/             # Auth components
│   ├── chat/             # Chat components
│   ├── analytics/        # Analytics components
│   └── layout/           # Layout components
├── lib/                   # Utilities
│   ├── api/              # API client
│   ├── auth/             # Better Auth config
│   ├── hooks/            # Custom hooks
│   ├── animations/       # Framer Motion variants
│   └── utils/            # Helper functions
└── types/                 # TypeScript types
```

## Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## Authentication Flow

1. User signs up with email/password
2. Better Auth creates account and generates JWT token
3. JWT stored in httpOnly cookie
4. Frontend sends JWT to backend in Authorization header
5. Backend verifies JWT via JWKS endpoint
6. User accesses protected dashboard routes

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

**Important**: Register production domain in OpenAI ChatKit allowlist before deploying.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `NEXT_PUBLIC_APP_URL` | Frontend URL | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `BETTER_AUTH_SECRET` | Secret for JWT signing | Yes |
| `BETTER_AUTH_URL` | Better Auth URL (same as APP_URL) | Yes |
| `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` | OpenAI ChatKit domain key | Yes |

## License

MIT
