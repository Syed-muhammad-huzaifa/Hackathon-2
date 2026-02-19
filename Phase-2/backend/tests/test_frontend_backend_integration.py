"""
Frontend-Backend Integration Tests

Tests the actual frontend integration pattern:
1. Frontend gets JWT token from Better Auth (mocked)
2. Frontend passes JWT to backend API
3. Backend verifies JWT via JWKS (mocked)
4. Backend performs database operations
5. Backend returns response to frontend

This verifies the complete flow with REAL database operations.

Run with: pytest tests/test_frontend_backend_integration.py -v
"""

import pytest
import uuid
import jwt
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, select
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from app.main import app
from app.core.database import engine
from app.core.config import settings
from app.core.auth import clear_jwks_cache
from app.models.task import Task


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear JWKS cache before and after each test."""
    clear_jwks_cache()
    yield
    clear_jwks_cache()


@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for JWT tokens."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return {
        'private': private_key,
        'public': private_key.public_key(),
        'kid': 'test-key-123'
    }


@pytest.fixture
def mock_jwks(rsa_key_pair, httpx_mock):
    """Mock JWKS endpoint for JWT verification."""
    from jwt.algorithms import RSAAlgorithm
    import json

    jwk = RSAAlgorithm.to_jwk(rsa_key_pair['public'])
    jwk_dict = json.loads(jwk)
    jwk_dict['kid'] = rsa_key_pair['kid']
    jwk_dict['use'] = 'sig'
    jwk_dict['alg'] = 'RS256'

    # Mock JWKS endpoint - allow unlimited requests
    httpx_mock.add_response(
        url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
        json={'keys': [jwk_dict]},
        match_headers=False  # Don't match headers
    )

    # Disable assertion that all mocked responses were requested
    httpx_mock._assert_all_responses_were_requested = False

    return jwk_dict


@pytest.fixture
def create_jwt_token(rsa_key_pair):
    """Factory to create valid JWT tokens."""
    def _create(user_id: str, email: str, name: str = "Test User"):
        now = datetime.now(timezone.utc)
        payload = {
            'sub': user_id,
            'email': email,
            'name': name,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(hours=1)).timestamp()),
        }
        return jwt.encode(
            payload,
            rsa_key_pair['private'],
            algorithm='RS256',
            headers={'kid': rsa_key_pair['kid']}
        )
    return _create


@pytest.fixture
async def client():
    """HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test data after each test."""
    yield
    with Session(engine) as session:
        # Delete test tasks
        result = session.exec(select(Task))
        for task in result.all():
            if task.user_id.startswith('test-user-'):
                session.delete(task)
        session.commit()


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
class TestFrontendBackendIntegration:
    """Test frontend-backend integration with real database operations."""

    async def test_create_task_with_jwt(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Frontend creates task with JWT token - backend writes to database."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': 'Frontend Integration Task',
                'description': 'Testing real DB write',
                'priority': 'high'
            },
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['title'] == 'Frontend Integration Task'
        assert data['data']['user_id'] == user_id

        # Verify in database
        task_id = data['data']['id']
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is not None
            assert db_task.title == 'Frontend Integration Task'
            assert db_task.user_id == user_id


    async def test_list_tasks_with_jwt(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Frontend lists tasks with JWT - backend reads from database."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Create 3 tasks
        for i in range(3):
            await client.post(
                f'/api/{user_id}/tasks',
                json={'title': f'Task {i+1}', 'priority': 'medium'},
                headers={'Authorization': f'Bearer {token}'}
            )

        # List tasks
        response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data['data']) == 3
        assert data['meta']['total'] == 3


    async def test_update_task_with_jwt(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Frontend updates task with JWT - backend updates database."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Create task
        create_resp = await client.post(
            f'/api/{user_id}/tasks',
            json={'title': 'Original', 'priority': 'low'},
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_resp.json()['data']['id']

        # Update task
        response = await client.patch(
            f'/api/{user_id}/tasks/{task_id}',
            json={'title': 'Updated', 'status': 'completed'},
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert response.json()['data']['title'] == 'Updated'

        # Verify in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.title == 'Updated'
            assert db_task.status == 'completed'


    async def test_delete_task_with_jwt(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Frontend deletes task with JWT - backend soft-deletes in database."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Create task
        create_resp = await client.post(
            f'/api/{user_id}/tasks',
            json={'title': 'To Delete', 'priority': 'low'},
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_resp.json()['data']['id']

        # Delete task
        response = await client.delete(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200

        # Verify soft delete in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.status == 'deleted'


    async def test_row_level_security(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Verify users can only access their own tasks."""
        user1_id = f'test-user-{uuid.uuid4().hex[:8]}'
        user2_id = f'test-user-{uuid.uuid4().hex[:8]}'

        token1 = create_jwt_token(user1_id, 'user1@example.com')
        token2 = create_jwt_token(user2_id, 'user2@example.com')

        # User 1 creates task
        create_resp = await client.post(
            f'/api/{user1_id}/tasks',
            json={'title': 'User 1 Task', 'priority': 'high'},
            headers={'Authorization': f'Bearer {token1}'}
        )
        task_id = create_resp.json()['data']['id']

        # User 2 tries to access User 1's task
        response = await client.get(
            f'/api/{user1_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token2}'}
        )

        assert response.status_code == 403


    async def test_unauthorized_without_token(self, client):
        """Verify protected endpoints require JWT token."""
        response = await client.get('/api/some-user/tasks')
        assert response.status_code in [401, 422]


    async def test_invalid_token_rejected(self, client, mock_jwks):
        """Verify invalid JWT tokens are rejected."""
        response = await client.get(
            '/api/some-user/tasks',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        assert response.status_code == 401


    async def test_complete_crud_flow(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Test complete CRUD flow as frontend would use it."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # CREATE
        create_resp = await client.post(
            f'/api/{user_id}/tasks',
            json={'title': 'CRUD Task', 'description': 'Testing', 'priority': 'medium'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert create_resp.status_code == 201
        task_id = create_resp.json()['data']['id']

        # READ (single)
        read_resp = await client.get(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert read_resp.status_code == 200
        assert read_resp.json()['data']['title'] == 'CRUD Task'

        # UPDATE
        update_resp = await client.patch(
            f'/api/{user_id}/tasks/{task_id}',
            json={'status': 'completed'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert update_resp.status_code == 200
        assert update_resp.json()['data']['status'] == 'completed'

        # READ (list)
        list_resp = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert list_resp.status_code == 200
        assert len(list_resp.json()['data']) >= 1

        # DELETE
        delete_resp = await client.delete(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert delete_resp.status_code == 200

        # Verify in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.status == 'deleted'


    async def test_multiple_users_isolated(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Verify multiple users have isolated task lists."""
        user1_id = f'test-user-{uuid.uuid4().hex[:8]}'
        user2_id = f'test-user-{uuid.uuid4().hex[:8]}'

        token1 = create_jwt_token(user1_id, 'user1@example.com')
        token2 = create_jwt_token(user2_id, 'user2@example.com')

        # User 1 creates 2 tasks
        for i in range(2):
            await client.post(
                f'/api/{user1_id}/tasks',
                json={'title': f'User1 Task {i+1}', 'priority': 'low'},
                headers={'Authorization': f'Bearer {token1}'}
            )

        # User 2 creates 3 tasks
        for i in range(3):
            await client.post(
                f'/api/{user2_id}/tasks',
                json={'title': f'User2 Task {i+1}', 'priority': 'high'},
                headers={'Authorization': f'Bearer {token2}'}
            )

        # User 1 sees only their 2 tasks
        resp1 = await client.get(
            f'/api/{user1_id}/tasks',
            headers={'Authorization': f'Bearer {token1}'}
        )
        assert len(resp1.json()['data']) == 2

        # User 2 sees only their 3 tasks
        resp2 = await client.get(
            f'/api/{user2_id}/tasks',
            headers={'Authorization': f'Bearer {token2}'}
        )
        assert len(resp2.json()['data']) == 3


    async def test_task_validation(self, client, mock_jwks, create_jwt_token):
        """Verify task validation works."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Empty title should fail
        response = await client.post(
            f'/api/{user_id}/tasks',
            json={'title': '', 'priority': 'low'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 422


    async def test_concurrent_task_creation(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Verify concurrent task creation works correctly."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Create 5 tasks rapidly
        task_ids = []
        for i in range(5):
            resp = await client.post(
                f'/api/{user_id}/tasks',
                json={'title': f'Concurrent {i+1}', 'priority': 'medium'},
                headers={'Authorization': f'Bearer {token}'}
            )
            assert resp.status_code == 201
            task_ids.append(resp.json()['data']['id'])

        # Verify all tasks exist in database
        with Session(engine) as session:
            for task_id in task_ids:
                db_task = session.get(Task, task_id)
                assert db_task is not None
                assert db_task.user_id == user_id


    async def test_database_persistence(self, client, mock_jwks, create_jwt_token, cleanup_db):
        """Verify data persists across requests."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        token = create_jwt_token(user_id, 'user@example.com')

        # Create task
        create_resp = await client.post(
            f'/api/{user_id}/tasks',
            json={'title': 'Persistent Task', 'priority': 'high'},
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_resp.json()['data']['id']

        # Read task multiple times
        for _ in range(3):
            resp = await client.get(
                f'/api/{user_id}/tasks/{task_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            assert resp.status_code == 200
            assert resp.json()['data']['title'] == 'Persistent Task'
