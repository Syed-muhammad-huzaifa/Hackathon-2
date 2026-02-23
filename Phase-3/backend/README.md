# Phase 3 Backend - AI Chatbot API

FastAPI backend with OpenAI Agents SDK integration for AI-powered task management chatbot.

## Features

- **OpenAI Agents SDK**: Stateless chat endpoint with agent orchestration
- **MCP Server**: 5 task management tools (add, list, complete, delete, update)
- **ChatKit Adapter**: Conversation state management
- **Guardrail Service**: Content safety and validation
- **JWT Authentication**: Better Auth integration
- **PostgreSQL**: Neon serverless database with async SQLModel

## Tech Stack

- Python 3.12+
- FastAPI (async)
- OpenAI Agents SDK
- SQLModel (async ORM)
- Neon PostgreSQL
- Grok API (OpenAI-compatible)

## Local Development

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Neon PostgreSQL database
- Grok API key

### Setup

1. **Install dependencies:**
   ```bash
   cd Phase-3/backend
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run development server:**
   ```bash
   uv run uvicorn app.main:app --reload --port 8001
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:8001/health/live
   ```

## Deployment to Hugging Face Spaces

### Step 1: Create a New Space

1. Go to https://huggingface.co/new-space
2. **Space name**: `backend-chatbot` (or your preferred name)
3. **License**: Apache 2.0
4. **Space SDK**: Docker
5. **Visibility**: Public or Private
6. Click **Create Space**

### Step 2: Set Environment Variables

Go to your Space settings: `https://huggingface.co/spaces/huz111/backend-chatbot/settings`

Add these environment variables:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname?ssl=require

# Better Auth (Phase 3 frontend URL)
BETTER_AUTH_URL=https://your-phase3-frontend.vercel.app

# Grok API
GROK_API_KEY=gsk_your_grok_api_key_here
GROK_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-3-mini

# Server
PORT=7860
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# CORS (comma-separated)
ALLOWED_ORIGINS=https://your-phase3-frontend.vercel.app,http://localhost:3000
```

### Step 3: Deploy

Run the deployment script:

```bash
# Set your Hugging Face token
export HF_TOKEN='your_hf_token_here'

# Optional: Set custom space name (default: huz111/backend-chatbot)
export HF_SPACE_NAME='your-username/your-space-name'

# Deploy
bash deploy.sh
```

The script will:
- Use git subtree to push only the `Phase-3/backend/` directory
- Deploy to your Hugging Face Space
- Trigger a Docker build

### Step 4: Verify Deployment

1. Wait for the build to complete (check Space logs)
2. Test the health endpoint:
   ```bash
   curl https://huz111-backend-chatbot.hf.space/health/live
   ```

3. Expected response:
   ```json
   {"status": "healthy"}
   ```

## API Endpoints

### Health Check
- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe

### Chat
- `POST /api/v1/chat` - Send message to AI chatbot
  - Requires JWT authentication
  - Body: `{"message": "string", "conversation_id": "string"}`

### Tasks (via MCP tools)
- Managed through chat interface
- Tools: add_task, list_tasks, complete_task, delete_task, update_task

## Architecture

```
Phase-3/backend/
├── app/
│   ├── api/v1/          # API routes
│   ├── core/            # Config, auth, database
│   ├── mcp/             # MCP server and tools
│   ├── models/          # SQLModel database models
│   ├── repositories/    # Data access layer
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── tests/               # Test suite
├── Dockerfile           # Docker configuration
├── pyproject.toml       # Dependencies (uv)
└── deploy.sh            # Deployment script
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_URL` | Yes | Phase 3 frontend URL for JWT validation |
| `GROK_API_KEY` | Yes | Grok API key for AI agent |
| `GROK_BASE_URL` | Yes | Grok API base URL |
| `GROK_MODEL` | Yes | Grok model name |
| `ALLOWED_ORIGINS` | Yes | CORS allowed origins |
| `PORT` | No | Server port (default: 8001, HF Spaces: 7860) |
| `APP_ENV` | No | Environment (development/production) |
| `DEBUG` | No | Debug mode (true/false) |
| `LOG_LEVEL` | No | Logging level (INFO/DEBUG/WARNING) |

## Testing

Run the test suite:

```bash
uv run pytest
```

## Troubleshooting

### Build fails on HF Spaces
- Check Space logs for errors
- Verify all environment variables are set
- Ensure DATABASE_URL is accessible from HF Spaces

### Database connection errors
- Verify Neon PostgreSQL allows connections from HF Spaces IPs
- Check DATABASE_URL format includes `?ssl=require`

### CORS errors
- Add your frontend URL to `ALLOWED_ORIGINS`
- Ensure `BETTER_AUTH_URL` matches your frontend

## Support

For issues or questions, check:
- Specifications: `specs/001-chatbot-backend/`
- Prompt history: `history/prompts/001-chatbot-backend/`
