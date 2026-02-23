"""
Better Auth JWT verification using JWKS (RS256).
Phase 3 has its own separate Better Auth system (not linked to Phase 2).
@spec: specs/001-chatbot-backend/spec.md (FR-002, FR-008)
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


@dataclass
class User:
    """User data extracted from verified JWT claims."""
    id: str
    email: str
    name: Optional[str] = None


@dataclass
class _JWKSCache:
    keys: dict
    expires_at: float


_cache: Optional[_JWKSCache] = None


async def _get_jwks() -> dict:
    """Fetch JWKS from Better Auth server with TTL caching."""
    global _cache

    now = time.time()
    if _cache and now < _cache.expires_at:
        return _cache.keys

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.BETTER_AUTH_URL.rstrip('/')}/api/auth/jwks",
            timeout=10.0,
        )
        response.raise_for_status()
        jwks = response.json()

    keys = {}
    for key in jwks.get("keys", []):
        keys[key["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(key)

    _cache = _JWKSCache(keys=keys, expires_at=now + JWKS_CACHE_TTL)
    logger.debug(f"JWKS refreshed, {len(keys)} key(s) cached")
    return keys


def clear_jwks_cache():
    global _cache
    _cache = None


async def verify_token(token: str) -> User:
    """Verify JWT using Better Auth JWKS. Returns User on success."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        public_keys = await _get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid or kid not in public_keys:
            clear_jwks_cache()
            public_keys = await _get_jwks()
            if not kid or kid not in public_keys:
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return User(id=user_id, email=payload.get("email", ""), name=payload.get("name"))

    except jwt.ExpiredSignatureError:
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
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth server unavailable. Please try again.",
        )


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> User:
    """FastAPI dependency — extracts and verifies the Bearer JWT token."""
    return await verify_token(authorization)
