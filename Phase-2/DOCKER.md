# Docker Deployment Guide

This guide covers running TaskFlow with Docker for development and production.

## Quick Start

### 1. Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -base64 32`
- `POSTGRES_PASSWORD`: Strong password for local DB

### 3. Run Full Stack

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## Individual Services

### Backend Only

```bash
cd backend
docker-compose up -d
```

### Frontend Only

```bash
cd frontend
docker-compose up -d
```

## Production Deployment

### 1. Build Production Images

```bash
# Build all services
docker-compose build --no-cache

# Or build individually
docker-compose build backend
docker-compose build frontend
```

### 2. Using Neon PostgreSQL

If using Neon (recommended for production), remove the `db` service:

```yaml
# In docker-compose.yml, comment out:
# db:
#   image: postgres:16-alpine
#   ...

# And remove depends_on db from other services
```

Update `DATABASE_URL` to your Neon connection string.

### 3. Environment Variables

**Production Checklist:**
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Use strong `BETTER_AUTH_SECRET`
- [ ] Configure `ALLOWED_ORIGINS` with your domain
- [ ] Use SSL-enabled `DATABASE_URL`
- [ ] Set `NODE_ENV=production`

### 4. Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Common Commands

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Execute Commands in Container

```bash
# Backend shell
docker-compose exec backend sh

# Frontend shell
docker-compose exec frontend sh

# Run migrations (if needed)
docker-compose exec backend uv run alembic upgrade head
```

## Health Checks

All services include health checks:

```bash
# Check backend health
curl http://localhost:8000/health/live

# Check frontend health
curl http://localhost:3000/api/health

# View health status
docker-compose ps
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in docker-compose.yml
ports:
  - "3001:3000"  # Use 3001 instead
```

### Database Connection Failed

1. Check `DATABASE_URL` format:
   ```
   postgresql://user:password@host:5432/database
   ```

2. Verify database is running:
   ```bash
   docker-compose ps db
   ```

3. Check logs:
   ```bash
   docker-compose logs db
   ```

### Frontend Can't Reach Backend

1. Ensure `NEXT_PUBLIC_API_URL` is correct
2. Check CORS settings in backend `.env`
3. Verify backend is healthy:
   ```bash
   curl http://localhost:8000/health/live
   ```

### Out of Memory

1. Increase Docker memory limit (Docker Desktop → Settings → Resources)
2. Add resource limits to services
3. Reduce worker count in backend Dockerfile

### Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

## Performance Optimization

### 1. Multi-stage Builds

Both Dockerfiles use multi-stage builds to minimize image size:
- Backend: ~200MB (vs ~1GB without optimization)
- Frontend: ~150MB (vs ~800MB without optimization)

### 2. Layer Caching

Dependencies are installed before copying source code to leverage Docker layer caching.

### 3. Production Workers

Backend runs with 4 Uvicorn workers by default. Adjust in `backend/Dockerfile`:

```dockerfile
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Security Best Practices

1. **Non-root User**: Both containers run as non-root users
2. **Secrets Management**: Never commit `.env` files
3. **Network Isolation**: Services communicate via internal Docker network
4. **Health Checks**: Automatic restart on failure
5. **Read-only Filesystem**: Consider adding `read_only: true` for production

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats taskflow-backend
```

### Disk Usage

```bash
# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Backend
        run: |
          cd Phase-2/backend
          docker build -t taskflow-backend:latest .
      
      - name: Build Frontend
        run: |
          cd Phase-2/frontend
          docker build -t taskflow-frontend:latest .
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Review health check status
4. Check GitHub Issues
