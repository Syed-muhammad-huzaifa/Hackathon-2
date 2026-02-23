"""
Async database engine and session factory using SQLModel + asyncpg.
Tables are created on FastAPI startup (no Alembic migrations).
@spec: specs/001-chatbot-backend/spec.md (FR-005, FR-006)
"""
import logging
import re
from urllib.parse import urlparse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings

logger = logging.getLogger(__name__)


def _to_asyncpg_url(url: str) -> tuple[str, bool]:
    """
    Convert a standard PostgreSQL URL to asyncpg-compatible format.
    Returns (cleaned_url, needs_ssl).
    - Replaces postgresql:// or postgres:// scheme with postgresql+asyncpg://
    - Strips sslmode param (asyncpg uses ssl=True via connect_args instead)
    - Strips channel_binding param (psycopg3-only, not supported by asyncpg)
    """
    needs_ssl = "sslmode=require" in url or "sslmode=verify" in url or "neon.tech" in url

    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            url = "postgresql+asyncpg://" + url[len(prefix):]
            break

    # Strip params asyncpg doesn't understand
    for param in (r"sslmode=[^&]*", r"channel_binding=[^&]*"):
        url = re.sub(rf"[?&]{param}", "", url)

    # Clean up any dangling ?& or trailing ? after stripping
    url = re.sub(r"\?&", "?", url)
    url = re.sub(r"[?&]$", "", url)
    return url, needs_ssl


_db_url, _needs_ssl = _to_asyncpg_url(settings.DATABASE_URL)


def get_db_connection_info() -> dict[str, str | bool]:
    """
    Return non-sensitive DB connection info for diagnostics.
    """
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip("/") if parsed.path else ""
    return {
        "host": parsed.hostname or "",
        "database": db_name,
        "ssl_enabled": _needs_ssl,
    }

engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={"ssl": True} if _needs_ssl else {},
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """FastAPI dependency — yields an async database session."""
    async with async_session_factory() as session:
        yield session


async def create_tables():
    """Create all SQLModel tables on startup."""
    info = get_db_connection_info()
    logger.info(
        "DB target host=%s database=%s ssl=%s",
        info["host"],
        info["database"],
        info["ssl_enabled"],
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await _ensure_schema(conn)
    logger.info("✓ Database tables created/verified")


async def _ensure_schema(conn) -> None:
    """
    Ensure critical columns/indexes exist in legacy schemas.
    SQLModel's create_all() doesn't alter existing tables.
    """
    # Conversations: chatkit_thread_id for ChatKit recovery
    await _ensure_column(conn, "conversations", "chatkit_thread_id", "VARCHAR(255)")
    await _ensure_index(conn, "ix_conversations_chatkit_thread_id", "conversations", "chatkit_thread_id")

    # Messages: tool_calls JSON (stored as text)
    await _ensure_column(conn, "messages", "tool_calls", "TEXT")


async def _ensure_column(conn, table: str, column: str, column_type: str) -> None:
    exists = await conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=:t AND column_name=:c"
        ),
        {"t": table, "c": column},
    )
    if exists.first() is None:
        logger.warning("Schema update: adding %s.%s", table, column)
        await conn.execute(
            text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {column_type}')
        )


async def _ensure_index(conn, index_name: str, table: str, column: str) -> None:
    exists = await conn.execute(
        text(
            "SELECT 1 FROM pg_indexes "
            "WHERE schemaname='public' AND indexname=:i"
        ),
        {"i": index_name},
    )
    if exists.first() is None:
        logger.warning("Schema update: creating index %s", index_name)
        await conn.execute(
            text(f'CREATE INDEX "{index_name}" ON "{table}" ("{column}")')
        )
