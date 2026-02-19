# TaskFlow - Complete Docker Setup Guide

## Step 1: Check Prerequisites

```bash
# Check Docker is installed and running
docker --version
docker-compose --version

# Check Docker is running
docker ps
```

Expected output:
- Docker version 20.10+
- Docker Compose version 2.0+

## Step 2: Setup Environment Variables

```bash
cd Phase-2

# Copy environment template
cp .env.example .env

# Edit with your values
nano .env  # or use any text editor
```

**Required values in .env:**
```env
# Generate secret: openssl rand -base64 32
BETTER_AUTH_SECRET=your-generated-secret-here

# For Neon PostgreSQL (recommended)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# For local PostgreSQL
DATABASE_URL=postgresql://taskflow:your-password@db:5432/taskflow
POSTGRES_PASSWORD=your-secure-password
```

## Step 3: Build Docker Images

```bash
# Build all images (backend + frontend)
docker-compose build

# Or build with no cache (clean build)
docker-compose build --no-cache
```

This will:
- Build backend Python image (~5-10 minutes first time)
- Build frontend Next.js image (~5-10 minutes first time)
- Subsequent builds are faster due to caching

## Step 4: Start All Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Or start with logs visible
docker-compose up
```

This starts:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL database (port 5432) - if using local DB

## Step 5: Verify Services are Running

```bash
# Check all containers are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health/live

# Check frontend health
curl http://localhost:3000/api/health

# View logs
docker-compose logs -f
```

## Step 6: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build

# Or use the script
./docker-rebuild.sh
```

### Execute Commands Inside Containers
```bash
# Backend shell
docker-compose exec backend sh

# Frontend shell
docker-compose exec frontend sh

# Run backend commands
docker-compose exec backend uv run python -m app.main
```

## Automated Scripts (Easier Method)

### Quick Start
```bash
./docker-start.sh
```

### View Logs
```bash
./docker-logs.sh           # All services
./docker-logs.sh backend   # Backend only
./docker-logs.sh frontend  # Frontend only
```

### Stop
```bash
./docker-stop.sh
```

### Rebuild
```bash
./docker-rebuild.sh
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database Connection Failed
1. Check DATABASE_URL in .env
2. Verify database is running: `docker-compose ps db`
3. Check logs: `docker-compose logs db`

### Frontend Can't Reach Backend
1. Check NEXT_PUBLIC_API_URL in .env
2. Verify backend is running: `curl http://localhost:8000/health/live`
3. Check CORS settings in backend .env (ALLOWED_ORIGINS)

### Build Fails
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### Container Keeps Restarting
```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port conflicts
```

## Production Deployment

For production:
1. Use Neon PostgreSQL (remove local db service)
2. Set APP_ENV=production
3. Set DEBUG=false
4. Use strong BETTER_AUTH_SECRET
5. Configure proper ALLOWED_ORIGINS
6. Enable SSL for DATABASE_URL

## Next Steps

After services are running:
1. Visit http://localhost:3000
2. Sign up for an account
3. Create your first task
4. Check analytics at http://localhost:3000/dashboard/analytics

## Support

- Full documentation: [DOCKER.md](./DOCKER.md)
- Quick reference: [README.Docker.md](./README.Docker.md)
- View logs: `docker-compose logs -f`
