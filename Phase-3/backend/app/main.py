"""
FastAPI application entry point.
- CORS middleware
- SQLModel table creation on startup
- FastMCP server mounted at /mcp (HTTP transport for external clients)
- MCPServerStdio subprocess started for the agent
- ChatKit adapter mounted at /api/chatkit
@spec: specs/001-chatbot-backend/spec.md (FR-016, FR-018)
"""
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from agents.mcp import MCPServerStdio

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.tasks import router as tasks_router
from app.mcp.mcp_server import mcp
from app.services.chat_service import set_mcp_server
from app.services.chatkit_adapter import chatkit_adapter_app

# Ensure all SQLModel models are registered before create_all is called
import app.models.task          # noqa: F401, E402
import app.models.conversation  # noqa: F401, E402
import app.models.message       # noqa: F401, E402

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastMCP HTTP app (mounted at /mcp for external MCP clients) ─
_mcp_http = mcp.http_app(path="/")

# ── Backend directory (for subprocess cwd) ─────────────────────
_BACKEND_DIR = str(Path(__file__).parent.parent)


# ── Lifespan ───────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Phase-3 Chatbot Backend...")

    await create_tables()
    logger.info("✓ Database tables ready")

    # Spawn MCP server subprocess — agent communicates via stdio
    # Pass current environment explicitly so subprocess has DATABASE_URL etc.
    mcp_subprocess = MCPServerStdio(
        name="Task MCP",
        params={
            "command": sys.executable,
            "args": ["-m", "app.mcp.mcp_server"],
            "cwd": _BACKEND_DIR,
            "env": dict(os.environ),
        },
        cache_tools_list=True,
        client_session_timeout_seconds=settings.MCP_CLIENT_TIMEOUT_SECONDS,
    )
    async with mcp_subprocess:
        set_mcp_server(mcp_subprocess)
        logger.info("✓ MCP server subprocess ready")
        logger.info("✓ Application ready")
        yield

    logger.info("Shutdown complete")


# ── App ────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Chatbot Backend",
    description="Natural language task management via OpenAI Agents SDK and FastMCP.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def normalize_chatkit_mount_path(request: Request, call_next):
    """Avoid slash-redirect churn for ChatKit clients that call /api/chatkit."""
    if request.scope.get("path") == "/api/chatkit":
        request.scope["path"] = "/api/chatkit/"
    return await call_next(request)


# ── CORS (FR-016) ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount FastMCP HTTP server at /mcp ──────────────────────────
app.mount("/mcp", _mcp_http)

# ── Mount ChatKit adapter at /api/chatkit ──────────────────────
app.mount("/api/chatkit", chatkit_adapter_app)

# ── Global error handlers (FR-018) ────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"status": "error", "code": "NOT_FOUND", "message": "Endpoint not found"},
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    return JSONResponse(
        status_code=405,
        content={"status": "error", "code": "METHOD_NOT_ALLOWED", "message": "Method not allowed"},
    )


# ── Routers ────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(tasks_router)


@app.get("/")
async def root():
    return {
        "name": "AI Chatbot Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/live",
        "mcp": "/mcp",
    }
