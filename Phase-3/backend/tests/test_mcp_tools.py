"""
Tests: MCP tools — real database operations
Each tool is called directly (no HTTP, no agent).
"""
import json
import pytest
import uuid

from app.mcp.tools.add_task import add_task_impl as add_task
from app.mcp.tools.list_tasks import list_tasks_impl as list_tasks
from app.mcp.tools.complete_task import complete_task_impl as complete_task
from app.mcp.tools.delete_task import delete_task_impl as delete_task
from app.mcp.tools.update_task import update_task_impl as update_task

USER_ID = "test-chatbot-user-phase3"


class TestAddTask:
    async def test_add_task_success(self):
        result = await add_task(USER_ID, "Test task from pytest", "Created by automated test")
        data = json.loads(result)
        assert "task_id" in data
        assert data["status"] == "created"
        assert data["title"] == "Test task from pytest"
        # Cleanup
        await delete_task(USER_ID, data["task_id"])

    async def test_add_task_empty_title_returns_error(self):
        result = await add_task(USER_ID, "   ")
        data = json.loads(result)
        assert data["code"] == "VALIDATION_ERROR"
        assert "error" in data

    async def test_add_task_no_description(self):
        result = await add_task(USER_ID, "Task without description")
        data = json.loads(result)
        assert data["status"] == "created"
        await delete_task(USER_ID, data["task_id"])


class TestListTasks:
    async def test_list_tasks_returns_array(self):
        result = await list_tasks(USER_ID, "all")
        data = json.loads(result)
        assert isinstance(data, list)

    async def test_list_tasks_status_filter_pending(self):
        # Add a task first
        add_result = json.loads(await add_task(USER_ID, "Pending task for list test"))
        task_id = add_result["task_id"]

        result = await list_tasks(USER_ID, "pending")
        tasks = json.loads(result)
        assert isinstance(tasks, list)
        # Our task should appear
        ids = [t["id"] for t in tasks]
        assert task_id in ids

        await delete_task(USER_ID, task_id)

    async def test_list_tasks_status_filter_completed(self):
        # Add + complete a task
        add_result = json.loads(await add_task(USER_ID, "Task to complete for list test"))
        task_id = add_result["task_id"]
        await complete_task(USER_ID, task_id)

        result = await list_tasks(USER_ID, "completed")
        tasks = json.loads(result)
        ids = [t["id"] for t in tasks]
        assert task_id in ids

        await delete_task(USER_ID, task_id)

    async def test_list_tasks_invalid_status_defaults_to_all(self):
        result = await list_tasks(USER_ID, "invalid_status")
        data = json.loads(result)
        assert isinstance(data, list)

    async def test_list_tasks_task_fields(self):
        add_result = json.loads(await add_task(USER_ID, "Field check task"))
        task_id = add_result["task_id"]

        result = await list_tasks(USER_ID, "all")
        tasks = json.loads(result)
        task = next((t for t in tasks if t["id"] == task_id), None)
        assert task is not None
        assert "title" in task
        assert "status" in task
        assert "id" in task

        await delete_task(USER_ID, task_id)


class TestCompleteTask:
    async def test_complete_task_success(self):
        add_result = json.loads(await add_task(USER_ID, "Task to complete"))
        task_id = add_result["task_id"]

        result = await complete_task(USER_ID, task_id)
        data = json.loads(result)
        assert data["status"] == "completed"
        assert data["task_id"] == task_id
        assert "title" in data

        await delete_task(USER_ID, task_id)

    async def test_complete_nonexistent_task(self):
        fake_id = str(uuid.uuid4())
        result = await complete_task(USER_ID, fake_id)
        data = json.loads(result)
        assert data["code"] == "TASK_NOT_FOUND"

    async def test_complete_invalid_uuid(self):
        result = await complete_task(USER_ID, "not-a-uuid")
        data = json.loads(result)
        assert data["code"] == "VALIDATION_ERROR"

    async def test_cannot_complete_another_users_task(self):
        """Multi-tenancy: other user's tasks are invisible."""
        add_result = json.loads(await add_task(USER_ID, "My private task"))
        task_id = add_result["task_id"]

        result = await complete_task("other-user-999", task_id)
        data = json.loads(result)
        assert data["code"] == "TASK_NOT_FOUND"

        await delete_task(USER_ID, task_id)


class TestDeleteTask:
    async def test_delete_task_success(self):
        add_result = json.loads(await add_task(USER_ID, "Task to delete"))
        task_id = add_result["task_id"]

        result = await delete_task(USER_ID, task_id)
        data = json.loads(result)
        assert data["status"] == "deleted"
        assert data["task_id"] == task_id

    async def test_deleted_task_not_in_list(self):
        add_result = json.loads(await add_task(USER_ID, "Task that will disappear"))
        task_id = add_result["task_id"]
        await delete_task(USER_ID, task_id)

        tasks = json.loads(await list_tasks(USER_ID, "all"))
        ids = [t["id"] for t in tasks]
        assert task_id not in ids

    async def test_delete_nonexistent_task(self):
        result = await delete_task(USER_ID, str(uuid.uuid4()))
        data = json.loads(result)
        assert data["code"] == "TASK_NOT_FOUND"

    async def test_delete_invalid_uuid(self):
        result = await delete_task(USER_ID, "bad-id")
        data = json.loads(result)
        assert data["code"] == "VALIDATION_ERROR"


class TestUpdateTask:
    async def test_update_title(self):
        add_result = json.loads(await add_task(USER_ID, "Original title"))
        task_id = add_result["task_id"]

        result = await update_task(USER_ID, task_id, title="Updated title")
        data = json.loads(result)
        assert data["status"] == "updated"
        assert data["title"] == "Updated title"

        await delete_task(USER_ID, task_id)

    async def test_update_description(self):
        add_result = json.loads(await add_task(USER_ID, "Task with desc"))
        task_id = add_result["task_id"]

        result = await update_task(USER_ID, task_id, description="New description")
        data = json.loads(result)
        assert data["status"] == "updated"

        await delete_task(USER_ID, task_id)

    async def test_update_requires_at_least_one_field(self):
        add_result = json.loads(await add_task(USER_ID, "Update nothing task"))
        task_id = add_result["task_id"]

        result = await update_task(USER_ID, task_id)
        data = json.loads(result)
        assert data["code"] == "VALIDATION_ERROR"

        await delete_task(USER_ID, task_id)

    async def test_update_nonexistent_task(self):
        result = await update_task(USER_ID, str(uuid.uuid4()), title="New title")
        data = json.loads(result)
        assert data["code"] == "TASK_NOT_FOUND"

    async def test_update_empty_title_rejected(self):
        add_result = json.loads(await add_task(USER_ID, "Task with empty update"))
        task_id = add_result["task_id"]

        result = await update_task(USER_ID, task_id, title="   ")
        data = json.loads(result)
        assert data["code"] == "VALIDATION_ERROR"

        await delete_task(USER_ID, task_id)
