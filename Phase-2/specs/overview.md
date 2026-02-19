# Project Overview: Todo App - Phase II

## 1. Project Mission
The objective of Phase II is to transition the application from a CLI tool to a production-grade **Full-Stack Web Application**. This version focuses on scalability, user data isolation, and a professional **Layered Architecture** to ensure clean separation between UI, business logic, and database operations.

## 2. Core Architecture: The Layered Pattern
To maintain industry standards, the backend is organized into three distinct layers. Communication follows a strict top-down flow:

1.  **Presentation Layer (Routes):** Manages HTTP requests/responses and status codes.
2.  **Service Layer (Business Logic):** Validates data, enforces permissions, and processes business rules.
3.  **Data Access Layer (Repositories):** Executes SQL queries and manages data persistence.

## 3. Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Package Manager** | **uv** | Extremely fast Python package manager for dependency resolution. |
| **Backend** | **FastAPI** | Modern, high-performance Python web framework. |
| **Database** | **Neon PostgreSQL** | Serverless SQL database for cloud-native persistence. |
| **ORM** | **SQLModel** | Unified layer for Pydantic validation and SQLAlchemy queries. |
| **Frontend** | **Next.js 15+** | React framework utilizing the App Router and TypeScript. |
| **Authentication** | **Better Auth** | Secure credential management with JWT-based session handling. |

## 4. Key Functional Requirements
* **Multi-User Support:** Secure signup and login functionality.
* **User Isolation:** Strict "Source of Truth" checks to ensure users only access their own data.
* **Full CRUD:** Create, Read, Update, and Delete tasks through a modern web UI.
* **Persistence:** All data is stored in the Neon cloud, surviving server restarts.

## 5. Development Standards
* **Spec-Driven Development (SDD):** All implementation follows the definitions in the `/specs` folder.
* **Type Safety:** Strict use of TypeScript (Frontend) and Pydantic/Type Hints (Backend).
* **Automated Schema:** Use of `SQLModel.metadata.create_all()` for automatic table generation.