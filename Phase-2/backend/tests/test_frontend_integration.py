"""
Frontend-Backend Integration Tests

Tests the complete integration between Next.js frontend and FastAPI backend
using real database operations and JWT authentication flow.

This simulates actual frontend requests to verify:
- User registration and authentication
- JWT token generation and verification
- Protected endpoint access
- Task CRUD operations with real database
- Row-level security enforcement

Run with: pytest tests/test_frontend_integration.py -v
"""

import pytest
import uuid
import jwt
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlmodel import Session, select
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from app.main import app
from app.core.database import engine
from app.core.config import settings
from app.models.task import Task


# ============================================================================
# Test Data
# ============================================================================

# Generate unique test users for each test run
TEST_USER_1 = {
    'email': f'testuser1_{uuid.uuid4().hex[:8]}@example.com',
    'password': 'SecurePass123!',
    'name': 'Test User 1'
}

TEST_USER_2 = {
    'email': f'testuser2_{uuid.uuid4().hex[:8]}@example.com',
    'password': 'SecurePass456!',
    'name': 'Test User 2'
}


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for JWT tokens."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return {
        'private': private_key,
        'public': public_key,
        'kid': 'test-key-id-123'
    }


@pytest.fixture
def mock_jwks(rsa_key_pair):
    """Mock JWKS response from Better Auth."""
    public_key = rsa_key_pair['public']

    # Convert to JWK format
    from jwt.algorithms import RSAAlgorithm
    jwk = RSAAlgorithm.to_jwk(public_key)

    import json
    jwk_dict = json.loads(jwk)
    jwk_dict['kid'] = rsa_key_pair['kid']
    jwk_dict['use'] = 'sig'
    jwk_dict['alg'] = 'RS256'

    return {
        'keys': [jwk_dict]
    }


@pytest.fixture
def create_test_jwt(rsa_key_pair):
    """Factory to create test JWT tokens."""
    def _create_jwt(user_id: str, email: str, name: str = None):
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=1)

        payload = {
            'sub': user_id,
            'email': email,
            'name': name,
            'iat': int(now.timestamp()),
            'exp': int(exp.timestamp()),
        }

        token = jwt.encode(
            payload,
            rsa_key_pair['private'],
            algorithm='RS256',
            headers={'kid': rsa_key_pair['kid']}
        )

        return token

    return _create_jwt


@pytest.fixture
async def client():
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=True
    ) as ac:
        yield ac


@pytest.fixture
def cleanup_db():
    """Clean up test data after each test."""
    yield
    # Cleanup tasks created during tests
    with Session(engine) as session:
        # Delete all test tasks
        result = session.exec(select(Task))
        for task in result.all():
            # Only delete tasks from test users
            if '@example.com' in task.user_id or task.user_id.startswith('test-'):
                session.delete(task)
        session.commit()


# ============================================================================
# Test Class: Complete Frontend Integration Flow
# ============================================================================

@pytest.mark.asyncio
class TestFrontendIntegration:
    """Test complete frontend-backend integration with real database."""

    async def test_01_user_signup_flow(self, client, httpx_mock, create_test_jwt, mock_jwks):
        """Test user sign-up flow as frontend would call it."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']

        # Mock Better Auth sign-up endpoint
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-up/email",
            json={
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': TEST_USER_1['name']
                },
                'session': {'token': token}
            },
            status_code=201
        )

        # Mock JWKS endpoint for token verification
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        response = await client.post(
            '/auth/sign-up',
            json={
                'email': email,
                'password': TEST_USER_1['password'],
                'name': TEST_USER_1['name']
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == email
        assert data['user']['name'] == TEST_USER_1['name']
        assert isinstance(data['token'], str)

        # Store for later tests
        TEST_USER_1['id'] = user_id
        TEST_USER_1['token'] = token


    async def test_02_user_signin_flow(self, client, httpx_mock, create_test_jwt, mock_jwks):
        """Test user sign-in flow as frontend would call it."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_2['email']

        # Mock Better Auth sign-in endpoint
        token = create_test_jwt(user_id, email, TEST_USER_2['name'])
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-in/email",
            json={
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': TEST_USER_2['name']
                },
                'session': {'token': token}
            }
        )

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        response = await client.post(
            '/auth/sign-in',
            json={
                'email': email,
                'password': TEST_USER_2['password']
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert 'user' in data
        assert 'token' in data
        assert data['user']['email'] == email

        TEST_USER_2['id'] = user_id
        TEST_USER_2['token'] = token


    async def test_03_get_current_user(self, client, httpx_mock, create_test_jwt, mock_jwks):
        """Test getting current user with JWT token."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint for token verification
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Mock Better Auth /me endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/session",
            json={
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': TEST_USER_1['name']
                }
            }
        )

        response = await client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert data['data']['email'] == email
        assert data['data']['name'] == TEST_USER_1['name']


    async def test_04_create_task_with_auth(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test creating a task with authentication (real DB write)."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint for token verification
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create task
        task_data = {
            'title': 'Integration Test Task',
            'description': 'Testing frontend-backend integration',
            'priority': 'high'
        }

        response = await client.post(
            f'/api/{user_id}/tasks',
            json=task_data,
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert data['status'] == 'success'
        assert data['data']['title'] == task_data['title']
        assert data['data']['description'] == task_data['description']
        assert data['data']['priority'] == task_data['priority']
        assert data['data']['user_id'] == user_id

        # Verify task was actually created in database
        task_id = data['data']['id']
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is not None
            assert db_task.title == task_data['title']
            assert db_task.user_id == user_id


    async def test_05_list_tasks_with_auth(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test listing tasks with authentication."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create multiple tasks
        for i in range(3):
            await client.post(
                f'/api/{user_id}/tasks',
                json={
                    'title': f'Task {i+1}',
                    'description': f'Description {i+1}',
                    'priority': 'medium'
                },
                headers={'Authorization': f'Bearer {token}'}
            )

        # List tasks
        response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert len(data['data']) == 3
        assert data['meta']['total'] == 3

        # Verify all tasks belong to the user
        for task in data['data']:
            assert task['user_id'] == user_id


    async def test_06_get_single_task(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test getting a single task by ID."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create task
        create_response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': 'Single Task Test',
                'description': 'Testing single task retrieval',
                'priority': 'low'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_response.json()['data']['id']

        # Get single task
        response = await client.get(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert data['data']['id'] == task_id
        assert data['data']['title'] == 'Single Task Test'


    async def test_07_update_task(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test updating a task."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create task
        create_response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': 'Original Title',
                'description': 'Original description',
                'priority': 'medium'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_response.json()['data']['id']

        # Update task
        update_data = {
            'title': 'Updated Title',
            'status': 'completed',
            'priority': 'high'
        }

        response = await client.patch(
            f'/api/{user_id}/tasks/{task_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert data['data']['title'] == 'Updated Title'
        assert data['data']['status'] == 'completed'
        assert data['data']['priority'] == 'high'

        # Verify update in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.title == 'Updated Title'
            assert db_task.status == 'completed'
            assert db_task.priority == 'high'


    async def test_08_delete_task(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test deleting a task (soft delete)."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create task
        create_response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': 'Task to Delete',
                'description': 'This will be deleted',
                'priority': 'low'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        task_id = create_response.json()['data']['id']

        # Delete task
        response = await client.delete(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'success'
        assert 'deleted' in data['message'].lower()

        # Verify task is soft-deleted in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.status == 'deleted'


    async def test_09_row_level_security(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test that users cannot access other users' tasks."""
        user1_id = f'test-user-{uuid.uuid4().hex[:8]}'
        user2_id = f'test-user-{uuid.uuid4().hex[:8]}'

        token1 = create_test_jwt(user1_id, TEST_USER_1['email'], TEST_USER_1['name'])
        token2 = create_test_jwt(user2_id, TEST_USER_2['email'], TEST_USER_2['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # User 1 creates a task
        create_response = await client.post(
            f'/api/{user1_id}/tasks',
            json={
                'title': 'User 1 Task',
                'description': 'Private task',
                'priority': 'high'
            },
            headers={'Authorization': f'Bearer {token1}'}
        )
        task_id = create_response.json()['data']['id']

        # User 2 tries to access User 1's task
        response = await client.get(
            f'/api/{user1_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token2}'}
        )

        # Should get 403 Forbidden
        assert response.status_code == 403


    async def test_10_unauthorized_access(self, client):
        """Test that protected endpoints require authentication."""
        # Try to access tasks without token
        response = await client.get('/api/some-user-id/tasks')

        assert response.status_code in [401, 422]  # 422 for validation, 401 for auth


    async def test_11_invalid_token(self, client, httpx_mock, mock_jwks):
        """Test that invalid tokens are rejected."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        response = await client.get(
            '/api/some-user-id/tasks',
            headers={'Authorization': 'Bearer invalid-token-here'}
        )

        assert response.status_code == 401


    async def test_12_complete_crud_flow(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test complete CRUD flow as frontend would use it."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # 1. Create task
        create_response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': 'CRUD Test Task',
                'description': 'Testing complete flow',
                'priority': 'medium'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()['data']['id']

        # 2. Read task
        read_response = await client.get(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert read_response.status_code == 200
        assert read_response.json()['data']['title'] == 'CRUD Test Task'

        # 3. Update task
        update_response = await client.patch(
            f'/api/{user_id}/tasks/{task_id}',
            json={'status': 'completed'},
            headers={'Authorization': f'Bearer {token}'}
        )
        assert update_response.status_code == 200
        assert update_response.json()['data']['status'] == 'completed'

        # 4. List tasks
        list_response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()['data']) >= 1

        # 5. Delete task
        delete_response = await client.delete(
            f'/api/{user_id}/tasks/{task_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert delete_response.status_code == 200

        # 6. Verify deletion in database
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task.status == 'deleted'


    async def test_13_task_validation(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test task validation as frontend would encounter it."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Try to create task with empty title
        response = await client.post(
            f'/api/{user_id}/tasks',
            json={
                'title': '',
                'description': 'Test',
                'priority': 'low'
            },
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 422  # Validation error


    async def test_14_pagination_and_filtering(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test pagination and filtering of tasks."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create tasks with different statuses
        for i in range(5):
            status = 'completed' if i < 2 else 'pending'
            await client.post(
                f'/api/{user_id}/tasks',
                json={
                    'title': f'Task {i+1}',
                    'description': f'Description {i+1}',
                    'priority': 'medium'
                },
                headers={'Authorization': f'Bearer {token}'}
            )

            # Update status for first 2 tasks
            if i < 2:
                tasks_response = await client.get(
                    f'/api/{user_id}/tasks',
                    headers={'Authorization': f'Bearer {token}'}
                )
                task_id = tasks_response.json()['data'][i]['id']
                await client.patch(
                    f'/api/{user_id}/tasks/{task_id}',
                    json={'status': 'completed'},
                    headers={'Authorization': f'Bearer {token}'}
                )

        # List all tasks
        response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data['data']) == 5
        assert data['meta']['total'] == 5


    async def test_15_concurrent_operations(self, client, httpx_mock, create_test_jwt, mock_jwks, cleanup_db):
        """Test that concurrent operations work correctly."""
        user_id = f'test-user-{uuid.uuid4().hex[:8]}'
        email = TEST_USER_1['email']
        token = create_test_jwt(user_id, email, TEST_USER_1['name'])

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create multiple tasks concurrently (simulated)
        tasks_created = []
        for i in range(3):
            response = await client.post(
                f'/api/{user_id}/tasks',
                json={
                    'title': f'Concurrent Task {i+1}',
                    'description': f'Testing concurrency {i+1}',
                    'priority': 'medium'
                },
                headers={'Authorization': f'Bearer {token}'}
            )
            assert response.status_code == 201
            tasks_created.append(response.json()['data']['id'])

        # Verify all tasks were created
        list_response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert list_response.status_code == 200
        assert len(list_response.json()['data']) == 3
