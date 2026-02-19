# Database Schema Specification - Phase II

## 1. Overview
The application uses **Neon Serverless PostgreSQL** for persistent storage. Data modeling is handled by **SQLModel**, which bridges the gap between Python classes (Models) and SQL tables.

## 2. Table Definitions

### 2.1 User Table (`user`)
This table stores user identity metadata and serves as the primary key for task ownership.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Provided by Better Auth session. |
| `email` | `String` | Unique, Indexed | User's login identifier. |
| `created_at` | `DateTime`| Default: `now()` | Timestamp of registration. |

### 2.2 Task Table (`task`)
This table contains the core application data.

| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Integer` | Primary Key, Auto-inc | Unique identifier for the task. |
| `user_id` | `UUID` | Foreign Key (`user.id`) | Links task to a specific owner. |
| `title` | `String` | Non-nullable, Max: 255 | Brief title of the todo item. |
| `description`| `String` | Nullable | Detailed notes (Optional). |
| `is_completed`| `Boolean` | Default: `False` | Completion status toggle. |
| `created_at` | `DateTime`| Default: `now()` | Creation timestamp. |
| `updated_at` | `DateTime`| Auto-update | Last modification timestamp. |

## 3. Layered Implementation Logic

### 3.1 Model Layer (`app/models/`)
- Define `User` and `Task` classes inheriting from `SQLModel`.
- Set `table=True` for both.
- Define a relationship property: `tasks: List["Task"] = Relationship(back_populates="user")`.

### 3.2 Repository Layer (`app/repositories/`)
- All queries must be scoped by `user_id`.
- Example Query: `select(Task).where(Task.user_id == user_id)`.
- Use `async` sessions to prevent blocking the event loop.

### 3.3 Service Layer (`app/services/`)
- Validates that the `user_id` passed to the Repository is authorized.
- Handles the logic for updating the `updated_at` timestamp before calling the Repository.

## 4. Connection Strategy
- **Driver:** `psycopg3` (configured for async support).
- **Initialization:** The backend `main.py` utilizes a **Lifespan Context Manager** to execute `SQLModel.metadata.create_all(engine)` on startup.
- **Environment:** The connection string is managed via `DATABASE_URL` in the `.env` file, loaded via `pydantic-settings`.

## 5. Security & Isolation
- **Referential Integrity:** If a user is deleted, all associated tasks must be deleted via `ondelete="CASCADE"`.
- **Row Level Safety:** Business logic in the Service layer ensures that no Repository query executes without a `user_id` filter.