# Todo App Overview – Hackathon II (Phase II)

## Project Name
hackathon-todo

## Current Phase
Phase II – Full-Stack Web Application

## Version
1.0.0 (Phase II specs & initial setup)

## Purpose
This project evolves a simple in-memory console todo app (Phase I) into a **secure, multi-user full-stack web application** with persistent storage and proper authentication.  
It demonstrates **spec-driven development** using Claude Code and Spec-Kit Plus — where all code is generated from written specifications (no manual coding allowed).  
The goal is to build a clean, maintainable foundation for later phases: AI chatbot, Kubernetes deployment, and event-driven cloud-native features.

## Phase II Objective (as per Hackathon Requirements)
Transform the Python console app into a modern web app with:
- Multi-user support via authentication
- Persistent data in Neon Serverless PostgreSQL
- RESTful API endpoints with JWT-based authorization
- Responsive frontend interface
- Strict user isolation: Each user can only access and modify their own tasks

## Core Features – Phase II (Basic Level – Mandatory)
- Add new task (title + optional description)
- View list of tasks (with status indicators)
- Update task details
- Delete task by ID
- Mark task as complete / incomplete
- User signup & signin
- JWT token issuance and verification for API security
- All operations filtered by authenticated user_id

## Tech Stack – Phase II
### Frontend
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (with JWT plugin enabled)

### Backend
- FastAPI (Python 3.13+)
- SQLModel (ORM + validation)
- Neon Serverless PostgreSQL (via DATABASE_URL env var)

### Shared / Tools
- Authentication: Better Auth + JWT (shared secret via BETTER_AUTH_SECRET)
- Project structure: Monorepo with specs/ folder

## Key Constraints & Principles
- User data isolation enforced at API and database level
- Stateless backend where possible
- Clean code, proper error handling (HTTP exceptions), validation
- Environment variables for all secrets

## Development Workflow (Spec-Driven)
1. Write/update Markdown specs in `/specs/`
2. System design documented in @specs/architecture.md
3. Claude generates code in Phase-2/frontend & backend
4. Iterate: Refine spec → re-generate → test
5. Commit specs history (shows process to judges)

## Key Specifications
1. @specs/architecture.md - System architecture, authentication flow, API communication
2. @specs/features/task-crud.md - Task CRUD operations specification
3. @specs/features/authentication.md - Authentication and JWT flow
4. @specs/api/rest-endpoints.md - Complete API endpoint documentation
5. @specs/database/schema.md - Database schema and relationships
6. @specs/ui/components.md - React component library
7. @specs/ui/pages.md - Next.js pages and routing

## References & Next Files
- Root Claude Guide: @CLAUDE.md
- Frontend Guidelines: @frontend/CLAUDE.md
- Backend Guidelines: @backend/CLAUDE.md 
- Constitution: .specify/memory/constitution.md

## Future Phases (Teaser)
- Phase III → AI Chatbot (natural language todo management)
- Phase IV → Local Kubernetes (Minikube + Helm)
- Phase V → Cloud-native (DOKS + Kafka + Dapr)
