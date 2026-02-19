"""
Backend Authentication Integration Tests

Tests the complete authentication flow between Better Auth (frontend)
and FastAPI backend, including JWT verification, JWKS fetching, and
protected endpoints.

Run with: pytest tests/test_auth_integration.py -v
"""

import pytest
import httpx
from datetime import datetime, timedelta, timezone
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from app.core.auth import verify_token, clear_jwks_cache, User
from app.core.config import settings


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for testing JWT tokens."""
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
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

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
    def _create_jwt(user_id: str, email: str, name: str = None, expired: bool = False):
        now = datetime.now(timezone.utc)
        exp = now - timedelta(hours=1) if expired else now + timedelta(hours=1)

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


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear JWKS cache before each test."""
    clear_jwks_cache()
    yield
    clear_jwks_cache()


# ============================================================================
# Test JWT Token Verification
# ============================================================================

class TestJWTVerification:
    """Test JWT token verification with JWKS."""

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, create_test_jwt, mock_jwks, httpx_mock):
        """Test verification of valid JWT token."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create valid token
        token = create_test_jwt(
            user_id='user-123',
            email='test@example.com',
            name='Test User'
        )

        # Verify token
        user = await verify_token(token)

        assert isinstance(user, User)
        assert user.id == 'user-123'
        assert user.email == 'test@example.com'
        assert user.name == 'Test User'


    @pytest.mark.asyncio
    async def test_verify_expired_token(self, create_test_jwt, mock_jwks, httpx_mock):
        """Test verification of expired JWT token."""
        from fastapi import HTTPException

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create expired token
        token = create_test_jwt(
            user_id='user-123',
            email='test@example.com',
            expired=True
        )

        # Verify token should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(token)

        assert exc_info.value.status_code == 401
        assert 'expired' in exc_info.value.detail.lower()


    @pytest.mark.asyncio
    async def test_verify_invalid_signature(self, mock_jwks, httpx_mock):
        """Test verification of token with invalid signature."""
        from fastapi import HTTPException

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create token with wrong signature
        token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3Qta2V5LWlkLTEyMyJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSJ9.invalid_signature"

        # Verify token should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(token)

        assert exc_info.value.status_code == 401


    @pytest.mark.asyncio
    async def test_verify_token_missing_sub(self, rsa_key_pair, mock_jwks, httpx_mock):
        """Test verification of token without 'sub' claim."""
        from fastapi import HTTPException

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Create token without 'sub'
        payload = {
            'email': 'test@example.com',
            'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }

        token = jwt.encode(
            payload,
            rsa_key_pair['private'],
            algorithm='RS256',
            headers={'kid': rsa_key_pair['kid']}
        )

        # Verify token should raise exception
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(token)

        assert exc_info.value.status_code == 401
        assert 'missing user id' in exc_info.value.detail.lower()


    @pytest.mark.asyncio
    async def test_jwks_caching(self, create_test_jwt, mock_jwks, httpx_mock):
        """Test that JWKS is cached and not fetched on every request."""
        # Mock JWKS endpoint (should only be called once)
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        token = create_test_jwt('user-123', 'test@example.com')

        # First verification - should fetch JWKS
        await verify_token(token)

        # Second verification - should use cached JWKS
        await verify_token(token)

        # Should only have made one request to JWKS endpoint
        assert len(httpx_mock.get_requests()) == 1


# ============================================================================
# Test Auth Endpoints
# ============================================================================

class TestAuthEndpoints:
    """Test authentication endpoints that proxy to Better Auth."""

    @pytest.mark.asyncio
    async def test_sign_up_success(self, client, httpx_mock, create_test_jwt, mock_jwks):
        """Test successful user sign up."""
        # Mock Better Auth sign-up endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-up/email",
            json={
                'user': {
                    'id': 'new-user-123',
                    'email': 'newuser@example.com',
                    'name': 'New User'
                }
            },
            status_code=201
        )

        # Mock Better Auth token endpoint
        token = create_test_jwt('new-user-123', 'newuser@example.com', 'New User')
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/token",
            json={'token': token}
        )

        # Sign up
        response = await client.post(
            '/auth/sign-up',
            json={
                'name': 'New User',
                'email': 'newuser@example.com',
                'password': 'password123'
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'success'
        assert data['token'] == token
        assert data['user']['id'] == 'new-user-123'
        assert data['user']['email'] == 'newuser@example.com'


    @pytest.mark.asyncio
    async def test_sign_up_duplicate_email(self, client, httpx_mock):
        """Test sign up with duplicate email."""
        # Mock Better Auth returning error
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-up/email",
            json={'error': 'Email already exists'},
            status_code=409
        )

        response = await client.post(
            '/auth/sign-up',
            json={
                'name': 'Test User',
                'email': 'existing@example.com',
                'password': 'password123'
            }
        )

        assert response.status_code == 409


    @pytest.mark.asyncio
    async def test_sign_in_success(self, client, httpx_mock, create_test_jwt):
        """Test successful user sign in."""
        # Mock Better Auth sign-in endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-in/email",
            json={
                'user': {
                    'id': 'user-123',
                    'email': 'test@example.com',
                    'name': 'Test User'
                }
            }
        )

        # Mock Better Auth token endpoint
        token = create_test_jwt('user-123', 'test@example.com', 'Test User')
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/token",
            json={'token': token}
        )

        response = await client.post(
            '/auth/sign-in',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['token'] == token


    @pytest.mark.asyncio
    async def test_sign_in_invalid_credentials(self, client, httpx_mock):
        """Test sign in with invalid credentials."""
        # Mock Better Auth returning error
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-in/email",
            json={'error': 'Invalid credentials'},
            status_code=401
        )

        response = await client.post(
            '/auth/sign-in',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )

        assert response.status_code == 401


    @pytest.mark.asyncio
    async def test_get_me_with_valid_token(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test /auth/me endpoint with valid JWT token."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        token = create_test_jwt('user-123', 'test@example.com', 'Test User')

        response = await client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['id'] == 'user-123'
        assert data['data']['email'] == 'test@example.com'


    @pytest.mark.asyncio
    async def test_get_me_without_token(self, client):
        """Test /auth/me endpoint without token."""
        response = await client.get('/auth/me')

        assert response.status_code == 422  # Missing required header


# ============================================================================
# Test Task Endpoints with Authentication
# ============================================================================

class TestTaskEndpointsAuth:
    """Test task endpoints require valid JWT authentication."""

    @pytest.mark.asyncio
    async def test_list_tasks_with_valid_token(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test listing tasks with valid JWT token."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        user_id = 'user-123'
        token = create_test_jwt(user_id, 'test@example.com')

        response = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
        assert 'data' in data


    @pytest.mark.asyncio
    async def test_list_tasks_without_token(self, client):
        """Test listing tasks without JWT token."""
        response = await client.get('/api/user-123/tasks')

        assert response.status_code == 422  # Missing Authorization header


    @pytest.mark.asyncio
    async def test_list_tasks_with_expired_token(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test listing tasks with expired JWT token."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        token = create_test_jwt('user-123', 'test@example.com', expired=True)

        response = await client.get(
            '/api/user-123/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 401


    @pytest.mark.asyncio
    async def test_access_other_user_tasks(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test that users cannot access other users' tasks."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # User A's token
        token = create_test_jwt('user-a', 'usera@example.com')

        # Try to access User B's tasks
        response = await client.get(
            '/api/user-b/tasks',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 403
        assert 'only access your own' in response.json()['detail'].lower()


    @pytest.mark.asyncio
    async def test_create_task_with_auth(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test creating task with valid authentication."""
        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        user_id = 'user-123'
        token = create_test_jwt(user_id, 'test@example.com')

        response = await client.post(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test Task',
                'description': 'Test Description',
                'status': 'pending',
                'priority': 'medium'
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'success'
        assert data['data']['title'] == 'Test Task'


# ============================================================================
# Test CORS Configuration
# ============================================================================

class TestCORS:
    """Test CORS configuration for frontend access."""

    @pytest.mark.asyncio
    async def test_cors_allowed_origin(self, client):
        """Test CORS with allowed origin."""
        response = await client.options(
            '/auth/me',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET'
            }
        )

        assert response.status_code == 200
        assert 'access-control-allow-origin' in response.headers


    @pytest.mark.asyncio
    async def test_cors_credentials(self, client):
        """Test CORS allows credentials."""
        response = await client.get(
            '/health',
            headers={'Origin': 'http://localhost:3000'}
        )

        assert 'access-control-allow-credentials' in response.headers
        assert response.headers['access-control-allow-credentials'] == 'true'


# ============================================================================
# Test Integration Scenarios
# ============================================================================

class TestIntegrationScenarios:
    """Test complete authentication flow scenarios."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client, httpx_mock, create_test_jwt, mock_jwks):
        """Test complete authentication flow: sign up → sign in → access protected resource."""
        user_id = 'integration-user-123'
        email = 'integration@example.com'

        # Step 1: Sign up
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/sign-up/email",
            json={'user': {'id': user_id, 'email': email, 'name': 'Integration User'}}
        )

        token = create_test_jwt(user_id, email, 'Integration User')
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/token",
            json={'token': token}
        )

        signup_response = await client.post(
            '/auth/sign-up',
            json={'name': 'Integration User', 'email': email, 'password': 'password123'}
        )

        assert signup_response.status_code == 201
        jwt_token = signup_response.json()['token']

        # Step 2: Access protected resource with token
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        me_response = await client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {jwt_token}'}
        )

        assert me_response.status_code == 200
        assert me_response.json()['data']['id'] == user_id

        # Step 3: Create a task
        task_response = await client.post(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {jwt_token}'},
            json={
                'title': 'Integration Test Task',
                'description': 'Testing complete flow',
                'status': 'pending',
                'priority': 'high'
            }
        )

        assert task_response.status_code == 201
        assert task_response.json()['data']['title'] == 'Integration Test Task'


    @pytest.mark.asyncio
    async def test_token_refresh_on_expiry(self, client, create_test_jwt, mock_jwks, httpx_mock):
        """Test that expired tokens are rejected and new tokens work."""
        user_id = 'user-123'

        # Mock JWKS endpoint
        httpx_mock.add_response(
            url=f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            json=mock_jwks
        )

        # Try with expired token
        expired_token = create_test_jwt(user_id, 'test@example.com', expired=True)

        response1 = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {expired_token}'}
        )

        assert response1.status_code == 401

        # Try with fresh token
        fresh_token = create_test_jwt(user_id, 'test@example.com')

        response2 = await client.get(
            f'/api/{user_id}/tasks',
            headers={'Authorization': f'Bearer {fresh_token}'}
        )

        assert response2.status_code == 200
