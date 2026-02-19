
















"""
Auth routes — proxy to Better Auth for signup/signin, return JWT.

Flow:
  1. Client calls POST /auth/sign-up or POST /auth/sign-in on FastAPI
  2. FastAPI proxies the request to Better Auth (Next.js server)
  3. Better Auth authenticates and returns a session cookie
  4. FastAPI calls /api/auth/token on Better Auth to exchange session → JWT
  5. JWT is returned to the caller for use in all protected API calls

Requires the Better Auth JWT plugin to be enabled on the frontend:
    import { jwt } from "better-auth/plugins"
    export const auth = betterAuth({ plugins: [jwt()], ... })

Skill: better-auth-python
@spec: specs/002-todo-backend-api/spec.md (FR-001, FR-007)
"""
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.auth import get_current_user, User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


# ── Request / Response Schemas ───────────────────────────────────────────────

class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class SignInRequest(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    rememberMe: bool = Field(True, description="Keep session alive after browser close")


class UserData(BaseModel):
    id: str
    email: str
    name: Optional[str] = None


class AuthResponse(BaseModel):
    status: str = "success"
    token: str = Field(..., description="JWT — use as: Authorization: Bearer <token>")
    user: UserData


class MeResponse(BaseModel):
    status: str = "success"
    data: UserData


# ── Helpers ──────────────────────────────────────────────────────────────────

async def _call_better_auth(
    client: httpx.AsyncClient,
    path: str,
    body: dict,
) -> tuple[dict, httpx.Cookies]:
    """
    POST to Better Auth and return (response_json, cookies).
    Raises HTTPException on auth failure or server error.
    """
    url = f"{settings.BETTER_AUTH_URL}/api/auth{path}"
    try:
        resp = await client.post(url, json=body, timeout=10.0)
    except httpx.ConnectError:
        logger.error(f"Cannot reach Better Auth at {settings.BETTER_AUTH_URL}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth server unreachable. Is it running at {settings.BETTER_AUTH_URL}?",
        )

    data = resp.json()

    if resp.status_code not in (200, 201):
        msg = data.get("message") or data.get("error") or "Authentication failed"
        logger.warning(f"Better Auth {path} returned {resp.status_code}: {msg}")
        raise HTTPException(
            status_code=resp.status_code if resp.status_code in (400, 401, 409, 422) else status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    return data, resp.cookies


async def _get_jwt(client: httpx.AsyncClient, cookies: httpx.Cookies) -> str:
    """
    Exchange a Better Auth session cookie for a JWT token.
    Requires the JWT plugin to be enabled in Better Auth.
    """
    url = f"{settings.BETTER_AUTH_URL}/api/auth/token"
    try:
        resp = await client.get(url, cookies=cookies, timeout=10.0)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth server unreachable while fetching JWT.",
        )

    if resp.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Better Auth JWT plugin is not enabled. "
                'Add `import { jwt } from "better-auth/plugins"` and `plugins: [jwt()]` '
                "to your Better Auth config."
            ),
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve JWT from auth server.",
        )

    token = resp.json().get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth server returned an empty JWT token.",
        )

    return token


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post(
    "/sign-up",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def sign_up(body: SignUpRequest):
    """
    Create a new account via Better Auth and return a JWT token.

    The JWT can then be used as: `Authorization: Bearer <token>` for all
    protected `/api/{user_id}/tasks` endpoints.
    """
    async with httpx.AsyncClient() as client:
        data, cookies = await _call_better_auth(
            client,
            "/sign-up/email",
            {"name": body.name, "email": body.email, "password": body.password},
        )
        token = await _get_jwt(client, cookies)

    user_raw = data.get("user", {})
    logger.info(f"New user registered: {user_raw.get('email')}")

    return AuthResponse(
        token=token,
        user=UserData(
            id=user_raw.get("id", ""),
            email=user_raw.get("email", body.email),
            name=user_raw.get("name", body.name),
        ),
    )


@router.post(
    "/sign-in",
    response_model=AuthResponse,
    summary="Sign in to an existing account",
)
async def sign_in(body: SignInRequest):
    """
    Sign in via Better Auth and return a JWT token.

    The JWT can then be used as: `Authorization: Bearer <token>` for all
    protected `/api/{user_id}/tasks` endpoints.
    """
    async with httpx.AsyncClient() as client:
        data, cookies = await _call_better_auth(
            client,
            "/sign-in/email",
            {"email": body.email, "password": body.password, "rememberMe": body.rememberMe},
        )
        token = await _get_jwt(client, cookies)

    user_raw = data.get("user", {})
    logger.info(f"User signed in: {user_raw.get('email')}")

    return AuthResponse(
        token=token,
        user=UserData(
            id=user_raw.get("id", ""),
            email=user_raw.get("email", body.email),
            name=user_raw.get("name"),
        ),
    )


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    """
    Returns the currently authenticated user extracted from the JWT token.

    Requires: `Authorization: Bearer <token>` header.
    """
    return MeResponse(
        data=UserData(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
        )
    )
