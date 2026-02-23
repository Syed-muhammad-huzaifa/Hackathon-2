"""
Shared fixtures for all tests.
- Real Groq API (llama-3.3-70b-versatile)
- Real Neon PostgreSQL database
- FastAPI lifespan triggered (starts FastMCP subprocess)
- JWT dependency overridden (no real token needed)
"""
import os
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

# Disable OpenAI tracing noise (Groq key != OpenAI key)
os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")

from app.main import app
from app.core.auth import User, get_current_user

# ── Stable test user ──────────────────────────────────────────
TEST_USER_ID = "test-chatbot-user-phase3"
TEST_USER = User(id=TEST_USER_ID, email="testphase3@example.com", name="Phase3 Tester")
AUTH_HEADERS = {"Authorization": "Bearer fake-test-token"}


async def mock_get_current_user() -> User:
    return TEST_USER


# Override JWT globally
app.dependency_overrides[get_current_user] = mock_get_current_user


@pytest_asyncio.fixture(scope="session")
async def client():
    """
    Session-scoped async client.
    LifespanManager triggers FastAPI lifespan → starts FastMCP MCP subprocess.
    """
    async with LifespanManager(app, startup_timeout=60, shutdown_timeout=30) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
        ) as c:
            yield c


@pytest.fixture
def auth_headers():
    return AUTH_HEADERS


@pytest.fixture
def test_user_id():
    return TEST_USER_ID
