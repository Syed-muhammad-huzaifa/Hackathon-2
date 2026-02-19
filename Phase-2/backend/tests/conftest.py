"""
Shared test fixtures.

Uses the real Neon PostgreSQL database to verify actual DB writes.
Each test run uses a unique user_id so tests are isolated and don't
collide with production data. Cleanup runs after every test.
"""
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, select

from app.main import app
from app.core.auth import get_current_user, User
from app.core.database import engine
from app.models.task import Task

# ── Stable test user (unique per test run) ───────────────────────────────────
TEST_USER_ID = f"test-user-{uuid.uuid4().hex[:8]}"
OTHER_USER_ID = f"test-user-{uuid.uuid4().hex[:8]}"


# ── User fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_user() -> User:
    return User(id=TEST_USER_ID, email="testuser@example.com", name="Test User")


@pytest.fixture(scope="session")
def other_user() -> User:
    return User(id=OTHER_USER_ID, email="other@example.com", name="Other User")


# ── Dependency overrides ──────────────────────────────────────────────────────

@pytest.fixture
def auth_as(test_user: User):
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield test_user
    app.dependency_overrides.clear()


@pytest.fixture
def auth_as_other(other_user: User):
    app.dependency_overrides[get_current_user] = lambda: other_user
    yield other_user
    app.dependency_overrides.clear()


# ── HTTP client ───────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c


# ── Database helpers ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Delete all tasks created by test users after every test."""
    yield
    with Session(engine) as session:
        for uid in (TEST_USER_ID, OTHER_USER_ID):
            result = session.exec(select(Task).where(Task.user_id == uid))
            for task in result.all():
                session.delete(task)
        session.commit()


def create_task_in_db(
    user_id: str,
    title: str = "Test Task",
    description: str | None = None,
    priority: str = "medium",
    status: str = "pending",
) -> Task:
    """Directly insert a task into the DB and return it."""
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            status=status,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


def get_task_from_db(task_id) -> Task | None:
    """Fetch a task directly from the DB."""
    with Session(engine) as session:
        result = session.exec(select(Task).where(Task.id == task_id))
        return result.first()
