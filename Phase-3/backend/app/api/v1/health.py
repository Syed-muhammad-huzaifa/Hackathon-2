"""
Health check endpoints for liveness and readiness probes.
@spec: specs/001-chatbot-backend/contracts/chat-api.yaml
"""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import async_session_factory, get_db_connection_info

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def liveness():
    """Liveness probe — server is running."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe — database connected."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail={"status": "not_ready", "database": "disconnected"})


@router.get("/health/db/info")
async def db_info(user_id: str | None = None):
    """
    DB diagnostics endpoint to verify backend connection target and row counts.
    """
    try:
        connection = get_db_connection_info()
        async with async_session_factory() as session:
            counts = {}
            for table in ("tasks", "conversations", "messages"):
                result = await session.execute(text(f"SELECT COUNT(*) AS c FROM {table}"))
                counts[table] = int(result.scalar_one())

            user_counts = None
            if user_id:
                user_counts = {}
                for table in ("tasks", "conversations", "messages"):
                    result = await session.execute(
                        text(f"SELECT COUNT(*) AS c FROM {table} WHERE user_id = :user_id"),
                        {"user_id": user_id},
                    )
                    user_counts[table] = int(result.scalar_one())

        return {
            "status": "ok",
            "connection": connection,
            "counts": counts,
            "user_id": user_id,
            "user_counts": user_counts,
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"DB diagnostics failed: {str(e)}")
