"""
Tests: Health endpoints
Real DB connection is verified in readiness probe.
"""


class TestLiveness:
    async def test_live_returns_ok(self, client):
        resp = await client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_live_no_auth_required(self, client):
        resp = await client.get("/health/live")
        assert resp.status_code == 200


class TestReadiness:
    async def test_ready_db_connected(self, client):
        """Hits real Neon DB to verify connection."""
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"


class TestRoot:
    async def test_root_returns_app_info(self, client):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "AI Chatbot Backend"
        assert "/docs" in data["docs"]
