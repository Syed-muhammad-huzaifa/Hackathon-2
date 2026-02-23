# Phase 3 Frontend - Deployment Guide

## Quick Deploy to Vercel

### Step 1: Prepare Environment Variables

You'll need these environment variables for Vercel:

```bash
# Database (Neon PostgreSQL - same as Phase 3 backend)
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=verify-full

# Backend API (Phase 3 Backend on HF Spaces)
NEXT_PUBLIC_API_URL=https://huz111-backend-chatbot.hf.space

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-app.vercel.app

# OpenAI ChatKit (get from OpenAI dashboard)
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key

# App URL (will be your Vercel URL)
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

### Step 2: Deploy to Vercel

#### Option A: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from Phase-3/frontend directory:**
   ```bash
   cd Phase-3/frontend
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name? `chatbot-frontend-phase3` (or your choice)
   - Directory? `./` (current directory)
   - Override settings? **N**

5. **Add environment variables:**
   ```bash
   vercel env add DATABASE_URL
   vercel env add NEXT_PUBLIC_API_URL
   vercel env add BETTER_AUTH_SECRET
   vercel env add NEXT_PUBLIC_BETTER_AUTH_URL
   vercel env add NEXT_PUBLIC_CHATKIT_DOMAIN_KEY
   vercel env add NEXT_PUBLIC_APP_URL
   ```

6. **Redeploy with environment variables:**
   ```bash
   vercel --prod
   ```

#### Option B: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Set **Root Directory** to: `Phase-3/frontend`
4. Add environment variables in the dashboard
5. Click **Deploy**

### Step 3: Update Backend CORS

After deployment, update the backend's `ALLOWED_ORIGINS` on HF Spaces:

Go to: https://huggingface.co/spaces/huz111/backend-chatbot/settings

Update `ALLOWED_ORIGINS`:
```bash
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3001
```

Also update `BETTER_AUTH_URL`:
```bash
BETTER_AUTH_URL=https://your-vercel-app.vercel.app
```

### Step 4: Update Frontend Environment Variables

After getting your Vercel URL, update these in Vercel dashboard:

```bash
NEXT_PUBLIC_APP_URL=https://your-actual-vercel-url.vercel.app
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-actual-vercel-url.vercel.app
```

Then redeploy.

### Step 5: Run Database Migrations

After first deployment, run migrations:

```bash
# Option 1: Via Vercel CLI
vercel env pull .env.local
npm run migrate

# Option 2: Manually via Neon SQL Editor
# Run the SQL from drizzle/0000_*.sql
```

## Environment Variables Explained

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string (same as backend) |
| `NEXT_PUBLIC_API_URL` | Yes | Phase 3 backend URL on HF Spaces |
| `BETTER_AUTH_SECRET` | Yes | Secret key for Better Auth (min 32 chars) |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | Your Vercel app URL |
| `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` | Yes | OpenAI ChatKit domain key |
| `NEXT_PUBLIC_APP_URL` | Yes | Your Vercel app URL |

## Local Development

1. **Install dependencies:**
   ```bash
   cd Phase-3/frontend
   npm install
   ```

2. **Create `.env.local`:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your values
   ```

3. **Run migrations:**
   ```bash
   npm run migrate
   ```

4. **Start dev server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   ```
   http://localhost:3001
   ```

## Troubleshooting

### CORS Errors
- Ensure backend `ALLOWED_ORIGINS` includes your Vercel URL
- Check that `NEXT_PUBLIC_API_URL` is correct

### Authentication Errors
- Verify `BETTER_AUTH_SECRET` is at least 32 characters
- Ensure `NEXT_PUBLIC_BETTER_AUTH_URL` matches your Vercel URL
- Check database migrations ran successfully

### ChatKit Errors
- Verify `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` is correct
- Check OpenAI ChatKit dashboard for domain configuration

### Database Connection Errors
- Ensure `DATABASE_URL` includes `?sslmode=verify-full`
- Verify Neon database allows connections from Vercel IPs
- Check database migrations completed

## Production Checklist

- [ ] All environment variables set in Vercel
- [ ] Database migrations completed
- [ ] Backend CORS configured with Vercel URL
- [ ] Better Auth URL updated in backend
- [ ] ChatKit domain configured
- [ ] Test authentication flow
- [ ] Test chatbot functionality
- [ ] Test task management features

## Support

For issues:
- Check specifications: `specs/001-chatbot-frontend/`
- Review prompt history: `history/prompts/001-chatbot-frontend/`
- Backend API: https://huz111-backend-chatbot.hf.space
