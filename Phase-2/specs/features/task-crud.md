# Feature Specification: Task CRUD Operations

## 1. Overview
This feature enables users to manage their personal todo items. By implementing a strict **Layered Architecture**, we ensure that all Create, Read, Update, and Delete (CRUD) operations are validated for ownership before the database is modified.

## 2. User Stories
- **Create:** As a user, I want to add a task with a title and description to my list.
- **Read:** As a user, I want to see only my tasks, sorted by the most recently updated.
- **Update:** As a user, I want to mark tasks as complete or edit their content.
- **Delete:** As a user, I want to remove tasks I no longer need.

## 3. Technical Logic & Layering

### 3.1 Create Operation
1. **Route:** Receives `TaskCreate` schema and `user_id`.
2. **Service:** Validates the title length and prepares the domain object.
3. **Repository:** Executes `INSERT` into the `task` table with the `user_id`.

### 3.2 Read Operation
1. **Route:** Requests all tasks for the authenticated user.
2. **Service:** Requests data from the Repository for a specific `user_id`.
3. **Repository:** Executes `SELECT * FROM task WHERE user_id = :uid`.

### 3.3 Update/Delete (Ownership Validation)
Before any `UPDATE` or `DELETE` occurs, the **Service Layer** must perform a "Secure Fetch":
- The Service asks the Repository for the task by `ID`.
- If the task exists but the `user_id` does not match the session, the Service raises a `403 Forbidden` error.
- Only if IDs match does the Service proceed with the update/deletion command.

## 4. UI/UX Requirements
- **Optimistic UI:** When a user toggles a checkbox, the UI should update immediately while the `PATCH` request happens in the background.
- **Loading States:** Show skeleton loaders in the task list during the initial fetch.
- **Empty States:** Display a clear message ("You have no tasks!") when the list is empty.
- **Feedback:** Use Toast notifications for errors (e.g., "Failed to save task").

## 5. Implementation Instructions for Agent

### 5.1 Repository Layer (`backend/app/repositories/task_repo.py`)
- Implement `get_all(user_id)`, `create(obj)`, `get_by_id(id)`, and `delete(id)`.
- Ensure all methods use `async` and the `SQLModel` session.

### 5.2 Service Layer (`backend/app/services/task_service.py`)
- Implement business logic that accepts `current_user_id`.
- Handle the `404 Not Found` and `403 Forbidden` logic here.

### 5.3 Presentation Layer (`backend/app/api/v1/tasks.py`)
- Define the endpoints and use FastAPI `Depends` to inject the `TaskService`.
- Map database objects to `TaskRead` schemas to avoid leaking internal IDs or `user_id` if not needed.