"""
Health endpoint tests.

Verifies /health, /health/live, /health/ready — including
real database connectivity to Neon PostgreSQL.
"""
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:

    async def test_health_returns_200(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_health_status_healthy(self, client: AsyncClient):
        resp = await client.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"

    async def test_health_includes_database_check(self, client: AsyncClient):
        resp = await client.get("/health")
        data = resp.json()
        assert "checks" in data
        assert "database" in data["checks"]

    async def test_health_database_connected(self, client: AsyncClient):
        """Verifies real connection to Neon PostgreSQL is alive."""
        resp = await client.get("/health")
        data = resp.json()
        assert data["checks"]["database"]["status"] == "healthy"

    async def test_health_includes_environment(self, client: AsyncClient):
        resp = await client.get("/health")
        data = resp.json()
        assert "environment" in data

    async def test_liveness_returns_200(self, client: AsyncClient):
        resp = await client.get("/health/live")
        assert resp.status_code == 200

    async def test_liveness_returns_alive(self, client: AsyncClient):
        resp = await client.get("/health/live")
        data = resp.json()
        assert data["status"] == "alive"

    async def test_readiness_returns_200(self, client: AsyncClient):
        resp = await client.get("/health/ready")
        assert resp.status_code == 200

    async def test_readiness_returns_ready(self, client: AsyncClient):
        resp = await client.get("/health/ready")
        data = resp.json()
        assert data["status"] == "ready"
