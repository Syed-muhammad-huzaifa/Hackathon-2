# System Architecture - Phase II (Industry Standard)

## 1. High-Level Design
The application follows a **Decoupled Full-Stack Architecture** within a monorepo. It utilizes a **Layered (N-Tier) Pattern** on the backend to ensure business logic is decoupled from the API framework and data access.

## 2. Component Breakdown

### 2.1 Frontend (The Client)
- **Framework:** Next.js 15+ (App Router).
- **State Management:** React Hooks and Context API for Auth state.
- **Styling:** Tailwind CSS + Shadcn/UI for a consistent design system.
- **Authentication:** **Better Auth** client-side SDK for managing login, signup, and session tokens.

### 2.2 Backend (The API Layer)
- **Framework:** FastAPI (Python).
- **Concurrency:** Asynchronous (async/await) request handling.
- **Security:** Middleware to intercept requests and verify JWT tokens issued by Better Auth.
- **Dependency Injection:** Fast API `Depends` is used for database sessions and user authentication checks.

### 2.3 Data Layer (Persistence)
- **Database:** Neon Serverless PostgreSQL.
- **ORM:** SQLModel (Pydantic + SQLAlchemy).
- **Schema Management:** Automated table creation via `SQLModel.metadata.create_all()` on application startup.

## 3. Layered Responsibilities (The Strict Flow)

Communication must follow this unidirectional path: 
**Client** → **Routes** → **Services** → **Repositories** → **Database**.

### 2.1 Presentation Layer (Routes)
- **Location:** `backend/app/api/`
- **Role:** Handles HTTP protocols (GET, POST, etc.), request parsing, and status code responses.
- **Rule:** Never contains SQL or business rules. It only calls the Service layer.

### 2.2 Service Layer (Business Logic)
- **Location:** `backend/app/services/`
- **Role:** The "Brain." It validates user ownership (e.g., "Is this task actually mine?"), performs calculations, and coordinates data.
- **Rule:** Acts as a bridge. It is framework-agnostic.

### 2.3 Data Access Layer (Repositories)
- **Location:** `backend/app/repositories/`
- **Role:** The only layer allowed to interface with `SQLModel` and the database.
- **Rule:** Performs atomic CRUD operations.

### 2.4 Domain Layer (Models)
- **Location:** `backend/app/models/`
- **Role:** Shared Pydantic/SQLModel definitions used by all layers.

## 4. Technology & Infrastructure Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Package Manager** | **uv** | Fast, reliable dependency and venv management. |
| **Backend** | **FastAPI** | High-performance asynchronous API layer. |
| **ORM** | **SQLModel** | Unified Pydantic validation and SQLAlchemy queries. |
| **Database** | **Neon PostgreSQL** | Serverless storage with cloud-native scaling. |
| **Frontend** | **Next.js 15+** | App Router, React Server Components, and TypeScript. |
| **Authentication** | **Better Auth** | Managed authentication with JWT session tokens. |

## 5. Directory Structure

```text
/root
├── /specs                 # Source of Truth (Markdown)
├── /frontend              # Next.js App
└── /backend
    ├── pyproject.toml     # Managed by uv
    └── /app
        ├── main.py        # Entry point & Lifespan management
        ├── /api           # Presentation Layer (Routes)
        │   └── deps.py    # DI for DB and Services
        ├── /services      # Service Layer (Business Logic)
        ├── /repositories  # Data Access Layer (SQL)
        ├── /models        # Shared Models (Tables/Schemas)
        └── /core          # Security/Config (JWT, Env)
```

## 6. Security & Request Lifecycle

1. **Tokenization:** Frontend sends JWT in `Authorization: Bearer <token>` header.

2. **Interception:** `backend/app/api/deps.py` extracts the `user_id` using the `BETTER_AUTH_SECRET`.

3. **Context Injection:** The `user_id` is passed into the Service, then to the Repository.

4. **Data Isolation:** Every query is strictly scoped: `SELECT * FROM tasks WHERE user_id = current_user_id`.