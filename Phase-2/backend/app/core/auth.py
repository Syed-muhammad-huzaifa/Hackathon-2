"""
Better Auth JWT verification using JWKS (RS256).

Fetches public keys from Better Auth's JWKS endpoint and verifies
RS256-signed JWT tokens issued by the frontend auth server.

Skill: better-auth-python
@spec: specs/002-todo-backend-api/spec.md (FR-001, FR-007)
"""
import time
import logging
from dataclasses import dataclass
from typing import Optional

import httpx
import jwt
from fastapi import HTTPException, Header, status

from app.core.config import settings

logger = logging.getLogger(__name__)

JWKS_CACHE_TTL = 300  # 5 minutes


# === USER MODEL ===
@dataclass
class User:
    """User data extracted from verified JWT claims."""
    id: str
    email: str
    name: Optional[str] = None


# === JWKS CACHE ===
@dataclass
class _JWKSCache:
    keys: dict
    expires_at: float


_cache: Optional[_JWKSCache] = None


async def _get_jwks() -> dict:
    """Fetch JWKS from Better Auth server with TTL caching."""
    global _cache

    now = time.time()

    # Return cached keys if still valid
    if _cache and now < _cache.expires_at:
        return _cache.keys

    # Fetch fresh JWKS from Better Auth
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BETTER_AUTH_URL}/api/auth/jwks",
            timeout=10.0,
        )
        response.raise_for_status()
        jwks = response.json()

    # Build key lookup by kid
    keys = {}
    for key in jwks.get("keys", []):
        keys[key["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(key)

    _cache = _JWKSCache(keys=keys, expires_at=now + JWKS_CACHE_TTL)
    logger.debug(f"JWKS refreshed, {len(keys)} key(s) cached")

    return keys


def clear_jwks_cache():
    """Clear the JWKS cache (useful for key rotation)."""
    global _cache
    _cache = None


# === TOKEN VERIFICATION ===
async def verify_token(token: str) -> User:
    """
    Verify a JWT token using Better Auth's JWKS endpoint.

    Args:
        token: Raw JWT string (with or without 'Bearer ' prefix)

    Returns:
        User: Extracted user data from verified claims

    Raises:
        HTTPException 401: Token invalid, expired, or missing
        HTTPException 503: Better Auth server unreachable
    """
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = await _get_jwks()

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            # Unknown kid — refresh cache once and retry
            clear_jwks_cache()
            public_keys = await _get_jwks()
            if not kid or kid not in public_keys:
                logger.warning(f"JWT kid '{kid}' not found in JWKS")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token key",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        payload = jwt.decode(
            token,
            public_keys[kid],
            algorithms=["RS256"],
            options={"verify_aud": False},
        )

        user_id: str = payload.get("sub")
        if not user_id:
            logger.warning("JWT missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"JWT verified for user {user_id}")
        return User(
            id=user_id,
            email=payload.get("email", ""),
            name=payload.get("name"),
        )

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS from Better Auth: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth server unavailable. Please try again.",
        )


# === FASTAPI DEPENDENCY ===
async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> User:
    """
    FastAPI dependency — extracts and verifies the Bearer JWT token.

    Usage:
        @router.get("/protected")
        async def route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    return await verify_token(authorization)
