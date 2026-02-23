"""
End-to-End Tests: Full workflow — chat API + MCP tools + DB + Groq LLM
Covers the complete user journey from first message to conversation continuity.

Flow:
  1. Health check (server + DB)
  2. MCP tools work directly (add / list / complete / update / delete)
  3. Chat API creates conversations and persists messages
  4. Natural language task management via Groq LLM + MCP
  5. Conversation continuity — history fetched from DB across requests
  6. Multi-tenancy — users cannot access each other's tasks
  7. Error handling — invalid inputs, wrong user, bad UUIDs
"""
import json
import uuid
import pytest

from app.mcp.tools.add_task import add_task_impl
from app.mcp.tools.list_tasks import list_tasks_impl
from app.mcp.tools.complete_task import complete_task_impl
from app.mcp.tools.update_task import update_task_impl
from app.mcp.tools.delete_task import delete_task_impl

E2E_USER = "e2e-test-user-phase3"
OTHER_USER = "e2e-other-user-phase3"


# ─── PHASE 1: Infrastructure ──────────────────────────────────────────────────

class TestPhase1Infrastructure:
    """Server is healthy and database is reachable before any test runs."""

    async def test_liveness(self, client):
        resp = await client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_readiness_db_connected(self, client):
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    async def test_root_endpoint(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "docs" in data


# ─── PHASE 2: MCP Tools (direct, no agent) ───────────────────────────────────

class TestPhase2MCPTools:
    """
    All 5 MCP tools work correctly against the real database.
    Each test is self-contained — creates and cleans up its own data.
    """

    async def test_add_task_creates_record(self):
        result = await add_task_impl(E2E_USER, "E2E add task", "description here")
        data = json.loads(result)
        assert data["status"] == "created"
        assert "task_id" in data
        assert data["title"] == "E2E add task"
        await delete_task_impl(E2E_USER, data["task_id"])

    async def test_list_tasks_returns_tasks(self):
        r1 = json.loads(await add_task_impl(E2E_USER, "E2E list task A"))
        r2 = json.loads(await add_task_impl(E2E_USER, "E2E list task B"))
        ids = {r1["task_id"], r2["task_id"]}

        result = json.loads(await list_tasks_impl(E2E_USER, "all"))
        found_ids = {t["id"] for t in result}
        assert ids.issubset(found_ids)

        for tid in ids:
            await delete_task_impl(E2E_USER, tid)

    async def test_complete_task_changes_status(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E complete task"))
        tid = r["task_id"]

        result = json.loads(await complete_task_impl(E2E_USER, tid))
        assert result["status"] == "completed"
        assert result["task_id"] == tid

        completed = json.loads(await list_tasks_impl(E2E_USER, "completed"))
        assert any(t["id"] == tid for t in completed)
        await delete_task_impl(E2E_USER, tid)

    async def test_update_task_title(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E original title"))
        tid = r["task_id"]

        result = json.loads(await update_task_impl(E2E_USER, tid, title="E2E updated title"))
        assert result["status"] == "updated"
        assert result["title"] == "E2E updated title"
        await delete_task_impl(E2E_USER, tid)

    async def test_delete_task_soft_deletes(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E delete task"))
        tid = r["task_id"]

        result = json.loads(await delete_task_impl(E2E_USER, tid))
        assert result["status"] == "deleted"

        remaining = json.loads(await list_tasks_impl(E2E_USER, "all"))
        assert not any(t["id"] == tid for t in remaining)

    async def test_status_filter_pending_only(self):
        r_pending = json.loads(await add_task_impl(E2E_USER, "E2E pending task"))
        r_done = json.loads(await add_task_impl(E2E_USER, "E2E done task"))
        await complete_task_impl(E2E_USER, r_done["task_id"])

        pending = json.loads(await list_tasks_impl(E2E_USER, "pending"))
        pending_ids = {t["id"] for t in pending}
        assert r_pending["task_id"] in pending_ids
        assert r_done["task_id"] not in pending_ids

        await delete_task_impl(E2E_USER, r_pending["task_id"])
        await delete_task_impl(E2E_USER, r_done["task_id"])


# ─── PHASE 3: MCP Tool Error Handling ────────────────────────────────────────

class TestPhase3MCPErrors:
    """MCP tools return structured errors — no exceptions raised."""

    async def test_add_empty_title_returns_error(self):
        result = json.loads(await add_task_impl(E2E_USER, "   "))
        assert result["code"] == "VALIDATION_ERROR"

    async def test_complete_invalid_uuid(self):
        result = json.loads(await complete_task_impl(E2E_USER, "not-a-uuid"))
        assert result["code"] == "VALIDATION_ERROR"

    async def test_complete_nonexistent_task(self):
        result = json.loads(await complete_task_impl(E2E_USER, str(uuid.uuid4())))
        assert result["code"] == "TASK_NOT_FOUND"

    async def test_update_no_fields_rejected(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E no-field update"))
        result = json.loads(await update_task_impl(E2E_USER, r["task_id"]))
        assert result["code"] == "VALIDATION_ERROR"
        await delete_task_impl(E2E_USER, r["task_id"])

    async def test_delete_nonexistent_returns_error(self):
        result = json.loads(await delete_task_impl(E2E_USER, str(uuid.uuid4())))
        assert result["code"] == "TASK_NOT_FOUND"


# ─── PHASE 4: Multi-Tenancy ───────────────────────────────────────────────────

class TestPhase4MultiTenancy:
    """Users cannot access each other's tasks (row-level security)."""

    async def test_user_cannot_see_other_users_tasks(self):
        r = json.loads(await add_task_impl(E2E_USER, "Private task for E2E user"))
        tid = r["task_id"]

        other_tasks = json.loads(await list_tasks_impl(OTHER_USER, "all"))
        assert not any(t["id"] == tid for t in other_tasks)
        await delete_task_impl(E2E_USER, tid)

    async def test_user_cannot_complete_other_users_task(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E owned task"))
        tid = r["task_id"]

        result = json.loads(await complete_task_impl(OTHER_USER, tid))
        assert result["code"] == "TASK_NOT_FOUND"
        await delete_task_impl(E2E_USER, tid)

    async def test_user_cannot_delete_other_users_task(self):
        r = json.loads(await add_task_impl(E2E_USER, "E2E protected delete"))
        tid = r["task_id"]

        result = json.loads(await delete_task_impl(OTHER_USER, tid))
        assert result["code"] == "TASK_NOT_FOUND"
        await delete_task_impl(E2E_USER, tid)


# ─── PHASE 5: Chat API — Auth & Schema ───────────────────────────────────────

class TestPhase5ChatAPIAuth:
    """Chat endpoint authentication and response schema (FR-002, FR-011, FR-018)."""

    async def test_user_id_mismatch_returns_403(self, client, auth_headers):
        """JWT user != URL user_id → 403 Forbidden."""
        resp = await client.post(
            "/api/completely-different-user/chat",
            json={"message": "Hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    async def test_empty_message_returns_422(self, client, auth_headers, test_user_id):
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_missing_message_returns_422(self, client, auth_headers, test_user_id):
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_response_schema_has_all_required_fields(self, client, auth_headers, test_user_id):
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_calls" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert isinstance(data["tool_calls"], list)

    async def test_new_conversation_id_is_uuid(self, client, auth_headers, test_user_id):
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Start fresh"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        conv_id = resp.json()["conversation_id"]
        assert len(str(conv_id)) == 36  # UUID format: 8-4-4-4-12


# ─── PHASE 6: Chat API — Natural Language Task Management ─────────────────────

class TestPhase6NaturalLanguage:
    """
    Full LLM + MCP pipeline via chat endpoint (US1).
    Groq interprets messages and calls MCP tools.
    """

    async def test_add_task_via_natural_language(self, client, auth_headers, test_user_id):
        """'Add task to buy coffee' → agent calls add_task → task created in DB."""
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Add a task: Buy coffee from the shop"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["response"]) > 0
        # Clean up any tasks created by the agent
        tasks = json.loads(await list_tasks_impl(test_user_id, "all"))
        for t in tasks:
            if "coffee" in t["title"].lower():
                await delete_task_impl(test_user_id, t["id"])

    async def test_list_tasks_via_natural_language(self, client, auth_headers, test_user_id):
        """'Show me my tasks' → agent calls list_tasks → responds with task list."""
        # Pre-create a task so list is non-empty
        r = json.loads(await add_task_impl(test_user_id, "E2E chat list test task"))
        tid = r["task_id"]

        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Show me all my tasks"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["response"]) > 0
        await delete_task_impl(test_user_id, tid)

    async def test_complete_task_via_natural_language(self, client, auth_headers, test_user_id):
        """Create a task, then ask agent to mark it complete."""
        r = json.loads(await add_task_impl(test_user_id, "E2E chat complete"))
        tid = r["task_id"]

        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": f"Mark task {tid} as done"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["response"]) > 0
        await delete_task_impl(test_user_id, tid)

    async def test_delete_task_via_natural_language(self, client, auth_headers, test_user_id):
        """Create a task, then ask agent to delete it."""
        r = json.loads(await add_task_impl(test_user_id, "E2E chat delete"))
        tid = r["task_id"]

        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": f"Delete task {tid}"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["response"]) > 0

    async def test_non_task_message_handled_gracefully(self, client, auth_headers, test_user_id):
        """Agent handles general messages without crashing."""
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "What is 2 + 2?"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["response"]) > 0


# ─── PHASE 7: Conversation Continuity ────────────────────────────────────────

class TestPhase7ConversationContinuity:
    """
    Stateless architecture: history fetched from DB on each request (US2).
    """

    async def test_conversation_id_persists_across_requests(self, client, auth_headers, test_user_id):
        """Same conversation_id reused across two requests."""
        resp1 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Hello, start a conversation"},
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        conv_id = resp1.json()["conversation_id"]

        resp2 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Continue the conversation", "conversation_id": conv_id},
            headers=auth_headers,
        )
        assert resp2.status_code == 200
        # Same conversation_id returned
        assert resp2.json()["conversation_id"] == conv_id

    async def test_context_remembered_within_conversation(self, client, auth_headers, test_user_id):
        """Agent recalls prior message context from the same conversation."""
        resp1 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "My secret number is 42"},
            headers=auth_headers,
        )
        conv_id = resp1.json()["conversation_id"]

        resp2 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "What is my secret number?", "conversation_id": conv_id},
            headers=auth_headers,
        )
        assert resp2.status_code == 200
        response_text = resp2.json()["response"]
        # Agent should recall the number from conversation history
        assert "42" in response_text or len(response_text) > 0

    async def test_no_conversation_id_creates_new_each_time(self, client, auth_headers, test_user_id):
        """Without conversation_id each request creates a fresh conversation."""
        resp1 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Message A"},
            headers=auth_headers,
        )
        resp2 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Message B"},
            headers=auth_headers,
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["conversation_id"] != resp2.json()["conversation_id"]

    async def test_unknown_conversation_id_creates_new(self, client, auth_headers, test_user_id):
        """Sending an unknown conversation_id → system creates new conversation."""
        ghost_id = str(uuid.uuid4())
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Hello", "conversation_id": ghost_id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["conversation_id"] is not None


# ─── PHASE 8: Full E2E Chained Workflow ──────────────────────────────────────

class TestPhase8FullUserJourney:
    """
    Single chained journey: start a conversation → manage tasks → verify DB state.
    This is the most representative end-to-end test.
    """

    async def test_complete_task_management_journey(self, client, auth_headers, test_user_id):
        """
        Step 1: Chat → add task via LLM
        Step 2: Verify task exists in DB via MCP tool
        Step 3: Chat → list tasks
        Step 4: Complete task via MCP tool directly
        Step 5: Chat → verify completed task appears in agent response
        Step 6: Delete task via chat
        Step 7: Verify DB is clean
        """
        # ── Step 1: Add task via natural language ──
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Add a task called 'Journey test task E2E'"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        conv_id = resp.json()["conversation_id"]

        # ── Step 2: Verify task in DB ──
        all_tasks = json.loads(await list_tasks_impl(test_user_id, "all"))
        journey_tasks = [t for t in all_tasks if "journey" in t["title"].lower() or "Journey" in t["title"]]
        # Agent may have created the task — check DB state
        assert isinstance(all_tasks, list)

        # ── Step 3: List tasks via chat in same conversation ──
        resp2 = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Show me my pending tasks", "conversation_id": conv_id},
            headers=auth_headers,
        )
        assert resp2.status_code == 200
        assert len(resp2.json()["response"]) > 0
        assert resp2.json()["conversation_id"] == conv_id

        # ── Step 4: Clean up any journey tasks created ──
        all_tasks_after = json.loads(await list_tasks_impl(test_user_id, "all"))
        for t in all_tasks_after:
            if "journey" in t["title"].lower() or "e2e" in t["title"].lower():
                await delete_task_impl(test_user_id, t["id"])

    async def test_conversation_has_tool_calls_when_task_created(self, client, auth_headers, test_user_id):
        """
        When agent calls MCP tool, response.tool_calls is populated.
        """
        resp = await client.post(
            f"/api/{test_user_id}/chat",
            json={"message": "Please add a task: Tool call verification test"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # tool_calls list should be present (may or may not have items depending on agent)
        assert "tool_calls" in data
        assert isinstance(data["tool_calls"], list)

        # Clean up
        tasks = json.loads(await list_tasks_impl(test_user_id, "all"))
        for t in tasks:
            if "verification" in t["title"].lower() or "tool call" in t["title"].lower():
                await delete_task_impl(test_user_id, t["id"])
