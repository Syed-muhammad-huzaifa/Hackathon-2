"""
Auth route tests.

Tests /auth/sign-up, /auth/sign-in, /auth/me.

Better Auth (the external Next.js server) is mocked with pytest-mock
so tests run without needing the frontend to be running.
The JWT verification dependency is overridden so /auth/me tests
do not require a live JWKS server.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, Response, Cookies

from app.core.auth import get_current_user, User


# ── Helpers ───────────────────────────────────────────────────────────────────

VALID_SIGNUP = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "securepassword123",
}

VALID_SIGNIN = {
    "email": "jane@example.com",
    "password": "securepassword123",
}

MOCK_USER_RESPONSE = {
    "id": "better-auth-user-001",
    "name": "Jane Doe",
    "email": "jane@example.com",
    "emailVerified": False,
    "createdAt": "2026-02-16T00:00:00Z",
}

MOCK_SESSION_RESPONSE = {
    "id": "session-001",
    "userId": "better-auth-user-001",
    "token": "session-token-abc",
}

MOCK_JWT_TOKEN = "eyJhbGciOiJSUzI1NiJ9.mock.signature"


def _make_better_auth_mock(signup_status=200, signin_status=200, token_status=200):
    """Build a mock httpx.AsyncClient that simulates Better Auth responses."""
    mock_client = AsyncMock()

    # sign-up response
    signup_resp = MagicMock(spec=Response)
    signup_resp.status_code = signup_status
    signup_resp.json.return_value = {
        "user": MOCK_USER_RESPONSE,
        "session": MOCK_SESSION_RESPONSE,
    }
    signup_resp.cookies = Cookies()

    # sign-in response
    signin_resp = MagicMock(spec=Response)
    signin_resp.status_code = signin_status
    signin_resp.json.return_value = {
        "user": MOCK_USER_RESPONSE,
        "session": MOCK_SESSION_RESPONSE,
    }
    signin_resp.cookies = Cookies()

    # token response
    token_resp = MagicMock(spec=Response)
    token_resp.status_code = token_status
    token_resp.json.return_value = {"token": MOCK_JWT_TOKEN}

    mock_client.post = AsyncMock(side_effect=[signup_resp, signin_resp])
    mock_client.get = AsyncMock(return_value=token_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    return mock_client


# ── Sign-Up Tests ─────────────────────────────────────────────────────────────

class TestSignUp:

    async def test_signup_success_returns_201(self, client: AsyncClient):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        post_resp = MagicMock(status_code=200, cookies=Cookies())
        post_resp.json.return_value = {"user": MOCK_USER_RESPONSE, "session": MOCK_SESSION_RESPONSE}
        get_resp = MagicMock(status_code=200)
        get_resp.json.return_value = {"token": MOCK_JWT_TOKEN}

        mock_client.post = AsyncMock(return_value=post_resp)
        mock_client.get = AsyncMock(return_value=get_resp)

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-up", json=VALID_SIGNUP)
        assert resp.status_code == 201

    async def test_signup_returns_token_and_user(self, client: AsyncClient):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        post_resp = MagicMock(status_code=200, cookies=Cookies())
        post_resp.json.return_value = {"user": MOCK_USER_RESPONSE, "session": MOCK_SESSION_RESPONSE}

        get_resp = MagicMock(status_code=200)
        get_resp.json.return_value = {"token": MOCK_JWT_TOKEN}

        mock_client.post = AsyncMock(return_value=post_resp)
        mock_client.get = AsyncMock(return_value=get_resp)

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-up", json=VALID_SIGNUP)

        data = resp.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == MOCK_USER_RESPONSE["email"]
        assert data["status"] == "success"

    async def test_signup_missing_name_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 422

    async def test_signup_missing_email_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={
            "name": "Test",
            "password": "password123",
        })
        assert resp.status_code == 422

    async def test_signup_missing_password_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={
            "name": "Test",
            "email": "test@example.com",
        })
        assert resp.status_code == 422

    async def test_signup_password_too_short_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={
            "name": "Test",
            "email": "test@example.com",
            "password": "short",  # < 8 chars
        })
        assert resp.status_code == 422

    async def test_signup_invalid_email_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={
            "name": "Test",
            "email": "not-an-email",
            "password": "password123",
        })
        assert resp.status_code == 422

    async def test_signup_empty_body_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-up", json={})
        assert resp.status_code == 422

    async def test_signup_better_auth_conflict_returns_400(self, client: AsyncClient):
        """Duplicate email — Better Auth returns 400/409."""
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        conflict_resp = MagicMock(status_code=409, cookies=Cookies())
        conflict_resp.json.return_value = {"message": "User already exists"}
        mock_client.post = AsyncMock(return_value=conflict_resp)

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-up", json=VALID_SIGNUP)

        assert resp.status_code in (400, 409)

    async def test_signup_better_auth_unreachable_returns_503(self, client: AsyncClient):
        import httpx as real_httpx
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=real_httpx.ConnectError("refused"))

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-up", json=VALID_SIGNUP)

        assert resp.status_code == 503


# ── Sign-In Tests ─────────────────────────────────────────────────────────────

class TestSignIn:

    def _mock_signin_success(self):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        post_resp = MagicMock(status_code=200, cookies=Cookies())
        post_resp.json.return_value = {"user": MOCK_USER_RESPONSE, "session": MOCK_SESSION_RESPONSE}

        get_resp = MagicMock(status_code=200)
        get_resp.json.return_value = {"token": MOCK_JWT_TOKEN}

        mock_client.post = AsyncMock(return_value=post_resp)
        mock_client.get = AsyncMock(return_value=get_resp)
        return mock_client

    async def test_signin_success_returns_200(self, client: AsyncClient):
        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=self._mock_signin_success()):
            resp = await client.post("/auth/sign-in", json=VALID_SIGNIN)
        assert resp.status_code == 200

    async def test_signin_returns_token(self, client: AsyncClient):
        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=self._mock_signin_success()):
            resp = await client.post("/auth/sign-in", json=VALID_SIGNIN)
        data = resp.json()
        assert "token" in data
        assert len(data["token"]) > 0

    async def test_signin_returns_user(self, client: AsyncClient):
        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=self._mock_signin_success()):
            resp = await client.post("/auth/sign-in", json=VALID_SIGNIN)
        data = resp.json()
        assert data["user"]["email"] == "jane@example.com"
        assert data["user"]["id"] == "better-auth-user-001"

    async def test_signin_wrong_credentials_returns_401(self, client: AsyncClient):
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        fail_resp = MagicMock(status_code=401, cookies=Cookies())
        fail_resp.json.return_value = {"message": "Invalid email or password"}
        mock_client.post = AsyncMock(return_value=fail_resp)

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-in", json={
                "email": "jane@example.com",
                "password": "wrongpassword",
            })
        assert resp.status_code == 401

    async def test_signin_missing_email_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-in", json={"password": "password123"})
        assert resp.status_code == 422

    async def test_signin_missing_password_returns_422(self, client: AsyncClient):
        resp = await client.post("/auth/sign-in", json={"email": "jane@example.com"})
        assert resp.status_code == 422

    async def test_signin_jwt_plugin_missing_returns_501(self, client: AsyncClient):
        """If Better Auth JWT plugin not enabled, /api/auth/token returns 404."""
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        post_resp = MagicMock(status_code=200, cookies=Cookies())
        post_resp.json.return_value = {"user": MOCK_USER_RESPONSE, "session": MOCK_SESSION_RESPONSE}
        mock_client.post = AsyncMock(return_value=post_resp)

        not_found_resp = MagicMock(status_code=404)
        not_found_resp.json.return_value = {"message": "Not found"}
        mock_client.get = AsyncMock(return_value=not_found_resp)

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-in", json=VALID_SIGNIN)

        assert resp.status_code == 501
        assert "JWT plugin" in resp.json()["detail"]

    async def test_signin_better_auth_unreachable_returns_503(self, client: AsyncClient):
        import httpx as real_httpx
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=real_httpx.ConnectError("refused"))

        with patch("app.api.v1.auth.httpx.AsyncClient", return_value=mock_client):
            resp = await client.post("/auth/sign-in", json=VALID_SIGNIN)
        assert resp.status_code == 503


# ── /auth/me Tests ────────────────────────────────────────────────────────────

class TestMe:

    async def test_me_returns_user(self, client: AsyncClient, auth_as: User):
        resp = await client.get("/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == auth_as.id
        assert data["data"]["email"] == auth_as.email

    async def test_me_without_auth_returns_422(self, client: AsyncClient):
        """No Authorization header → FastAPI returns 422 (missing required header).
        Note: dependency_overrides must be empty for this to test real auth."""
        from app.main import app as _app
        _app.dependency_overrides.clear()
        resp = await client.get("/auth/me")
        assert resp.status_code == 422

    async def test_me_with_invalid_token_returns_401(self, client: AsyncClient):
        """Bad token → JWT verify raises 401."""
        resp = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code in (401, 503)  # 401 bad token, 503 if JWKS unreachable
