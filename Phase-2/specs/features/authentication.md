# Feature Specification: Authentication & Authorization

## 1. Overview
Authentication is the gatekeeper of the application. We use **Better Auth** for the frontend user experience and **JWT (JSON Web Tokens)** to secure the backend. This ensures that every task in the database is tied to a specific identity.

## 2. Technical Stack
- **Frontend Auth:** Better Auth (Social + Credentials).
- **Backend Validation:** Custom FastAPI middleware/dependency using `PyJWT`.
- **Token Type:** Bearer Token (JWT).
- **Secret Management:** `BETTER_AUTH_SECRET` shared between Next.js and FastAPI.

## 3. The Authentication Flow

### 3.1 Frontend (Client-Side)
1. User enters credentials on the Next.js login page.
2. Better Auth handles the handshake and stores the session/token.
3. Every subsequent request to the FastAPI backend includes the header:
   `Authorization: Bearer <token>`

### 3.2 Backend (Server-Side)
The backend validates the token at the **Presentation Layer** before any logic reaches the **Service Layer**.

1. **Extraction:** The `get_current_user` dependency in `app/api/deps.py` reads the header.
2. **Verification:** The token is decoded and checked for expiration and signature validity.
3. **Context:** If valid, the `user_id` is injected into the Route function.

## 4. Layered Security Logic

| Layer | Responsibility |
| :--- | :--- |
| **Presentation (Route)** | Calls the `get_current_user` dependency to protect the endpoint. |
| **Service** | Receives the `user_id` and ensures it is passed to all repository calls. |
| **Repository** | Appends `.where(Task.user_id == user_id)` to every SQL query. |

## 5. Security Requirements
- **Password Hashing:** Handled by Better Auth on the frontend/auth server.
- **Environment Variables:** `DATABASE_URL` and `BETTER_AUTH_SECRET` must be set in the backend via `uv`.
- **Data Isolation:** A user session must never be able to "cross-pollinate" data. If `user_A` tries to access `task_id` belonging to `user_B`, the **Service Layer** must raise a `403 Forbidden` error.

## 6. Implementation Instructions for Agent
1. **Dependency:** Implement `get_current_user` in `backend/app/api/deps.py`.
2. **Decoding:** Use `jwt.decode` with the `BETTER_AUTH_SECRET`.
3. **Usage:** Apply the dependency to the `APIRouter` in `backend/app/api/v1/tasks.py` so all task routes are protected by default.