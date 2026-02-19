"""
Error handling tests.

Verifies that all error responses follow a consistent JSON structure,
correct HTTP status codes are returned, and no internal details leak.
"""
import pytest
from uuid import uuid4
from httpx import AsyncClient

from tests.conftest import TEST_USER_ID, create_task_in_db
from app.core.auth import User


class TestValidationErrorResponses:

    async def test_validation_error_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": ""},  # empty title fails validator
        )
        assert resp.status_code == 422

    async def test_validation_error_has_detail_field(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"priority": "invalid"},
        )
        assert resp.status_code == 422
        body = resp.json()
        # Our custom handler uses "details" (with errors list) + "code" + "message"
        assert "details" in body
        assert body["code"] == "VALIDATION_ERROR"

    async def test_malformed_json_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            content=b"not-valid-json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    async def test_invalid_uuid_in_path_returns_422(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/not-a-uuid")
        assert resp.status_code == 422

    async def test_extra_fields_ignored(self, client: AsyncClient, auth_as: User):
        """Pydantic ignores unknown fields by default — should not error."""
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Valid", "extra_unknown_field": "value"},
        )
        assert resp.status_code == 201


class TestAuthErrorResponses:

    async def test_missing_auth_header_returns_422(self, client: AsyncClient):
        """No Authorization header at all → FastAPI 422 (required header missing).
        Overrides must be cleared so the real dependency is used."""
        from app.main import app as _app
        _app.dependency_overrides.clear()
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        assert resp.status_code == 422

    async def test_invalid_bearer_token_returns_401_or_503(self, client: AsyncClient):
        """Malformed JWT → 401 (invalid token) or 503 (JWKS unreachable in test env)."""
        resp = await client.get(
            f"/api/{TEST_USER_ID}/tasks",
            headers={"Authorization": "Bearer eyInvalid.Token.Here"},
        )
        assert resp.status_code in (401, 503)

    async def test_wrong_user_in_path_returns_403(self, client: AsyncClient, auth_as: User):
        """JWT is for TEST_USER but path uses a different user_id → 403."""
        from tests.conftest import OTHER_USER_ID
        resp = await client.get(f"/api/{OTHER_USER_ID}/tasks")
        assert resp.status_code == 403

    async def test_403_response_has_detail(self, client: AsyncClient, auth_as: User):
        from tests.conftest import OTHER_USER_ID
        resp = await client.get(f"/api/{OTHER_USER_ID}/tasks")
        body = resp.json()
        assert "detail" in body


class TestNotFoundResponses:

    async def test_task_not_found_returns_404(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{uuid4()}")
        assert resp.status_code == 404

    async def test_404_response_has_detail(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks/{uuid4()}")
        body = resp.json()
        assert "detail" in body

    async def test_unknown_route_returns_404(self, client: AsyncClient):
        resp = await client.get("/api/nonexistent/endpoint")
        assert resp.status_code == 404


class TestResponseStructure:

    async def test_success_create_has_status_field(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Structure Check"},
        )
        assert resp.json()["status"] == "success"

    async def test_success_list_has_data_and_meta(self, client: AsyncClient, auth_as: User):
        resp = await client.get(f"/api/{TEST_USER_ID}/tasks")
        body = resp.json()
        assert "data" in body
        assert "meta" in body
        assert "total" in body["meta"]

    async def test_task_response_has_all_required_fields(self, client: AsyncClient, auth_as: User):
        resp = await client.post(
            f"/api/{TEST_USER_ID}/tasks",
            json={"title": "Fields check"},
        )
        data = resp.json()["data"]
        required = {"id", "user_id", "title", "status", "priority", "created_at", "updated_at"}
        assert required.issubset(data.keys())

    async def test_delete_response_has_status_and_message(self, client: AsyncClient, auth_as: User):
        task = create_task_in_db(TEST_USER_ID, title="Delete structure")
        resp = await client.delete(f"/api/{TEST_USER_ID}/tasks/{task.id}")
        body = resp.json()
        assert body["status"] == "success"
        assert "message" in body

    async def test_no_internal_error_details_leaked_on_500(self, client: AsyncClient, auth_as: User):
        """Generic 500 must not expose stack traces or internal paths."""
        # We can't easily trigger a real 500 without mocking, so test the
        # structure of the existing generic_exception_handler via the registered handler.
        from app.api.exception_handlers import generic_exception_handler
        from fastapi import Request
        from unittest.mock import MagicMock

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"

        response = await generic_exception_handler(request, Exception("internal secret"))
        body = response.body
        import json
        data = json.loads(body)

        # Must not contain the internal error message
        assert "internal secret" not in str(data)
        assert data["status"] == "error"
        assert data["code"] == "INTERNAL_ERROR"
