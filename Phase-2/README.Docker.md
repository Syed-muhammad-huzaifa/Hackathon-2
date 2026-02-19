# TaskFlow - Docker Quick Start

Production-ready Docker setup for TaskFlow (Backend + Frontend).

## 🚀 Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your values

# 2. Start everything
./docker-start.sh

# 3. Access the app
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📦 What's Included

### Services
- **Backend**: FastAPI (Python 3.12) on port 8000
- **Frontend**: Next.js 15 on port 3000
- **Database**: PostgreSQL 16 on port 5432 (optional, use Neon for production)

### Features
- ✅ Multi-stage builds (optimized image sizes)
- ✅ Health checks for all services
- ✅ Non-root users for security
- ✅ Hot reload disabled (production mode)
- ✅ Automatic restarts on failure
- ✅ Resource limits ready
- ✅ Network isolation

## 🛠️ Utility Scripts

```bash
./docker-start.sh    # Build and start all services
./docker-stop.sh     # Stop all services
./docker-logs.sh     # View logs (all services)
./docker-logs.sh backend   # View backend logs only
./docker-rebuild.sh  # Rebuild from scratch
```

## 📝 Manual Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Check status
docker-compose ps

# Execute commands in container
docker-compose exec backend sh
docker-compose exec frontend sh
```

## 🔧 Configuration

### Required Environment Variables

**Backend (.env or Phase-2/.env):**
- `DATABASE_URL` - PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Auth secret (generate with `openssl rand -base64 32`)
- `ALLOWED_ORIGINS` - CORS origins (e.g., `http://localhost:3000`)

**Frontend (.env.local or Phase-2/.env):**
- `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., `http://localhost:8000`)
- `BETTER_AUTH_SECRET` - Same as backend
- `DATABASE_URL` - Same as backend (for Better Auth)

### Using Neon PostgreSQL

For production, use Neon instead of local PostgreSQL:

1. Comment out the `db` service in `docker-compose.yml`
2. Set `DATABASE_URL` to your Neon connection string
3. Remove `depends_on: db` from other services

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Docker Network: taskflow-network      │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────┐ │
│  │ Frontend │  │ Backend  │  │  DB  │ │
│  │  :3000   │◄─┤  :8000   │◄─┤ :5432│ │
│  └──────────┘  └──────────┘  └──────┘ │
└─────────────────────────────────────────┘
```

## 📊 Health Checks

All services expose health endpoints:

```bash
# Backend
curl http://localhost:8000/health/live

# Frontend
curl http://localhost:3000/api/health
```

## 🐛 Troubleshooting

### Port conflicts
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database connection issues
1. Check `DATABASE_URL` format
2. Verify database is running: `docker-compose ps db`
3. Check logs: `docker-compose logs db`

### Build failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## 📚 Documentation

See [DOCKER.md](./DOCKER.md) for comprehensive documentation including:
- Production deployment
- Security best practices
- Performance optimization
- CI/CD integration
- Monitoring

## 🔒 Security Notes

- Both containers run as non-root users
- Never commit `.env` files
- Use strong secrets in production
- Enable SSL for production databases
- Configure CORS properly

## 📈 Performance

**Image Sizes:**
- Backend: ~200MB (optimized with multi-stage build)
- Frontend: ~150MB (Next.js standalone output)

**Resource Usage:**
- Backend: ~512MB RAM, 0.5 CPU
- Frontend: ~256MB RAM, 0.25 CPU
- Database: ~256MB RAM, 0.25 CPU

## 🤝 Contributing

When modifying Docker configuration:
1. Test locally with `./docker-rebuild.sh`
2. Update documentation
3. Verify health checks pass
4. Check image sizes haven't increased significantly

## 📞 Support

- Documentation: [DOCKER.md](./DOCKER.md)
- Issues: GitHub Issues
- Logs: `./docker-logs.sh`
