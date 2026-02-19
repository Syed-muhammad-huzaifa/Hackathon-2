---
title: TaskFlow Backend
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 8001
pinned: false
---

# Backend API for Task Management

A production-ready, secure, multi-tenant FastAPI service for task management with N-Tier architecture.

## ✨ Features

- 🔐 **JWT Authentication** - Secure authentication with Better Auth integration
- 👥 **Multi-Tenancy** - Complete data isolation between users
- 🏗️ **N-Tier Architecture** - Clean separation: Routes → Services → Repositories
- ⚡ **Async/Await** - High-performance async operations throughout
- 🛡️ **Security Hardening** - Rate limiting, security headers, input validation
- 📊 **Comprehensive Logging** - Request tracking with correlation IDs
- 🔍 **Health Checks** - Kubernetes-ready liveness and readiness probes
- 🐳 **Docker Ready** - Production-ready containerization
- 📚 **Full Documentation** - API reference, deployment guides, and examples

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- PostgreSQL database (Neon Serverless recommended)
- 'uv' package manager

### Installation

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
uv run uvicorn app.main:app --reload
```

### Docker Deployment

```bash
# Using Docker Compose (includes PostgreSQL)
docker-compose up -d

# Or build and run manually
docker build -t taskapi .
docker run -p 8000:8000 --env-file .env taskapi
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 Documentation

- **[API Reference](API.md)** - Complete endpoint documentation with examples
- **[Production Deployment](PRODUCTION.md)** - Deployment guide for all platforms
- **[Enhancements Summary](ENHANCEMENTS.md)** - Production-ready features overview
- **[Quickstart Guide](../../specs/002-todo-backend-api/quickstart.md)** - Detailed setup instructions

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/                    # Presentation Layer
│   │   ├── v1/
│   │   │   ├── tasks.py        # Task CRUD endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   ├── middleware.py       # Request logging
│   │   ├── security_middleware.py  # Security headers
│   │   ├── rate_limit_middleware.py  # Rate limiting
│   │   └── exception_handlers.py  # Global error handlers
│   ├── services/               # Service Layer
│   │   └── task_service.py     # Business logic
│   ├── repositories/           # Repository Layer
│   │   └── task_repository.py  # Data access
│   ├── models/                 # SQLModel entities + schemas
│   │   └── task.py             # Task model and schemas
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database connection
│   │   ├── auth.py             # JWT verification
│   │   └── validation.py       # Input validation
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── Dockerfile                  # Production container
├── docker-compose.yml          # Local development
├── pyproject.toml              # Project configuration
├── .env.example                # Environment template
├── API.md                      # API documentation
├── PRODUCTION.md               # Deployment guide
├── ENHANCEMENTS.md             # Features summary
└── README.md                   # This file
```

## 🔒 Security Features

- ✅ JWT token verification with Better Auth
- ✅ Multi-tenancy with user_id filtering
- ✅ Rate limiting (60 requests/minute per user)
- ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)
- ✅ Input validation and sanitization
- ✅ SQL injection protection (parameterized queries)
- ✅ Request ID tracking for audit trails
- ✅ Soft delete (data retention)

## 🎯 API Endpoints

### Tasks
- `GET /api/{user_id}/tasks` - List all tasks
- `GET /api/{user_id}/tasks/{task_id}` - Get specific task
- `POST /api/{user_id}/tasks` - Create new task
- `PATCH /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task (soft delete)

### Health Checks
- `GET /health` - Overall health with database check
- `GET /health/ready` - Readiness probe (Kubernetes)
- `GET /health/live` - Liveness probe (Kubernetes)

## 🧪 Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format app/ tests/

# Lint code
uv run ruff check app/ tests/

# Type checking
uv run mypy app/
```

## 🚀 Production Deployment

See [PRODUCTION.md](PRODUCTION.md) for detailed deployment instructions for:
- Docker/Docker Compose
- AWS Elastic Beanstalk
- Google Cloud Run
- Heroku
- VPS with systemd
- Kubernetes

### Environment Variables (Production)

```bash
# Critical Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
BETTER_AUTH_SECRET=<strong-secret-here>
ALLOWED_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql+psycopg://user:pass@host/db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
ENABLE_SECURITY_HEADERS=true
```

## 📊 Performance

- **Connection Pooling**: 20 connections with 10 overflow
- **Async Operations**: Full async/await support
- **Multiple Workers**: Configurable worker processes
- **Database Indexes**: Optimized queries with composite indexes
- **Rate Limiting**: Prevents abuse and ensures fair usage

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

Key settings:
- `APP_ENV`: Environment (development/staging/production)
- `DEBUG`: Enable debug mode (false in production)
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Shared secret with frontend
- `ALLOWED_ORIGINS`: CORS allowed origins
- `RATE_LIMIT_PER_MINUTE`: Rate limit threshold

## 🤝 Contributing

1. Follow the N-Tier architecture pattern
2. Add comprehensive error handling
3. Include logging for important operations
4. Write tests for new features
5. Update documentation

## 📝 License

[Your License Here]

## 🆘 Support

- **Health Status**: Check `/health` endpoint
- **API Docs**: Visit `/docs` (development only)
- **Issues**: [Your issue tracker]
- **Documentation**: See API.md and PRODUCTION.md

---

**Status**: ✅ Production Ready
**Version**: 0.1.0
**Architecture**: N-Tier (Routes → Services → Repositories)
**Database**: PostgreSQL with SQLModel
**Authentication**: JWT with Better Auth
