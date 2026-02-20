---
title: TaskFlow Backend API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# TaskFlow Backend API

A production-grade FastAPI backend for task management with multi-tenant support and JWT authentication.

## Features

- **Multi-tenant Architecture**: Row-level security with user isolation
- **JWT Authentication**: Secure token-based authentication via Better Auth
- **Async Operations**: Full async/await support with SQLModel and asyncpg
- **Rate Limiting**: Built-in request rate limiting
- **Health Checks**: Liveness and readiness endpoints
- **CORS Support**: Configurable cross-origin resource sharing
- **Security Headers**: Production-ready security middleware

## API Endpoints

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe
- `GET /api/{user_id}/tasks` - List all tasks for user
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks/{task_id}` - Get task by ID
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

## Environment Variables

Configure these in your Space settings:
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT signing secret
- `BETTER_AUTH_URL`: Better Auth service URL
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

## Tech Stack

- FastAPI 0.109+
- SQLModel (async ORM)
- PostgreSQL (Neon Serverless)
- PyJWT for token verification
- uvicorn ASGI server

## Architecture

Follows strict layered architecture:
- **Models**: SQLModel schemas and database tables
- **Repositories**: Data access layer
- **Services**: Business logic and validation
- **Routes**: HTTP handlers and dependency injection

Built with ❤️ using FastAPI and deployed on Hugging Face Spaces
