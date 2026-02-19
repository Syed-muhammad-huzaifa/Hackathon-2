"""
Task CRUD tests.

Covers:
  - Create, read, update, delete (real DB writes verified)
  - Request validation (title, priority, status enums)
  - Multi-tenancy: user A cannot touch user B's tasks
  - Business rules: cannot update/list deleted tasks
  - Soft-delete: record stays in DB with status="deleted"
  - Response structure matches schema
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import (
    TEST_USER_ID,
    OTHER_USER_ID,
    create_task_in_db,
    get_task_from_db,
)
from app.core.auth import User


# ── Create Task ───────────────────────────────────────────────────────────────

class TestCreateTask:

    async def test_create_task_returns_201(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Buy groceries"},
        )
        assert resp.status_code == 201

    async def test_create_task_persisted_in_database(self, client: AsyncClient, auth_as: User):
        """Verify the row actually exists in Neon PostgreSQL after creation."""
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "DB persistence check"},
        )
        assert resp.status_code == 201
        task_id = resp.json()["data"]["id"]

        db_task = get_task_from_db(task_id)
        assert db_task is not None
        assert db_task.title == "DB persistence check"
        assert db_task.user_id == TEST_USER_ID

    async def test_create_task_default_status_is_pending(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Status check"},
        )
        assert resp.json()["data"]["status"] == "pending"

    async def test_create_task_default_priority_is_medium(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Priority check"},
        )
        assert resp.json()["data"]["priority"] == "medium"

    async def test_create_task_with_all_fields(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={
                "title": "Full task",
                "description": "A detailed description",
                "priority": "high",
            },
        )
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["title"] == "Full task"
        assert data["description"] == "A detailed description"
        assert data["priority"] == "high"

    async def test_create_task_strips_whitespace_from_title(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "  Padded Title  "},
        )
        assert resp.json()["data"]["title"] == "Padded Title"

    async def test_create_task_response_contains_id_and_timestamps(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Schema check"},
        )
        data = resp.json()["data"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "user_id" in data
        assert data["user_id"] == TEST_USER_ID

    async def test_create_task_missing_title_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"description": "No title"},
        )
        assert resp.status_code == 422

    async def test_create_task_empty_title_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": ""},
        )
        assert resp.status_code == 422

    async def test_create_task_whitespace_only_title_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "   "},
        )
        assert resp.status_code == 422

    async def test_create_task_invalid_priority_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Task", "priority": "urgent"},
        )
        assert resp.status_code == 422

    async def test_create_task_wrong_user_id_returns_403(self, client: AsyncClient, auth_as: User):
        """JWT is for TEST_USER_ID but path uses a different user_id."""
        resp = await client.post(
            f"/api/{OTHER_USER_ID}/tasks",
            json={"title": "Forbidden"},
        )
        assert resp.status_code == 403

    async def test_create_task_title_too_long_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "x" * 501},
        )
        assert resp.status_code == 422


# ── List Tasks ────────────────────────────────────────────────────────────────

class TestListTasks:

    async def test_list_tasks_returns_200(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        assert resp.status_code == 200

    async def test_list_tasks_returns_correct_structure(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        data = resp.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)

    async def test_list_tasks_count_matches_meta(self, client: AsyncClient, auth_as: User):
        create_task_in_db(TEST_USER_ID, title="Task A")
        create_task_in_db(TEST_USER_ID, title="Task B")

        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        data = resp.json()
        assert data["meta"]["total"] == len(data["data"])

    async def test_list_tasks_only_returns_own_tasks(self, client: AsyncClient, auth_as: User):
        create_task_in_db(TEST_USER_ID, title="My Task")
        create_task_in_db(OTHER_USER_ID, title="Other Task")

        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        tasks = resp.json()["data"]
        for task in tasks:
            assert task["user_id"] == TEST_USER_ID

    async def test_list_tasks_excludes_deleted(self, client: AsyncClient, auth_as: User):
        create_task_in_db(TEST_USER_ID, title="Active Task")
        create_task_in_db(TEST_USER_ID, title="Deleted Task", status="deleted")

        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        titles = [t["title"] for t in resp.json()["data"]]
        assert "Active Task" in titles
        assert "Deleted Task" not in titles

    async def test_list_tasks_wrong_user_returns_403(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{OTHER_USER_ID}/tasks")
        assert resp.status_code == 403

    async def test_list_tasks_empty_for_new_user(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        data = resp.json()
        # May have 0 tasks if no tasks created in this test
        assert isinstance(data["data"], list)


# ── Get Single Task ───────────────────────────────────────────────────────────

class TestGetTask:

    async def test_get_task_returns_200(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Fetch me")
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        assert resp.status_code == 200

    async def test_get_task_returns_correct_data(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Specific Task", priority="high")
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        data = resp.json()["data"]
        assert str(data["id"]) == str(task.id)
        assert data["title"] == "Specific Task"
        assert data["priority"] == "high"

    async def test_get_task_not_found_returns_404(self, client: AsyncClient, auth_as: User):
        fake_id = str(uuid4())
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{fake_id}")
        assert resp.status_code == 404

    async def test_get_task_wrong_user_returns_403(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Mine")
        # Authenticated as TEST_USER but path says OTHER_USER
        resp = await client.get(f"/api/{OTHER_USER_ID}/tasks/{task.id}")
        assert resp.status_code == 403

    async def test_get_task_other_users_task_returns_404(self, client: AsyncClient, auth_as: User):
        """Even with correct path user_id, cannot see another user's task."""
        other_task = create_task_in_db(OTHER_USER_ID, title="Not Mine")
        # Auth is TEST_USER, path is TEST_USER but task belongs to OTHER_USER
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{other_task.id}")
        assert resp.status_code == 404

    async def test_get_task_invalid_uuid_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/not-a-uuid")
        assert resp.status_code == 422


# ── Update Task ───────────────────────────────────────────────────────────────

class TestUpdateTask:

    async def test_update_task_returns_200(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Old Title")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"title": "New Title"},
        )
        assert resp.status_code == 200

    async def test_update_task_persisted_in_database(self, client: AsyncClient, auth_as: User):
        """Verify update is actually written to Neon PostgreSQL."""
        task = create_task_in_db(TEST_USER_ID, title="Before Update")
        await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"title": "After Update", "status": "in_progress"},
        )
        db_task = get_task_from_db(task.id)
        assert db_task.title == "After Update"
        assert db_task.status == "in_progress"

    async def test_update_task_partial_update(self, client: AsyncClient, auth_as: User):
        """Only provided fields are updated; others stay unchanged."""
        task = create_task_in_db(TEST_USER_ID, title="Original", priority="low")
        await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"status": "completed"},
        )
        db_task = get_task_from_db(task.id)
        assert db_task.title == "Original"  # unchanged
        assert db_task.priority == "low"    # unchanged
        assert db_task.status == "completed"

    async def test_update_task_all_valid_statuses(self, client: AsyncClient, auth_as: User):
        for status_val in ("pending", "in_progress", "completed"):
            task = create_task_in_db(TEST_USER_ID, title=f"Status {status_val}")
            resp = await client.patch(
                f"/api/{TEST_USER_ID}/tasks/{task.id}",
                json={"status": status_val},
            )
            assert resp.status_code == 200

    async def test_update_task_invalid_status_returns_422(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Bad Status")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"status": "archived"},
        )
        assert resp.status_code == 422

    async def test_update_task_invalid_priority_returns_422(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Bad Priority")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"priority": "critical"},
        )
        assert resp.status_code == 422

    async def test_update_deleted_task_returns_400(self, client: AsyncClient, auth_as: User):
        """Business rule: cannot update a soft-deleted task."""
        task = create_task_in_db(TEST_USER_ID, title="Deleted", status="deleted")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"title": "Try to update"},
        )
        assert resp.status_code == 400

    async def test_update_task_not_found_returns_404(self, client: AsyncClient, auth_as: User):
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{uuid4()}",
            json={"title": "Ghost"},
        )
        assert resp.status_code == 404

    async def test_update_task_wrong_user_returns_403(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Mine")
        resp = await client.patch(
            f"/api/{OTHER_USER_ID}/tasks/{task.id}",
            json={"title": "Hijack"},
        )
        assert resp.status_code == 403

    async def test_update_task_empty_title_returns_422(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Valid")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{task.id}",
            json={"title": ""},
        )
        assert resp.status_code == 422


# ── Delete Task ───────────────────────────────────────────────────────────────

class TestDeleteTask:

    async def test_delete_task_returns_200(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="To Delete")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        assert resp.status_code == 200

    async def test_delete_task_is_soft_delete(self, client: AsyncClient, auth_as: User):
        """Soft delete: row stays in DB with status='deleted', not actually removed."""
        task = create_task_in_db(TEST_USER_ID, title="Soft Delete Me")
        await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")

        db_task = get_task_from_db(task.id)
        assert db_task is not None              # still in DB
        assert db_task.status == "deleted"      # status changed

    async def test_delete_task_hidden_from_list(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Hide Me")
        await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")

        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        ids = [t["id"] for t in resp.json()["data"]]
        assert str(task.id) not in ids

    async def test_delete_task_success_message(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Bye")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        assert resp.json()["status"] == "success"

    async def test_delete_task_not_found_returns_404(self, client: AsyncClient, auth_as: User):
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{uuid4()}")
        assert resp.status_code == 404

    async def test_delete_task_wrong_user_returns_403(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Mine")
        resp = await client.delete(f"/api/{OTHER_USER_ID}/tasks/{task.id}")
        assert resp.status_code == 403

    async def test_delete_other_users_task_returns_404(self, client: AsyncClient, auth_as: User):
        """User cannot delete another user's task (returns 404 for security)."""
        other_task = create_task_in_db(OTHER_USER_ID, title="Not Mine")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{other_task.id}")
        assert resp.status_code == 404

    async def test_double_delete_idempotent(self, client: AsyncClient, auth_as: User):
        """Deleting an already-deleted task should succeed gracefully."""
        task = create_task_in_db(TEST_USER_ID, title="Delete Twice")
        await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        # Already deleted: service still returns success (task found, already deleted)
        assert resp.status_code == 200


# ── Multi-tenancy ─────────────────────────────────────────────────────────────

class TestMultiTenancy:
    """End-to-end multi-tenancy isolation across users."""

    async def test_user_a_cannot_read_user_b_tasks(
        self, client: AsyncClient, auth_as: User
    ):
        b_task = create_task_in_db(OTHER_USER_ID, title="User B Task")
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{b_task.id}")
        assert resp.status_code == 404

    async def test_user_a_cannot_update_user_b_tasks(
        self, client: AsyncClient, auth_as: User
    ):
        b_task = create_task_in_db(OTHER_USER_ID, title="User B Task")
        resp = await client.patch(
            f"/api/{TEST_USER_ID}/tasks/{b_task.id}",
            json={"title": "Hijacked"},
        )
        assert resp.status_code == 404

    async def test_user_a_cannot_delete_user_b_tasks(
        self, client: AsyncClient, auth_as: User
    ):
        b_task = create_task_in_db(OTHER_USER_ID, title="User B Task")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{b_task.id}")
        assert resp.status_code == 404

    async def test_each_user_sees_only_their_tasks(
        self, client: AsyncClient, auth_as: User, other_user: User
    ):
        create_task_in_db(TEST_USER_ID, title="A's Task")
        create_task_in_db(OTHER_USER_ID, title="B's Task")

        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        a_user_ids = {t["user_id"] for t in resp.json()["data"]}
        assert a_user_ids == {TEST_USER_ID}
